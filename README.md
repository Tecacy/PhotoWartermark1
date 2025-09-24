# 图片拍摄时间水印添加工具

一个Python命令行程序，可以读取图片EXIF信息中的拍摄时间，并将其作为水印添加到图片上。

## 功能特点

- 📸 自动读取图片EXIF信息中的拍摄时间
- 🎨 支持自定义水印样式：
  - 字体大小设置
  - 颜色选择（支持颜色名称、RGB值、十六进制）
  - 位置选择（左上角、右上角、居中、左下角、右下角）
  - 透明度调节
- 📁 批量处理目录中的图片
- 💾 自动创建输出目录，保留原图质量
- 🛡️ 完善的错误处理和用户提示

## 安装

1. 安装依赖：
```bash
pip install -r requirements.txt
```

## 使用方法

### 基本用法

处理单个图片文件：
```bash
python photo_watermark.py 图片路径
```

处理整个目录：
```bash
python photo_watermark.py 目录路径
```

### 高级选项

```bash
python photo_watermark.py 图片路径 --font-size 48 --color red --position top-left --opacity 0.9
```

### 参数说明

- `input_path`: 图片文件路径或目录路径（必需）
- `--font-size`: 水印字体大小，默认 36
- `--color`: 水印颜色，支持：
  - 颜色名称：white, black, red, green, blue, yellow, cyan, magenta
  - RGB格式：255,255,255
  - 十六进制：#FF0000
- `--position`: 水印位置，可选：
  - top-left（左上角）
  - top-right（右上角）
  - center（居中）
  - bottom-left（左下角）
  - bottom-right（右下角，默认）
- `--opacity`: 水印透明度，0-1，默认 0.8

## 示例

1. 处理单个图片，使用大字体红色水印：
```bash
python photo_watermark.py photo.jpg --font-size 60 --color red --position center
```

2. 批量处理目录，使用蓝色半透明水印：
```bash
python photo_watermark.py ./photos --color blue --opacity 0.6
```

3. 使用自定义RGB颜色：
```bash
python photo_watermark.py photo.jpg --color "255,128,0" --position top-right
```

## 输出

- 单个文件：在同级目录创建 `原文件名_watermark` 目录
- 批量处理：在同级目录创建 `原目录名_watermark` 目录
- 输出文件保持原始图片格式和质量

## 支持的图片格式

- JPEG (.jpg, .jpeg)
- PNG (.png)
- BMP (.bmp)
- TIFF (.tiff, .tif)

## 注意事项

- 需要图片包含EXIF拍摄时间信息
- 如果图片没有EXIF信息，会使用"未知日期"作为水印
- 程序会自动处理不同操作系统下的字体路径
- 输出图片质量设置为95%以保留最佳画质

## 错误处理

程序会处理以下情况：
- 文件路径不存在
- 不支持的图片格式
- EXIF信息读取失败
- 字体加载失败（自动回退到默认字体）
- 图片处理过程中的其他错误

## 许可证

MIT License