Coglet GC0308 原厂自动 ISP 基线补丁

目的：
1. 撤销应用层 16 位字节交换。
2. 撤销 U/V 交换实验。
3. 不再使用手动白平衡增益。
4. 显式启用 GC0308 内部：
   - AEC 自动曝光
   - AWB 自动白平衡
   - AGC 自动增益
5. 强制特殊效果为 Normal，避免灰度/负片模式。
6. 恢复 GC0308 原厂白平衡种子：
   R/G/B = 0x56 / 0x40 / 0x4A
7. 将画面方向改为 HMirror=false、VFlip=false。

它不会修改：
- PCLK、MCLK、VSYNC/HREF
- 分辨率、窗口和帧率
- DMA
- GC0308 完整初始化寄存器表

覆盖方式：
把压缩包内容合并到工程根目录并覆盖同名文件。

menuconfig 必须确认：
[ ] CAMERA_SENSOR_SWAP_PIXEL_BYTE_ORDER
[ ] XIAOZHI_ENABLE_CAMERA_ENDIANNESS_SWAP

然后执行：
idf.py fullclean
idf.py build
idf.py -p COM20 flash monitor

启动成功应看到类似：
GC0308 factory-auto: AAAA_EN=0x57 (AEC=1 AWB=1 AGC=1),
AEC_CTRL=0x90, EFFECT=0x00, current R/G/B=...

说明：
GC0308 的完整 ISP 初始化表本来就会在 set_format 时写入。
本补丁只是显式恢复自动控制并打印读回值，建立一个干净基线。
