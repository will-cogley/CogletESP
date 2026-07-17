# CogletESP V1.1 camera patch

This package adapts the former `bread-compact-wifi-s3cam` profile to the
CogletESP V1.1_3 schematic while keeping the legacy Kconfig symbol for
compatibility with an existing `sdkconfig`.

## Main changes

- Board menu label is now `CogletESP V1.1 (Camera, no LCD)`.
- The selected board now builds `main/boards/cogletesp-v1_1/`.
- LCD/SPI initialization and the misleading GPIO3 status LED are removed.
- Camera GPIOs follow the CogletESP V1.1_3 schematic:
  - D0..D7 = GPIO39, 40, 41, 42, 14, 2, 8, 3
  - XCLK = GPIO13, PCLK = GPIO12
  - VSYNC = GPIO9, HREF = GPIO11
  - SCCB SDA = GPIO21, SCL = GPIO47
  - PWDN = GPIO10, RESET = GPIO48
- Failed camera initialization is now cleaned up. The device continues in
  audio-only mode instead of retaining camera/video resources and provoking
  repeated UDP `errno=12` failures.

## Build steps

1. Open ESP-IDF v5.5.3 PowerShell.
2. Enter the project directory.
3. Run `idf.py menuconfig` and verify:
   - Board Type: `CogletESP V1.1 (Camera, no LCD)`
   - Camera sensor: select the physically installed sensor, e.g. GC0308.
4. Run `idf.py fullclean` once because the board source changed.
5. Run `idf.py build`.
6. Flash and monitor with `idf.py -p COM20 flash monitor` (replace COM20 if needed).

## Expected camera log

Success should include camera detection and `Camera initialized successfully`.
If camera probing still fails, the firmware should log that resources were
released and continue without the camera; UDP audio should remain stable.
