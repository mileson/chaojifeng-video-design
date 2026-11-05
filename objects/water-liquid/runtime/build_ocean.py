"""Original deterministic open-ocean builder. Run inside Blender, not system Python.
No external assets or saved scenes. frame=1 corresponds to absolute time zero.
The .blend is an editable snapshot; this script is the authoritative animation source.
"""
import argparse
import hashlib
import json
import math
import sys
import time
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from config import load, frames_for, ConfigError
import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree


def dump(path,value):
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')


def rgb(value):
    return tuple(value)+(1,)


class Ocean:
    def __init__(self,c,out,quality,device):
        self.c=c;self.out=out;self.quality=quality;self.device=device
        bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
        self.scene=s=bpy.context.scene;s.render.engine='CYCLES'
        s.render.resolution_x=c['output']['width'];s.render.resolution_y=c['output']['height']
        s.render.resolution_percentage=100 if quality=='native' else c['render']['preview_percentage']
        s.render.fps=c['output']['fps'];s.render.image_settings.file_format='PNG'
        s.render.threads_mode='FIXED';s.render.threads=c['render']['threads']
        s.cycles.samples=c['render']['native_samples' if quality=='native' else 'preview_samples']
        s.cycles.use_denoising=True;s.cycles.seed=c['seed'];s.cycles.use_animated_seed=False
        s.cycles.max_bounces=c['render']['max_bounces'];s.cycles.transmission_bounces=c['render']['transmission_bounces']
        s.cycles.volume_bounces=0;s.cycles.transparent_max_bounces=4
        s.view_settings.view_transform='AgX';s.view_settings.exposure=0
        self.devices=[]
        if device=='METAL':
            prefs=bpy.context.preferences.addons['cycles'].preferences
            prefs.compute_device_type='METAL';prefs.get_devices()
            for d in prefs.devices:d.use=(d.type=='METAL')
            self.devices=[{'name':d.name,'type':d.type,'enabled':bool(d.use)} for d in prefs.devices]
            if not any(d['enabled'] for d in self.devices):raise RuntimeError('No Metal device; select CPU explicitly')
            s.cycles.device='GPU'
        else:s.cycles.device='CPU';self.devices=[{'name':'CPU','type':'CPU','enabled':True}]
        self.make_mesh();self.make_material();self.make_light()
        bpy.ops.object.camera_add();self.camera=bpy.context.object;self.camera.name='Camera';s.camera=self.camera
        self.camera.data.lens=c['camera']['lens_mm'];self.camera.data.clip_end=c['grid']['extent_m']*3
        self.camera.data.sensor_fit='VERTICAL';self.camera.data.sensor_height=24
        self.camera.data.clip_start=.1
        s.frame_start=1;s.frame_end=round(c['output']['duration_seconds']*c['output']['fps'])

    def make_mesh(self):
        c=self.c;g=c['grid'];n=g['points'];self.n=n
        a=math.asinh(g['extent_m']/g['center_spacing_scale_m']);u=np.linspace(-a,a,n)
        axis=g['center_spacing_scale_m']*np.sinh(u)
        x,y=np.meshgrid(axis,axis);self.xy=np.column_stack((x.ravel(),y.ravel()))
        self.base=np.column_stack((self.xy,np.zeros(n*n))).astype(np.float32)
        spacing=g['center_spacing_scale_m']*np.cosh(u)*(2*a/(n-1))
        self.spacing=np.maximum(*np.meshgrid(spacing,spacing)).ravel()
        self.faces=[(j*n+i,j*n+i+1,(j+1)*n+i+1,(j+1)*n+i) for j in range(n-1) for i in range(n-1)]
        mesh=bpy.data.meshes.new('World grid');mesh.from_pydata(self.base.tolist(),[],self.faces);mesh.update()
        src=bpy.data.objects.new('FFT evaluation surface',mesh);bpy.context.collection.objects.link(src)
        src.hide_render=True;src.display_type='WIRE';self.source=src
        m=src.modifiers.new('Large spectrum','OCEAN');m.geometry_mode='DISPLACE'
        o=c['ocean'];m.resolution=o['resolution'];m.viewport_resolution=o['resolution'];m.spatial_size=o['spatial_size_m']
        m.repeat_x=1;m.repeat_y=1;m.wind_velocity=o['wind_m_s'];m.wave_scale=o['wave_scale']
        m.wave_scale_min=o['smallest_wave_m'];m.choppiness=o['choppiness'];m.wave_alignment=o['alignment']
        m.wave_direction=o['direction_rad'];m.depth=o['depth_m'];m.random_seed=c['seed'];self.modifier=m
        # A single sparse closed volume: top + perimeter skirts + one bottom cap.
        # No full duplicate bottom grid and no repeated Solidify surface.
        edge=list(range(n))+[j*n+n-1 for j in range(1,n)]+list(range(n*n-2,n*(n-1)-1,-1))+[j*n for j in range(n-2,0,-1)]
        self.edge=edge;k=len(self.base)
        bottom=self.base[edge].copy();bottom[:,2]=-g['bottom_depth_m']
        verts=np.concatenate((self.base,bottom));faces=list(self.faces)
        for i,v in enumerate(edge):
            j=(i+1)%len(edge);faces.append((v,k+i,k+j,edge[j]))
        faces.append(tuple(reversed(range(k,k+len(edge)))))
        self.full_coordinates=verts;mesh=bpy.data.meshes.new('Closed ocean');mesh.from_pydata(verts.tolist(),[],faces);mesh.update()
        self.water=bpy.data.objects.new('Water',mesh);bpy.context.collection.objects.link(self.water)
        for poly in mesh.polygons:poly.use_smooth=True
        self.phases=np.random.default_rng(c['seed']).uniform(0,2*math.pi,len(c['medium']['wavelengths_m']))

    def make_material(self):
        c=self.c;mat=bpy.data.materials.new('Water optics');mat.use_nodes=True;n=mat.node_tree.nodes;n.clear();l=mat.node_tree.links
        out=n.new('ShaderNodeOutputMaterial');bs=n.new('ShaderNodeBsdfPrincipled');w=c['water']
        bs.inputs['Base Color'].default_value=rgb(w['surface_color']);bs.inputs['IOR'].default_value=w['ior']
        bs.inputs['Transmission Weight'].default_value=w['transmission'];bs.inputs['Roughness'].default_value=w['roughness']
        l.new(bs.outputs[0],out.inputs['Surface'])
        volume=n.new('ShaderNodeVolumeAbsorption');volume.inputs['Color'].default_value=rgb(w['absorption_color'])
        volume.inputs['Density'].default_value=w['absorption_density'];l.new(volume.outputs[0],out.inputs['Volume'])
        # Geometry Position is stable world-space. Noise W uses absolute film time.
        coord=n.new('ShaderNodeNewGeometry');noise=n.new('ShaderNodeTexNoise');noise.noise_dimensions='4D'
        noise.inputs['Scale'].default_value=c['micro']['scale_per_m'];noise.inputs['Detail'].default_value=2
        l.new(coord.outputs['Position'],noise.inputs['Vector']);self.micro=noise
        bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=c['micro']['strength'];bump.inputs['Distance'].default_value=c['micro']['distance_m']
        l.new(noise.outputs['Fac'],bump.inputs['Height'])
        # A bounded normal-only middle band continues unresolved distant geometry.
        # This is an artistic noise approximation, explicitly not recovered FFT slopes.
        middle=n.new('ShaderNodeTexNoise');middle.noise_dimensions='4D';middle.inputs['Scale'].default_value=.65;middle.inputs['Detail'].default_value=2
        l.new(coord.outputs['Position'],middle.inputs['Vector']);self.middle_normal=middle
        mb=n.new('ShaderNodeBump');mb.inputs['Strength'].default_value=.3;mb.inputs['Distance'].default_value=c['medium']['amplitude_m']*2
        l.new(middle.outputs['Fac'],mb.inputs['Height']);l.new(mb.outputs['Normal'],bump.inputs['Normal']);l.new(bump.outputs['Normal'],bs.inputs['Normal'])
        self.water.data.materials.append(mat)

    def make_light(self):
        c=self.c['lighting'];world=bpy.data.worlds.new('Sky and clouds');self.scene.world=world;world.use_nodes=True
        n=world.node_tree.nodes;n.clear();l=world.node_tree.links
        out=n.new('ShaderNodeOutputWorld');bg=n.new('ShaderNodeBackground');bg.inputs['Strength'].default_value=c['sky_strength']
        sky=n.new('ShaderNodeTexSky');sky.sky_type='MULTIPLE_SCATTERING';sky.sun_disc=False
        sky.sun_elevation=math.radians(c['sun_elevation_deg']);sky.sun_rotation=math.radians(c['sun_azimuth_deg'])
        # Sky carries ambient atmosphere only; one directional light forms sun glints.
        coord=n.new('ShaderNodeTexCoord');scale=n.new('ShaderNodeVectorMath');scale.operation='MULTIPLY';scale.inputs[1].default_value=(2,2,5)
        l.new(coord.outputs['Normal'],scale.inputs[0]);noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=3;noise.inputs['Detail'].default_value=2;l.new(scale.outputs[0],noise.inputs['Vector'])
        ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.6;ramp.color_ramp.elements[0].color=(0,0,0,1);ramp.color_ramp.elements[1].position=.76;ramp.color_ramp.elements[1].color=(c['cloud_coverage'],)*3+(1,)
        l.new(noise.outputs['Fac'],ramp.inputs[0]);mix=n.new('ShaderNodeMixRGB');l.new(ramp.outputs[0],mix.inputs[0]);l.new(sky.outputs[0],mix.inputs[1]);mix.inputs[2].default_value=(c['cloud_brightness'],)*3+(1,)
        l.new(mix.outputs[0],bg.inputs[0]);l.new(bg.outputs[0],out.inputs[0])
        elev=math.radians(c['sun_elevation_deg']);azi=math.radians(c['sun_azimuth_deg'])
        direction=Vector((math.cos(elev)*math.cos(azi),math.cos(elev)*math.sin(azi),math.sin(elev)))
        bpy.ops.object.light_add(type='SUN');sun=bpy.context.object;sun.name='Single sun'
        sun.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler();sun.data.energy=c['sun_energy'];sun.data.angle=math.radians(c['sun_angle_deg'])

    def apply(self,frame,measure=True):
        start=time.monotonic();c=self.c;t=(frame-1)/c['output']['fps'];self.scene.frame_set(frame)
        self.modifier.time=c['ocean']['time_origin_s']+t*c['ocean']['time_speed'];bpy.context.view_layer.update()
        deps=bpy.context.evaluated_depsgraph_get();ev=self.source.evaluated_get(deps);mesh=ev.to_mesh()
        try:
            coords=np.empty(len(mesh.vertices)*3,dtype=np.float32);mesh.vertices.foreach_get('co',coords);coords=coords.reshape(-1,3)
        finally:ev.to_mesh_clear()
        # Nyquist-oriented far-field filtering: unresolved displacement tends continuously to mean level.
        large_filter=np.exp(-(self.spacing/6)**2)
        coords=self.base+(coords-self.base)*large_filter[:,None]
        med=c['medium'];dist=np.linalg.norm(self.xy,axis=1)
        for i,wl in enumerate(med['wavelengths_m']):
            direction=med['direction_rad']+i*.73;k=2*math.pi/wl
            phase=k*(self.xy[:,0]*math.cos(direction)+self.xy[:,1]*math.sin(direction))-math.sqrt(9.81*k)*t+self.phases[i]
            filt=np.exp(-(2*self.spacing/wl)**4)*np.exp(-(dist/med['fade_distance_m'])**2)
            coords[:,2]+=med['amplitude_m']/len(med['wavelengths_m'])*np.sin(phase)*filt
        self.full_coordinates[:len(coords)]=coords
        self.full_coordinates[len(coords):,:2]=coords[self.edge,:2]
        self.water.data.vertices.foreach_set('co',self.full_coordinates.ravel());self.water.data.update()
        self.micro.inputs['W'].default_value=t*c['micro']['time_speed']
        self.middle_normal.inputs['W'].default_value=t*.12
        duration=(self.scene.frame_end-1)/c['output']['fps'];alpha=t/duration if duration else 0
        cam=c['camera'];loc=np.array(cam['start'])*(1-alpha)+np.array(cam['end'])*alpha
        target=np.array(cam['target_start'])*(1-alpha)+np.array(cam['target_end'])*alpha
        self.camera.location=loc;self.camera.rotation_euler=(Vector(target)-Vector(loc)).to_track_quat('-Z','Y').to_euler()
        bpy.context.view_layer.update()
        if not measure:return None
        tree=BVHTree.FromPolygons(coords.tolist(),self.faces,all_triangles=False)
        hit=tree.ray_cast(Vector((loc[0],loc[1],1000)),Vector((0,0,-1)))
        if hit[0] is None:raise RuntimeError('Camera has no water surface below it')
        clearance=float(loc[2]-hit[0].z);height=float(coords[:,2].max()-coords[:,2].min())
        xy=coords[:,:2].reshape(self.n,self.n,2)
        a=xy[:-1,:-1];b=xy[:-1,1:];cc=xy[1:,1:];d=xy[1:,:-1]
        cross=lambda u,v:u[...,0]*v[...,1]-u[...,1]*v[...,0]
        area1=cross(b-a,cc-a);area2=cross(cc-a,d-a)
        folded=int(np.count_nonzero(area1<=0)+np.count_nonzero(area2<=0))
        edge_distance=c['grid']['extent_m']-max(abs(loc[0]),abs(loc[1]))
        focal_px=c['output']['height']*cam['lens_mm']/24
        edge_pixels=float((loc[2]+abs(coords[:,2].min()))/edge_distance*focal_px)
        status={'frame':frame,'folded_top_triangles':folded,'minimum_projected_triangle_area_m2':float(min(area1.min(),area2.min())*.5),'absolute_seconds':t,'spectrum_seconds':float(self.modifier.time),'z_min_m':float(coords[:,2].min()),'z_max_m':float(coords[:,2].max()),'wave_height_range_m':height,'camera_water_z_m':float(hit[0].z),'camera_clearance_m':clearance,'far_edge_below_horizon_pixels':edge_pixels,'surface_sha256':hashlib.sha256(coords.tobytes()).hexdigest(),'apply_measure_seconds':time.monotonic()-start}
        state={'surface':status['surface_sha256'],'camera_location':list(self.camera.location),'camera_rotation':list(self.camera.rotation_euler),'micro_w':float(self.micro.inputs['W'].default_value),'middle_w':float(self.middle_normal.inputs['W'].default_value),'exposure':self.scene.view_settings.exposure}
        status['state_sha256']=hashlib.sha256(json.dumps(state,sort_keys=True).encode()).hexdigest()
        dump(self.out/'latest-state.json',status)
        if folded:raise RuntimeError(f'Top surface folds at frame {frame}: {folded} inverted triangles')
        if clearance<c['safety']['clearance_m']:raise RuntimeError(f'Unsafe camera at frame {frame}: clearance {clearance:.3f}m')
        if height>c['safety']['max_wave_height_m']:raise RuntimeError(f'Wave height {height:.3f}m exceeds safety envelope at frame {frame}')
        if edge_pixels>c['safety']['horizon_edge_pixels']:raise RuntimeError(f'Far boundary {edge_pixels:.2f}px below horizon exceeds coverage tolerance')
        return status


def main():
    p=argparse.ArgumentParser();p.add_argument('--config',required=True);p.add_argument('--output',required=True)
    p.add_argument('--mode',choices=['build','frame','clip'],default='build');p.add_argument('--frames');p.add_argument('--quality',choices=['preview','native'],default='preview');p.add_argument('--device',choices=['CPU','METAL'],default='CPU')
    args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    c=load(args.config);frames=frames_for(c,args.mode,args.frames);out=Path(args.output).resolve()
    if out.exists() and any(out.iterdir()):raise ConfigError('Output directory must be empty; existing evidence is never overwritten')
    out.mkdir(parents=True,exist_ok=True)
    manifest={'status':'running','blender_version':bpy.app.version_string,'blender_build_hash':bpy.app.build_hash.decode(),'configuration_sha256':hashlib.sha256(json.dumps(c,sort_keys=True).encode()).hexdigest(),'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'mode':args.mode,'quality':args.quality,'requested_frames':frames,'implementation_present':True,'deterministic_numeric':'not_run','image_reviewed':'not_run','continuous_reviewed':'not_run','reference_target':'not_verified','approximations':['Medium waves are filtered linear dispersive sine waves, not a second FFT cascade.','Micro-normal noise is an artistic time-varying approximation, not a wind spectrum.','Unresolved far displacement is filtered to mean level; finite boundary projection is measured.','Clouds are procedural directional noise, not volumetric clouds.'],'rendered':[]}
    manifest['source_files']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),HERE/'config.py']}
    manifest['source_bundle_sha256']=hashlib.sha256(json.dumps(manifest['source_files'],sort_keys=True).encode()).hexdigest()
    manifest['scene_note']='scene.blend is an editable frame snapshot; run build_ocean.py for absolute-time animation, not Blender timeline playback.'
    dump(out/'effective-config.json',c);dump(out/'manifest.json',manifest)
    try:
        runtime=Ocean(c,out,args.quality,args.device);manifest['devices']=runtime.devices
        manifest['effective_engine']={'sensor_fit':'VERTICAL','sensor_height_mm':24,'view_transform':'AgX','exposure':0,'animated_seed':False,'volume_bounces':0,'transparent_max_bounces':4,'medium_normal_scale_per_m':.65,'medium_normal_strength':.3,'medium_normal_distance_m':c['medium']['amplitude_m']*2,'medium_normal_w_per_second':.12,'far_geometry_filter':'exp(-(local_spacing_m/6)^2)','ocean_geometry_mode':'DISPLACE','sun_disc':False,'source_scene':'built from scratch'}
        manifest['mesh']={'top_vertices':len(runtime.base),'total_vertices':len(runtime.full_coordinates),'repeat_x':1,'repeat_y':1,'closure':'perimeter skirts and single bottom cap; no Solidify'}
        # Preflight every output frame, even for a sparse or partial requested render.
        measurements=[]
        try:
            for f in range(1,runtime.scene.frame_end+1):
                manifest['preflight_current_frame']=f
                measurements.append(runtime.apply(f))
        finally:
            dump(out/'measurements.json',measurements)
        # Random-access rewind check compares coordinates; does not imply video or image acceptance.
        order=[runtime.scene.frame_end,1,max(1,runtime.scene.frame_end//2),max(1,runtime.scene.frame_end//3),1]
        rewind=[]
        for f in order:
            check=runtime.apply(f);rewind.append({'frame':f,'matches_sequential':check['state_sha256']==measurements[f-1]['state_sha256'],'state_sha256':check['state_sha256'],'surface_sha256':check['surface_sha256']})
        manifest['rewind_checks']=rewind
        manifest['deterministic_numeric']='passed' if all(x['matches_sequential'] for x in rewind) else 'failed'
        if manifest['deterministic_numeric']!='passed':raise RuntimeError('Absolute-time rewind mismatch')
        runtime.apply(frames[0],False);bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'))
        if args.mode!='build':
            (out/'frames').mkdir(exist_ok=True)
            for frame in frames:
                runtime.apply(frame,False);path=out/'frames'/f'ocean_{frame:04d}.png';runtime.scene.render.filepath=str(path)
                start=time.monotonic();bpy.ops.render.render(write_still=True);elapsed=time.monotonic()-start
                manifest['rendered'].append({'frame':frame,'path':str(path.relative_to(out)),'seconds':elapsed,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()});dump(out/'manifest.json',manifest)
                if elapsed>c['safety']['max_frame_seconds']:raise RuntimeError('Frame exceeded resource time budget; remaining render cancelled')
        manifest['status']='complete';manifest['actual_dimensions']=[round(c['output']['width']*runtime.scene.render.resolution_percentage/100),round(c['output']['height']*runtime.scene.render.resolution_percentage/100)]
    except Exception as exc:
        manifest['status']='failed';manifest['error']=str(exc);dump(out/'manifest.json',manifest);raise
    dump(out/'manifest.json',manifest)
    print(json.dumps({'output':str(out),'status':manifest['status'],'rendered_frames':len(manifest['rendered'])}))

if __name__=='__main__':main()
