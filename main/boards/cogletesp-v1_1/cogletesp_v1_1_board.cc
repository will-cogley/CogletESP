#include "wifi_board.h"
#include "codecs/no_audio_codec.h"
#include "application.h"
#include "button.h"
#include "config.h"
#include "esp32_camera.h"

#include <wifi_station.h>
#include <esp_log.h>
#include <driver/gpio.h>
#include <esp_rom_sys.h>

#define TAG "CogletEspV11Board"

class CogletEspV11Board : public WifiBoard {
private:
    Button boot_button_;
    Esp32Camera* camera_ = nullptr;

    void InitializeCamera() {
        esp_log_level_set("Esp32Camera", ESP_LOG_DEBUG);
        esp_log_level_set("esp_video", ESP_LOG_DEBUG);
        esp_log_level_set("video", ESP_LOG_DEBUG);

        static esp_cam_ctlr_dvp_pin_config_t dvp_pin_config = {
            .data_width = CAM_CTLR_DATA_WIDTH_8,
            .data_io = {
                [0] = CAMERA_PIN_D0,
                [1] = CAMERA_PIN_D1,
                [2] = CAMERA_PIN_D2,
                [3] = CAMERA_PIN_D3,
                [4] = CAMERA_PIN_D4,
                [5] = CAMERA_PIN_D5,
                [6] = CAMERA_PIN_D6,
                [7] = CAMERA_PIN_D7,
            },
            .vsync_io = CAMERA_PIN_VSYNC,
            .de_io = CAMERA_PIN_HREF,
            .pclk_io = CAMERA_PIN_PCLK,
            .xclk_io = CAMERA_PIN_XCLK,
        };

        esp_video_init_sccb_config_t sccb_config = {
            .init_sccb = true,
            .i2c_config = {
                .port = 0,
                .scl_pin = CAMERA_PIN_SIOC,
                .sda_pin = CAMERA_PIN_SIOD,
            },
            .freq = 100000,
        };

        esp_video_init_dvp_config_t dvp_config = {
            .sccb_config = sccb_config,
            .reset_pin = CAMERA_PIN_RESET,
            .pwdn_pin = CAMERA_PIN_PWDN,
            .dvp_pin = dvp_pin_config,
            .xclk_freq = XCLK_FREQ_HZ,
        };

        esp_video_init_config_t video_config = {
            .dvp = &dvp_config,
        };

        // Allow camera power/reset rails to settle before probing SCCB.
        esp_rom_delay_us(20000);

        camera_ = new Esp32Camera(video_config);
        if (!camera_->IsInitialized()) {
            ESP_LOGE(TAG, "Camera initialization failed; releasing video resources and continuing without camera");
            delete camera_;
            camera_ = nullptr;
            return;
        }

        // The physical module is mounted opposite to the old branch.
        camera_->SetHMirror(false);
        camera_->SetVFlip(false);

        if (!camera_->SetGc0308FactoryAuto()) {
            ESP_LOGE(TAG, "GC0308 factory automatic controls failed");
        }

        ESP_LOGI(TAG, "Camera initialized successfully");
    }

    void InitializeButtons() {
        boot_button_.OnClick([this]() {
            auto& app = Application::GetInstance();
            if (app.GetDeviceState() == kDeviceStateStarting && !WifiStation::GetInstance().IsConnected()) {
                ResetWifiConfiguration();
            }
            app.ToggleChatState();
        });
    }

public:
    CogletEspV11Board() : boot_button_(BOOT_BUTTON_GPIO) {
        // GPIO39..42 are also default JTAG pins on ESP32-S3. Release them
        // before the DVP driver claims them for Y2..Y5.
        gpio_reset_pin(GPIO_NUM_39);
        gpio_reset_pin(GPIO_NUM_40);
        gpio_reset_pin(GPIO_NUM_41);
        gpio_reset_pin(GPIO_NUM_42);

        InitializeButtons();
        InitializeCamera();
    }

    AudioCodec* GetAudioCodec() override {
        static NoAudioCodecSimplex audio_codec(
            AUDIO_INPUT_SAMPLE_RATE,
            AUDIO_OUTPUT_SAMPLE_RATE,
            AUDIO_I2S_SPK_GPIO_BCLK,
            AUDIO_I2S_SPK_GPIO_LRCK,
            AUDIO_I2S_SPK_GPIO_DOUT,
            AUDIO_I2S_MIC_GPIO_SCK,
            AUDIO_I2S_MIC_GPIO_WS,
            AUDIO_I2S_MIC_GPIO_DIN
        );
        return &audio_codec;
    }

    Camera* GetCamera() override {
        return camera_;
    }

    // No LCD and no status LED override:
    // Board::GetDisplay() supplies NoDisplay, and Board::GetLed() supplies NoLed.
};

DECLARE_BOARD(CogletEspV11Board);
