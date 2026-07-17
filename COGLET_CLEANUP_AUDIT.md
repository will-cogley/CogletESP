# CogletESP 当前压缩包清理审计

## 结论

当前压缩包的庞大体积主要不是 Coglet 代码，而是误打包进来的 ESP-IDF 下载依赖。

- 原压缩包：约 **91.5 MiB**
- 解压后文件：**5571 个**
- 解压后总量：约 **156.7 MiB**
- `managed_components`：约 **150.1 MiB**
- 其中 `lvgl__lvgl`：约 **149.5 MiB**
- 清理后源码：**1370 个文件，约 6.5 MiB**

`managed_components` 与 `build` 都是可再生目录，不应作为源码交付内容。
工程保留 `dependencies.lock`，首次构建时 ESP-IDF Component Manager 会按锁定版本重新下载依赖。

## 本次实际删除

| 路径 | 文件数 | 大小 | 原因 |
|---|---:|---:|---|
| `managed_components` | 4196 | 150.06 MiB | ESP-IDF Component Manager 下载目录；依赖会按 dependencies.lock 重新获取，不应打进源码包 |
| `build` | 0 | 0.00 MiB | 构建输出目录；当前为空，任何时候都可由 idf.py build 重建 |
| `sdkconfig.old` | 1 | 0.09 MiB | menuconfig 自动生成的旧配置备份 |
| `main/assets/lang_config.h` | 1 | 0.01 MiB | 由 scripts/gen_lang.py 在构建时自动生成 |
| `README_覆盖说明.txt` | 1 | 0.00 MiB | 已经撤回的微雪整表实验说明，继续保留会误导 |
| `main/boards/bread-compact-wifi-s3cam` | 3 | 0.02 MiB | 旧板级目录；当前 CMake 已把该配置符号映射到 cogletesp-v1_1，工程中无引用 |

## 本次明确保留

- `sdkconfig`：包含 Coglet 板型、GC0308、PSRAM、Light Impact 等当前工作配置。
- `dependencies.lock`：固定当前 ESP32-S3 构建所用组件版本。
- `main/boards/cogletesp-v1_1`：Coglet V1.1 板级实现和引脚。
- `main/audio/codecs/no_audio_codec.cc`：当前 I2S 诊断与双核 Watchpoint。
- `main/boards/common/esp32_camera.*`：当前相机生命周期修复。
- `RP2040`：板载 RP2040 相关固件资料。
- `docs`、README、LICENSE：交接和开源所需资料。

## 为什么暂时没有删除其他约一百个板型

它们确实不是 Coglet 运行所需，但当前上游工程的 `main/CMakeLists.txt`、
`main/Kconfig.projbuild` 和 `main/idf_component.yml` 仍是“多板型框架”结构：

- CMake 中包含大量板型选择分支；
- 许多通用音频、显示和板级源文件目前被无条件编译；
- 组件清单同时声明了多种屏幕、触摸、4G、传感器依赖。

直接只删目录会让 menuconfig 中仍能选到不存在的板型，并可能造成构建失败。
真正的 Coglet-only 精简需要同步重写这三个构建文件，并在 ESP-IDF 环境里完整编译验证。

## 推荐的下一阶段

先使用本次“安全清理版”继续排查 GC0308，确保功能不被清理动作影响。
相机稳定后，再建立 Coglet-only 分支，逐步完成：

1. 固定唯一板型为 `cogletesp-v1_1`；
2. 删除其他板型目录及对应 Kconfig/CMake 分支；
3. 只编译 NoDisplay、NoLed、NoAudioCodecSimplex、Wi-Fi、相机和协议所需源文件；
4. 精简 `idf_component.yml`，停止下载 LCD、触摸、4G 和无关传感器组件；
5. 将需要长期修改的 GC0308 驱动移到项目本地组件，避免每次进入 `managed_components` 修改。

本包还加入了 `scripts/package_coglet_source.ps1`，以后运行它即可生成不含
`build` 和 `managed_components` 的干净源码压缩包。
