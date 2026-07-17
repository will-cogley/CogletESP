#ifndef _COGLETESP_V1_1_BOARD_CONFIG_H_
#define _COGLETESP_V1_1_BOARD_CONFIG_H_

#include <driver/gpio.h>

// CogletESP V1.1_3
// Schematic: SCH_ASCII文件 V2_2026-07-09

#define AUDIO_INPUT_SAMPLE_RATE  16000
#define AUDIO_OUTPUT_SAMPLE_RATE 24000

// Coglet uses separate I2S buses for microphone input and speaker output.
#define AUDIO_I2S_METHOD_SIMPLEX

#define AUDIO_I2S_MIC_GPIO_WS    GPIO_NUM_4
#define AUDIO_I2S_MIC_GPIO_SCK   GPIO_NUM_5
#define AUDIO_I2S_MIC_GPIO_DIN   GPIO_NUM_6
#define AUDIO_I2S_SPK_GPIO_DOUT  GPIO_NUM_7
#define AUDIO_I2S_SPK_GPIO_BCLK  GPIO_NUM_15
#define AUDIO_I2S_SPK_GPIO_LRCK  GPIO_NUM_16

#define BOOT_BUTTON_GPIO          GPIO_NUM_0

// DVP camera data bus: sensor Y2..Y9 map to D0..D7.
#define CAMERA_PIN_D0             GPIO_NUM_39  // Y2
#define CAMERA_PIN_D1             GPIO_NUM_40  // Y3
#define CAMERA_PIN_D2             GPIO_NUM_41  // Y4
#define CAMERA_PIN_D3             GPIO_NUM_42  // Y5
#define CAMERA_PIN_D4             GPIO_NUM_14  // Y6
#define CAMERA_PIN_D5             GPIO_NUM_2   // Y7
#define CAMERA_PIN_D6             GPIO_NUM_8   // Y8
#define CAMERA_PIN_D7             GPIO_NUM_3   // Y9

#define CAMERA_PIN_XCLK           GPIO_NUM_13  // MCLK
#define CAMERA_PIN_PCLK           GPIO_NUM_12
#define CAMERA_PIN_VSYNC          GPIO_NUM_9
#define CAMERA_PIN_HREF           GPIO_NUM_11
#define CAMERA_PIN_SIOC           GPIO_NUM_47  // SCCB SCL
#define CAMERA_PIN_SIOD           GPIO_NUM_21  // SCCB SDA
#define CAMERA_PIN_PWDN           GPIO_NUM_10
#define CAMERA_PIN_RESET          GPIO_NUM_48
#define XCLK_FREQ_HZ              20000000

// GC0308 color baseline is configured at runtime by
// Esp32Camera::SetGc0308FactoryAuto(). No manual WB gains are used here.

#endif  // _COGLETESP_V1_1_BOARD_CONFIG_H_
