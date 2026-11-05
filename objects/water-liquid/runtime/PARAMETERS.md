# Runtime 参数与接口

本目录是原创 Blender 5.2.1 实现；不依赖历史 `.blend`、本机目录或网络素材。`scene.blend` 是可编辑的指定帧快照，直接拖动 Blender 时间线不会重算海面；`build_ocean.py` 是时间求值和动画渲染入口。配置是完整合同，未知字段、缺字段、非法范围或资源耦合错误均拒绝。

```sh
blender -b -t 4 --python-exit-code 1 --python build_ocean.py -- \
  --config presets/open-ocean.json --output /your/empty/output --mode build

blender -b -t 4 --python-exit-code 1 --python build_ocean.py -- \
  --config presets/open-ocean.json --output /your/empty/native --mode frame \
  --frames 1,36,72 --quality native --device METAL

blender -b -t 4 --python-exit-code 1 --python build_ocean.py -- \
  --config presets/open-ocean.json --output /your/empty/clip --mode clip \
  --quality preview --device METAL
```

`--mode build`只建场景、逐帧几何预检与乱序数值恢复检查；`frame`渲染指定离散帧；`clip`只接受连续帧，默认前一秒。`--frames 1,2,3`逐项列帧，不将`1,12,24`解释为范围。短片默认最多24帧，配置硬上限60帧，拒绝自动长片。`--quality preview|native`明确区分预演和原生输出；`--device CPU|METAL`默认CPU，Metal不可用时明确失败，不静默回退。输出目录必须为空，防止覆盖旧证据。非零退出须带`--python-exit-code 1`。

本入口输出PNG序列，避免隐式下载或占用另一个编码器。可按配置fps用已有FFmpeg串行编码，例如`ffmpeg -framerate 24 -i frames/ocean_%04d.png -c:v libx264 -pix_fmt yuv420p clip.mp4`。编码、声音、完整播放不被几何或渲染成功代替。

## 参数单位、职责与耦合

| 字段 | 单位／类型 | 作用与耦合 |
| --- | --- | --- |
| schema_version | 整数，固定1 | 配置合同版本。 |
| name | 字符串 | 预设说明，不参与模拟。 |
| seed | 整数 | FFT、解析波相位和Cycles固定随机种子；不是每帧随机。 |
| output.width, height | 像素，偶数 | 原生尺寸；预演按百分比缩放，覆盖容差仍按原生像素核验。 |
| output.fps | 帧/秒 | `t=(frame-1)/fps`，改变fps会改变帧号与时间的关系。 |
| output.duration_seconds | 秒，最多10 | 定义整个相机路径和预检范围；不等于自动全片渲染。 |
| render.preview_percentage | 百分比 | 仅预览尺寸；不改变网格和时间求值。 |
| render.preview_samples, native_samples | Cycles样本数 | 分别限制预览/原生采样，最大32/96。 |
| render.threads | CPU线程数，1—4 | 显式限制；不生成并行渲染实例。 |
| render.max_bounces | 反弹次数，2—8 | 光线追踪上限；调低须检查反射和透射变化。 |
| render.transmission_bounces | 透射次数，2—6 | 不可超过总反弹次数；体积散射反弹固定0，仅使用吸收。 |
| render.max_clip_frames | 帧数，1—60 | 短片防成本上限。 |
| grid.points | 每轴点数，奇数33—321 | 顶面点数为平方；非均匀网格，近中心密、远方疏。 |
| grid.extent_m | 米，中心至边界 | 网格固定世界位置；相机最高点与最大偏移决定远边界像素容差。 |
| grid.center_spacing_scale_m | 米 | sinh网格的近密远疏尺度；与points、extent共同决定中心采样间隔。 |
| grid.bottom_depth_m | 米 | 底面z为负值；只有外周裙边与单底盖，没有复制底面网格或Solidify。须大于允许波高的两倍。 |
| ocean.resolution | Blender引擎量，4—12 | FFT内部网格分辨率控制，不是输出像素；DISPLACE使用自建顶面，repeat固定1。 |
| ocean.spatial_size_m | 米 | 频谱域尺度。改变它会改变浪形与实际振幅关系，必须重新测波高，不能只沿用wave_scale。 |
| ocean.wind_m_s | 米/秒 | 风浪频谱输入，不是相机速度。 |
| ocean.wave_scale | 引擎位移比例 | **不是米制浪高**；实际z范围逐帧测量。 |
| ocean.smallest_wave_m | 米 | Ocean的wave_scale_min，最短波长过滤阈值；不应低于几何可解析范围。 |
| ocean.choppiness | 引擎比例，0—1 | 水平压缩/浪尖形态；最终仍检查顶面三角形投影翻折。 |
| ocean.alignment | 比例，0—1 | 风浪方向性；不接受超出RNA范围的值。 |
| ocean.direction_rad | 弧度 | 波向；与medium方向独立，产生多尺度层次。 |
| ocean.depth_m | 米 | 频谱深度；不等于闭合底面深度。 |
| ocean.time_origin_s | 模拟秒 | 初始波相，固定可重放。 |
| ocean.time_speed | 倍率 | FFT时间为origin+t×speed；为艺术时间倍率，不宣称物理实时时钟。 |
| medium.amplitude_m | 米 | 解析中波总振幅预算，各波分摊，再经过采样与距离过滤。 |
| medium.wavelengths_m | 米数组，1—8项 | 线性重力波，角频率sqrt(gk)；是近似中波，不冒充第二层FFT。 |
| medium.direction_rad | 弧度 | 第一中波方向，其他波按固定角差展开。 |
| medium.fade_distance_m | 米 | 中波随世界半径衰减，同时按局部网格间距做频率过滤。 |
| micro.scale_per_m | 1/米 | 世界坐标噪声尺度，不随镜头粘连。 |
| micro.strength | 无量纲 | Bump法线强度，不改变几何轮廓。 |
| micro.distance_m | 米 | Bump距离尺度；与strength、roughness共同决定细高光，过大像金属。 |
| micro.time_speed | 噪声W/秒 | 4D噪声的绝对时间变化率；不是物理风浪频谱。 |
| water.surface_color | 线性RGB | 表面色；透射/吸收才承担厚度颜色，不只靠底色。 |
| water.roughness | 比例 | 表面有效粗糙度；应配合微法线、太阳角尺寸抑制碎闪。 |
| water.ior | 折射率 | 默认1.333；约束1.3—1.4。 |
| water.transmission | 比例 | 表面透射权重，1为全透射介质表面。 |
| water.absorption_color | 线性RGB | Blender体积吸收颜色，不是直接显示色或测得的海水光谱。 |
| water.absorption_density | 引擎密度/世界米 | 封闭水体内光程消光强度；没有散射或焦散实现。 |
| lighting.sun_elevation_deg | 度 | 太阳高度，影响反射路径与浪形阴影。 |
| lighting.sun_azimuth_deg | 度 | 从+X朝+Y的方位；窄竖幅需确认高光路径是否落在镜头内。 |
| lighting.sun_energy | Blender太阳能量 | 单一方向灯；天空关闭太阳圆盘，不再添加第二个太阳灯。 |
| lighting.sun_angle_deg | 度 | 太阳角尺寸，控制高光宽度和碎闪。 |
| lighting.sky_strength | 比例 | 天空环境光强；过高会压平浪形、冲淡太阳路径。 |
| lighting.cloud_coverage | 混合上限比例 | 方向噪声的云遮罩最大混合量，不是气象云量百分比。 |
| lighting.cloud_brightness | 线性亮度 | 程序化云亮度；不是体积云。 |
| camera.start, end | XYZ米 | 整片起终点，绝对时间线性插值，无默认Bezier波速变化。 |
| camera.target_start, target_end | XYZ米 | 看向点同样线性插值；不得与相机位置重合。 |
| camera.lens_mm | 毫米 | 固定竖向24mm传感器；同时用于保守远边界像素估计。 |
| safety.clearance_m | 米 | 每个输出帧用顶面BVH测相机下方水面，低于阈值拒绝渲染。 |
| safety.max_wave_height_m | 米 | 全顶面z最大减最小的允许范围；不是仅浪尖高度。 |
| safety.horizon_edge_pixels | 原生像素 | 全程有限水面远边界距理想地平线的保守容差；不是雾遮挡。 |
| safety.max_frame_seconds | 秒 | 单帧完成后超过预算立即取消余下帧；不能中断卡死的底层GPU调用。 |

## 实现与证据边界

- 大波：Blender Ocean DISPLACE求值；自建非均匀世界网格，不随相机重定位。未解析的远处位移逐渐过滤到平均海平面。
- 中波：固定seed解析重力波近似，波速与波长关联；微波：稳定世界坐标4D噪声法线近似；另以0.65/米的中尺度噪声法线接续远景（strength 0.3、distance为中波振幅2倍、W速度0.12/秒），这些派生值写入manifest.effective_engine。两者都不宣称完整谱级联。
- 体积：顶面、外周裙边、底盖闭合，光程吸收有效；没有体积散射、白沫历史、岸线、焦散、跨水面或浮力。
- 每次建场景都检查整片所有输出帧，保存实际波高、相机净空、投影翻折、远边界像素、几何哈希与耗时；失败保存已测范围、当前帧、错误和latest-state。
- `manifest.json`分别记录implementation_present、deterministic_numeric、image_reviewed、continuous_reviewed、reference_target。运行器只自动赋实现和数值状态；不会把渲染成功升级为视觉或参考通过。
- `.blend`、有效配置、构建脚本/config.py哈希与Blender版本是可复查依据。几何哈希仅说明同机同版本数值恢复，不证明跨GPU逐像素一致。
- `max_frame_seconds`是完成后止损，不是看门狗。外部终止进程、系统休眠和GPU挂起仍需宿主管理，不能据此承诺绝对运行时间上限。
