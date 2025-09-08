#!/usr/bin/env python3
"""
模板生成脚本：从pics目录拷贝图片到web/templates目录并生成缩略图
功能：
1. 从pics目录拷贝图片到web/templates目录
2. 重命名为template1.jpg, template2.jpg等格式
3. 生成对应的缩略图template1_thumb.jpg等
"""

import os
import shutil
from pathlib import Path
from PIL import Image
import logging
import config

# 配置日志
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT
)
logger = logging.getLogger(__name__)

class TemplateGenerator:
    def __init__(self):
        self.pics_dir = Path(config.PICS_DIR)
        self.templates_dir = Path(config.TEMPLATES_DIR)
        self.thumbnail_size = config.THUMBNAIL_SIZE
        self.thumbnail_quality = config.THUMBNAIL_QUALITY
        self.supported_formats = config.SUPPORTED_IMAGE_FORMATS
        
        # 确保模板目录存在
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
    def get_image_files(self):
        """获取pics目录下的所有图片文件"""
        image_files = []
        for file_path in self.pics_dir.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in self.supported_formats:
                image_files.append(file_path)
        return sorted(image_files)
    
    def copy_and_rename_image(self, source_path, template_number):
        """拷贝并重命名图片"""
        target_filename = f"template{template_number}.jpg"
        target_path = self.templates_dir / target_filename
        
        try:
            # 如果源文件不是jpg格式，需要转换
            if source_path.suffix.lower() != '.jpg':
                # 使用PIL转换格式
                with Image.open(source_path) as img:
                    # 转换为RGB模式（去除透明通道）
                    if img.mode in ('RGBA', 'LA', 'P'):
                        rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'P':
                            img = img.convert('RGBA')
                        rgb_img.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                        img = rgb_img
                    elif img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    # 保存为JPG格式
                    img.save(target_path, 'JPEG', quality=95)
                    logger.info(f"转换并保存: {source_path} -> {target_path}")
            else:
                # 直接拷贝JPG文件
                shutil.copy2(source_path, target_path)
                logger.info(f"拷贝: {source_path} -> {target_path}")
            
            return target_path
            
        except Exception as e:
            logger.error(f"拷贝文件失败 {source_path} -> {target_path}: {e}")
            return None
    
    def generate_thumbnail(self, image_path, template_number):
        """生成缩略图"""
        thumbnail_filename = f"template{template_number}_thumb.jpg"
        thumbnail_path = self.templates_dir / thumbnail_filename
        
        try:
            with Image.open(image_path) as img:
                # 转换为RGB模式
                if img.mode in ('RGBA', 'LA', 'P'):
                    rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    rgb_img.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                    img = rgb_img
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # 创建缩略图（保持宽高比）
                img.thumbnail(self.thumbnail_size, Image.Resampling.LANCZOS)
                
                # 创建正方形背景
                thumb = Image.new('RGB', self.thumbnail_size, (255, 255, 255))
                
                # 计算居中位置
                x = (self.thumbnail_size[0] - img.width) // 2
                y = (self.thumbnail_size[1] - img.height) // 2
                
                # 粘贴缩略图到中心
                thumb.paste(img, (x, y))
                
                # 保存缩略图
                thumb.save(thumbnail_path, 'JPEG', quality=self.thumbnail_quality)
                logger.info(f"生成缩略图: {thumbnail_path}")
                
            return thumbnail_path
            
        except Exception as e:
            logger.error(f"生成缩略图失败 {image_path} -> {thumbnail_path}: {e}")
            return None
    
    def clean_templates_directory(self):
        """清理模板目录中的旧文件"""
        try:
            for file_path in self.templates_dir.iterdir():
                if file_path.is_file() and (
                    file_path.name.startswith('template') and 
                    (file_path.name.endswith('.jpg') or file_path.name.endswith('.jpeg'))
                ):
                    file_path.unlink()
                    logger.info(f"删除旧文件: {file_path}")
        except Exception as e:
            logger.error(f"清理目录失败: {e}")
    
    def run(self, clean_first=True):
        """运行模板生成"""
        logger.info("开始生成模板和缩略图")
        
        # 检查pics目录
        if not self.pics_dir.exists():
            logger.error(f"pics目录不存在: {self.pics_dir}")
            return False
        
        # 获取图片文件
        image_files = self.get_image_files()
        if not image_files:
            logger.warning("pics目录下没有找到支持的图片文件")
            return False
        
        logger.info(f"找到 {len(image_files)} 个图片文件")
        
        # 清理旧文件
        if clean_first:
            logger.info("清理模板目录中的旧文件...")
            self.clean_templates_directory()
        
        # 处理每个图片
        success_count = 0
        for i, image_path in enumerate(image_files, 1):
            logger.info(f"处理第 {i} 个图片: {image_path.name}")
            
            try:
                # 拷贝并重命名图片
                template_path = self.copy_and_rename_image(image_path, i)
                if not template_path:
                    continue
                
                # 生成缩略图
                thumbnail_path = self.generate_thumbnail(template_path, i)
                if not thumbnail_path:
                    continue
                
                success_count += 1
                logger.info(f"✓ 模板 {i} 处理完成")
                
            except Exception as e:
                logger.error(f"处理图片 {image_path} 时发生错误: {e}")
        
        logger.info(f"任务完成！成功处理 {success_count}/{len(image_files)} 个模板")
        
        # 显示结果
        self.show_results()
        
        return success_count > 0
    
    def show_results(self):
        """显示生成结果"""
        logger.info("生成的文件列表:")
        
        template_files = sorted(self.templates_dir.glob("template*.jpg"))
        for file_path in template_files:
            file_size = file_path.stat().st_size / 1024  # KB
            logger.info(f"  {file_path.name} ({file_size:.1f} KB)")


def main():
    """主函数"""
    print("=" * 60)
    print("模板和缩略图生成器")
    print("=" * 60)
    print("功能：从pics目录拷贝图片到web/templates目录并生成缩略图")
    print()
    
    try:
        generator = TemplateGenerator()
        
        # 显示当前状态
        image_files = generator.get_image_files()
        print(f"pics目录下找到 {len(image_files)} 个图片文件:")
        for i, img in enumerate(image_files, 1):
            print(f"  {i}. {img.name}")
        
        if not image_files:
            print("没有找到图片文件，请检查pics目录")
            return
        
        print()
        response = input("是否开始生成模板和缩略图？(y/n): ")
        if response.lower() != 'y':
            print("操作已取消")
            return
        
        print()
        success = generator.run()
        
        if success:
            print("=" * 60)
            print("✓ 模板和缩略图生成完成！")
            print(f"文件保存在: {generator.templates_dir.absolute()}")
            print("=" * 60)
        else:
            print("=" * 60)
            print("✗ 生成失败，请检查日志")
            print("=" * 60)
            
    except KeyboardInterrupt:
        print("\n操作被用户中断")
    except Exception as e:
        logger.error(f"程序执行失败: {e}")
        print(f"\n程序执行失败: {e}")


if __name__ == "__main__":
    main()
