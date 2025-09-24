#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片拍摄时间水印添加工具
功能：读取图片EXIF信息中的拍摄时间，并将其作为水印添加到图片上
"""

import os
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ExifTags
from datetime import datetime
import argparse


class PhotoWatermark:
    def __init__(self):
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
        self.font_path = self._get_default_font()
    
    def _get_default_font(self):
        """获取系统默认字体"""
        if sys.platform.startswith('win'):
            return 'C:/Windows/Fonts/simhei.ttf'  # 黑体
        elif sys.platform.startswith('darwin'):
            return '/System/Library/Fonts/PingFang.ttc'
        else:
            return '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    
    def get_shooting_date(self, image_path):
        """
        从图片EXIF信息中提取拍摄日期
        Args:
            image_path: 图片文件路径
        Returns:
            str: 拍摄日期（YYYY-MM-DD格式）或None
        """
        try:
            with Image.open(image_path) as img:
                exif_data = img._getexif()
                if exif_data is None:
                    return None
                
                # 查找拍摄日期
                for tag_id, value in exif_data.items():
                    tag = ExifTags.TAGS.get(tag_id, tag_id)
                    if tag == 'DateTime':
                        # EXIF日期格式通常是 "2023:10:15 14:30:25"
                        try:
                            dt = datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
                            return dt.strftime('%Y-%m-%d')
                        except ValueError:
                            continue
                
                # 如果没有DateTime，尝试其他可能的日期字段
                date_tags = ['DateTimeOriginal', 'DateTimeDigitized']
                for tag_name in date_tags:
                    for tag_id, value in exif_data.items():
                        tag = ExifTags.TAGS.get(tag_id, tag_id)
                        if tag == tag_name:
                            try:
                                dt = datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
                                return dt.strftime('%Y-%m-%d')
                            except ValueError:
                                continue
                
                return None
                
        except Exception as e:
            print(f"读取EXIF信息时出错: {e}")
            return None
    
    def add_watermark(self, image_path, output_path, font_size=36, color=(255, 255, 255), 
                     position='bottom-right', opacity=0.8):
        """
        给图片添加水印
        Args:
            image_path: 原图片路径
            output_path: 输出图片路径
            font_size: 字体大小
            color: 字体颜色 (R, G, B)
            position: 水印位置 ('top-left', 'top-right', 'center', 'bottom-left', 'bottom-right')
            opacity: 透明度 (0-1)
        """
        try:
            # 打开图片
            with Image.open(image_path) as img:
                img = img.convert('RGBA')
                
                # 获取拍摄日期
                shooting_date = self.get_shooting_date(image_path)
                if shooting_date is None:
                    print(f"警告: {os.path.basename(image_path)} 未找到拍摄日期信息")
                    shooting_date = "未知日期"
                else:
                    # 测试功能：输出拍摄时间到控制台
                    print(f"📸 {os.path.basename(image_path)} 的拍摄时间: {shooting_date}")
                
                # 创建透明层用于绘制水印
                txt_layer = Image.new('RGBA', img.size, (255, 255, 255, 0))
                draw = ImageDraw.Draw(txt_layer)
                
                # 加载字体
                try:
                    font = ImageFont.truetype(self.font_path, font_size)
                except:
                    # 如果字体加载失败，使用默认字体
                    font = ImageFont.load_default()
                
                # 获取文本尺寸
                bbox = draw.textbbox((0, 0), shooting_date, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                # 计算水印位置
                margin = 20
                if position == 'top-left':
                    x, y = margin, margin
                elif position == 'top-right':
                    x, y = img.width - text_width - margin, margin
                elif position == 'center':
                    x, y = (img.width - text_width) // 2, (img.height - text_height) // 2
                elif position == 'bottom-left':
                    x, y = margin, img.height - text_height - margin
                else:  # bottom-right (默认)
                    x, y = img.width - text_width - margin, img.height - text_height - margin
                
                # 绘制水印（带透明度）
                text_color = (*color, int(255 * opacity))
                draw.text((x, y), shooting_date, font=font, fill=text_color)
                
                # 合并图层
                watermarked = Image.alpha_composite(img, txt_layer)
                
                # 转换回RGB模式并保存
                if str(output_path).lower().endswith('.jpg') or str(output_path).lower().endswith('.jpeg'):
                    watermarked = watermarked.convert('RGB')
                
                watermarked.save(output_path, quality=95)
                print(f"已保存: {os.path.basename(output_path)}")
                
        except Exception as e:
            print(f"处理图片 {os.path.basename(image_path)} 时出错: {e}")
            raise
    
    def process_directory(self, input_dir, font_size=36, color=(255, 255, 255), 
                         position='bottom-right', opacity=0.8):
        """
        处理整个目录的图片
        Args:
            input_dir: 输入目录路径
            font_size: 字体大小
            color: 字体颜色
            position: 水印位置
            opacity: 透明度
        """
        input_path = Path(input_dir)
        if not input_path.exists():
            print(f"错误: 目录 {input_dir} 不存在")
            return
        
        # 创建输出目录
        output_dir = input_path.parent / f"{input_path.name}_watermark"
        output_dir.mkdir(exist_ok=True)
        print(f"输出目录: {output_dir}")
        
        # 查找所有支持的图片文件
        image_files = []
        for ext in self.supported_formats:
            image_files.extend(input_path.glob(f'*{ext}'))
            image_files.extend(input_path.glob(f'*{ext.upper()}'))
        
        if not image_files:
            print("未找到支持的图片文件")
            return
        
        print(f"找到 {len(image_files)} 张图片，开始处理...")
        
        # 测试功能：先显示所有图片的拍摄时间
        print("\n=== 拍摄时间信息预览 ===")
        for img_path in image_files:
            shooting_date = self.get_shooting_date(img_path)
            if shooting_date:
                print(f"📸 {img_path.name}: {shooting_date}")
            else:
                print(f"📷 {img_path.name}: 无拍摄时间信息")
        print("=======================\n")
        
        # 处理每张图片
        success_count = 0
        for img_path in image_files:
            try:
                output_path = output_dir / img_path.name
                self.add_watermark(img_path, output_path, font_size, color, position, opacity)
                success_count += 1
            except Exception as e:
                print(f"处理 {img_path.name} 失败: {e}")
                continue
        
        print(f"\n处理完成！成功: {success_count}/{len(image_files)}")
        print(f"输出目录: {output_dir}")


def parse_color(color_str):
    """解析颜色字符串为RGB元组"""
    try:
        if color_str.startswith('#'):
            # 十六进制颜色
            color_str = color_str.lstrip('#')
            return tuple(int(color_str[i:i+2], 16) for i in (0, 2, 4))
        elif ',' in color_str:
            # RGB格式: 255,255,255
            return tuple(map(int, color_str.split(',')))
        else:
            # 预定义颜色名称
            colors = {
                'white': (255, 255, 255),
                'black': (0, 0, 0),
                'red': (255, 0, 0),
                'green': (0, 255, 0),
                'blue': (0, 0, 255),
                'yellow': (255, 255, 0),
                'cyan': (0, 255, 255),
                'magenta': (255, 0, 255)
            }
            return colors.get(color_str.lower(), (255, 255, 255))
    except:
        return (255, 255, 255)


def main():
    parser = argparse.ArgumentParser(description='图片拍摄时间水印添加工具')
    parser.add_argument('input_path', help='图片文件路径或目录路径')
    parser.add_argument('--font-size', type=int, default=36, help='水印字体大小 (默认: 36)')
    parser.add_argument('--color', default='white', help='水印颜色 (默认: white，支持: white, black, red, #FF0000, 255,255,255)')
    parser.add_argument('--position', default='bottom-right', 
                       choices=['top-left', 'top-right', 'center', 'bottom-left', 'bottom-right'],
                       help='水印位置 (默认: bottom-right)')
    parser.add_argument('--opacity', type=float, default=0.8, help='水印透明度 0-1 (默认: 0.8)')
    
    args = parser.parse_args()
    
    # 解析颜色
    color = parse_color(args.color)
    
    # 创建水印处理器
    watermark = PhotoWatermark()
    
    # 判断输入路径是文件还是目录
    input_path = Path(args.input_path)
    
    if input_path.is_file():
        # 处理单个文件
        if input_path.suffix.lower() not in watermark.supported_formats:
            print(f"错误: 不支持的文件格式 {input_path.suffix}")
            return
        
        # 创建输出目录
        output_dir = input_path.parent / f"{input_path.stem}_watermark"
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / input_path.name
        
        try:
            watermark.add_watermark(input_path, output_path, args.font_size, color, args.position, args.opacity)
            print(f"\n处理完成！输出文件: {output_path}")
        except Exception as e:
            print(f"处理失败: {e}")
    
    elif input_path.is_dir():
        # 处理整个目录
        watermark.process_directory(args.input_path, args.font_size, color, args.position, args.opacity)
    
    else:
        print(f"错误: 路径 {args.input_path} 不存在")


if __name__ == '__main__':
    main()