"""Pure-Python configuration and render-range validation; no Blender dependency."""
import json
import math
from pathlib import Path

class ConfigError(ValueError):
    pass

def validate(config):
    c = config
    def require(condition, message):
        if not condition:
            raise ConfigError(message)
    def number(value, lo, hi, label, integer=False):
        require(type(value) in (int, float) and math.isfinite(value), f'{label}: finite number required')
        require(lo <= value <= hi, f'{label}: must be in [{lo}, {hi}]')
        require(not integer or type(value) is int, f'{label}: integer required')
    expected = {
        'output': {'width','height','fps','duration_seconds'},
        'render': {'preview_percentage','preview_samples','native_samples','threads','max_bounces','transmission_bounces','max_clip_frames'},
        'grid': {'points','extent_m','center_spacing_scale_m','bottom_depth_m'},
        'ocean': {'resolution','spatial_size_m','wind_m_s','wave_scale','smallest_wave_m','choppiness','alignment','direction_rad','depth_m','time_origin_s','time_speed'},
        'medium': {'amplitude_m','wavelengths_m','direction_rad','fade_distance_m'},
        'micro': {'scale_per_m','strength','distance_m','time_speed'},
        'water': {'surface_color','roughness','ior','transmission','absorption_color','absorption_density'},
        'lighting': {'sun_elevation_deg','sun_azimuth_deg','sun_energy','sun_angle_deg','sky_strength','cloud_coverage','cloud_brightness'},
        'camera': {'start','end','target_start','target_end','lens_mm'},
        'safety': {'clearance_m','max_wave_height_m','horizon_edge_pixels','max_frame_seconds'},
    }
    require(type(c) is dict, 'config must be an object')
    require(set(c) == set(expected) | {'schema_version','name','seed'}, 'unknown or missing top-level fields')
    require(type(c['schema_version']) is int and c['schema_version'] == 1, 'schema_version must be 1')
    require(type(c['name']) is str and 0 < len(c['name']) < 100, 'name required')
    number(c['seed'], 0, 2147483647, 'seed', True)
    for section, fields in expected.items():
        require(type(c[section]) is dict and set(c[section]) == fields, f'{section}: unknown or missing fields')
    bounds = {
        'output': {'width':(64,2160),'height':(64,3840),'fps':(1,60),'duration_seconds':(.1,10)},
        'render': {'preview_percentage':(5,100),'preview_samples':(1,32),'native_samples':(8,96),'threads':(1,4),'max_bounces':(2,8),'transmission_bounces':(2,6),'max_clip_frames':(1,60)},
        'grid': {'points':(33,321),'extent_m':(500,10000),'center_spacing_scale_m':(2,20),'bottom_depth_m':(10,100)},
        'ocean': {'resolution':(4,12),'spatial_size_m':(30,200),'wind_m_s':(2,20),'wave_scale':(.01,3),'smallest_wave_m':(.1,5),'choppiness':(0,1),'alignment':(0,1),'direction_rad':(-math.pi,math.pi),'depth_m':(10,200),'time_origin_s':(0,100),'time_speed':(.1,2)},
        'medium': {'amplitude_m':(0,.3),'direction_rad':(-math.pi,math.pi),'fade_distance_m':(10,100)},
        'micro': {'scale_per_m':(.1,8),'strength':(0,.4),'distance_m':(0,.15),'time_speed':(0,1)},
        'water': {'roughness':(.025,.3),'ior':(1.3,1.4),'transmission':(0,1),'absorption_density':(.001,.3)},
        'lighting': {'sun_elevation_deg':(5,70),'sun_azimuth_deg':(-180,180),'sun_energy':(.1,4),'sun_angle_deg':(.3,5),'sky_strength':(.1,2),'cloud_coverage':(0,.5),'cloud_brightness':(.1,1)},
        'camera': {'lens_mm':(20,70)},
        'safety': {'clearance_m':(.3,5),'max_wave_height_m':(.5,10),'horizon_edge_pixels':(.5,5),'max_frame_seconds':(10,300)},
    }
    ints = {'width','height','fps','preview_percentage','preview_samples','native_samples','threads','max_bounces','transmission_bounces','max_clip_frames','points','resolution','spatial_size_m'}
    for section, fields in bounds.items():
        for key, (lo,hi) in fields.items():
            number(c[section][key],lo,hi,f'{section}.{key}',key in ints)
    for key in ('surface_color','absorption_color'):
        v=c['water'][key];require(type(v) is list and len(v)==3, f'water.{key}: RGB required')
        for x in v:number(x,0,1,f'water.{key}')
    for key in ('start','end','target_start','target_end'):
        v=c['camera'][key];require(type(v) is list and len(v)==3,f'camera.{key}: XYZ required')
        for x in v:number(x,-100,100,f'camera.{key}')
    waves=c['medium']['wavelengths_m'];require(type(waves) is list and 1<=len(waves)<=8,'medium.wavelengths_m: 1..8 wavelengths required')
    for x in waves:number(x,.5,10,'medium.wavelengths_m')
    require(c['grid']['points']%2==1,'grid.points must be odd')
    require(c['output']['width']%2==0 and c['output']['height']%2==0,'output dimensions must be even')
    require(c['render']['transmission_bounces']<=c['render']['max_bounces'],'transmission_bounces cannot exceed max_bounces')
    require(c['output']['duration_seconds']*c['output']['fps']>=1,'duration must contain a frame')
    for a,b in [('start','target_start'),('end','target_end')]:
        require(sum((x-y)**2 for x,y in zip(c['camera'][a],c['camera'][b]))>.01,'camera and target must differ')
        require(c['camera'][a][2]>=c['safety']['clearance_m']+.2,'camera height below minimum safety clearance')
    spacing=c['grid']['center_spacing_scale_m']*math.sinh(math.asinh(c['grid']['extent_m']/c['grid']['center_spacing_scale_m'])*2/(c['grid']['points']-1))
    require(spacing<=min(waves)/2,'central mesh spacing undersamples medium wavelengths')
    require(c['grid']['bottom_depth_m']>c['safety']['max_wave_height_m']*2,'bottom depth must exceed twice allowed wave height')
    return c

def load(path):
    return validate(json.loads(Path(path).read_text(encoding='utf-8')))

def frames_for(config, mode, spec=None):
    count=round(config['output']['duration_seconds']*config['output']['fps'])
    if spec:
        try: frames=[int(v) for v in spec.split(',')]
        except ValueError as exc: raise ConfigError('frames must be comma-separated integers') from exc
    else: frames=[1] if mode!='clip' else list(range(1,min(count,config['output']['fps'])+1))
    if not frames or len(set(frames))!=len(frames) or any(f<1 or f>count for f in frames):
        raise ConfigError(f'frames must be unique and in 1..{count}')
    if mode=='clip':
        if frames!=list(range(frames[0],frames[-1]+1)):
            raise ConfigError('clip frames must be contiguous; use frame mode for sparse frames')
        if len(frames)>config['render']['max_clip_frames']:
            raise ConfigError('clip exceeds max_clip_frames; long rendering is deliberately not automatic')
    return frames
