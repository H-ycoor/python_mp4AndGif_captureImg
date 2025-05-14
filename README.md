HI！

如果你需要给你的ArduinoOled添加视频动画而苦恼转换工具，那么也许你可以试试这个简易的转换工具他或许能帮助到你
这是基于pysimpleGUI为图形窗口的python转换cpp数组工具


# Arduino OLED视频动画转换工具

## 🚀 项目亮点
一键转换：将MP4/AVI视频转为Arduino兼容的帧数据

内存优化：自动生成PROGMEM存储的紧凑格式

精确控制：可调帧间隔(0.05s~1.0s)和分辨率(128x64)

跨平台：支持Windows/macOS/Linux

## 📦 快速开始
安装依赖
```bash
pip install opencv-python pillow numpy pysimplegui
```
设置输出路径（默认生成frames.h）

调整帧间隔滑块

点击"开始转换"

## 🛠️ 技术细节
生成的数据结构
``` cpp
// 示例输出 frames.h
const PROGMEM uint8_t frame_000[] = { 
  0x00, 0x7F, ... // 1024字节/帧 
};
const uint8_t* const all_frames[] PROGMEM = { frame_000, ... };
const uint16_t FRAME_COUNT = 15;
Arduino集成示例
cpp
#include "frames.h"

void loop() {
  const uint8_t* frame = (const uint8_t*)pgm_read_ptr(&all_frames[currentFrame]);
  display.drawBitmap(0, 0, frame, 128, 64, WHITE);
  currentFrame = (currentFrame + 1) % FRAME_COUNT;
  delay(100); 
}
```
## 🌟 进阶功能
动态内存检测：自动警告超出芯片容量

多语言支持：内置中文/英文界面

预设配置：保存常用转换参数

## 🛠️ 硬件兼容性
开发板	最大推荐帧数
Arduino Uno	15帧
Arduino Mega	100帧
ESP32	500帧+

## 💡 常见问题
Q: 转换后动画播放卡顿？
A: 尝试：

降低帧率（增大间隔）

使用display.startWrite()加速绘制

Q: 出现白屏/花屏？

cpp
// 添加诊断代码：
Serial.println(pgm_read_byte(&frame_000[0])); // 应返回非零值
## 📜 开源协议
MIT License - 欢迎提交Pull Request！

