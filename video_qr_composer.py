#!/usr/bin/env python3
"""
视频二维码合成器
功能：
1. 将images目录下的二维码图片合成到videos目录下对应的视频中
2. 二维码显示在视频右下角
3. 支持自定义二维码大小、位置和透明度
"""

import os
import cv2
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw
import logging
import config

# 配置日志
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT
)
logger = logging.getLogger(__name__)

class VideoQRComposer:
    def __init__(self):
        self.images_dir = Path("images")
        self.videos_dir = Path(config.VIDEOS_DIR)
        self.output_dir = Path(config.VIDEOS_WITH_QR_DIR)

        # 二维码合成参数（从配置文件读取）
        self.qr_size = config.QR_SIZE
        self.margin = config.QR_MARGIN
        self.opacity = config.QR_OPACITY

        # 确保输出目录存在
        self.output_dir.mkdir(exist_ok=True)
        
    def get_video_qr_pairs(self):
        """获取视频和二维码的配对列表"""
        pairs = []
        
        # 查找所有生成的视频文件
        video_files = list(self.videos_dir.glob("fanyi-*_generated.mp4"))
        
        for video_file in video_files:
            # 从文件名提取数字，例如 fanyi-1_generated.mp4 -> 1
            filename = video_file.stem  # fanyi-1_generated
            if filename.startswith("fanyi-") and filename.endswith("_generated"):
                number_part = filename.replace("fanyi-", "").replace("_generated", "")
                
                # 查找对应的二维码文件
                qr_file = self.images_dir / f"qr{number_part}.jpg"
                if qr_file.exists():
                    pairs.append({
                        'video': video_file,
                        'qr': qr_file,
                        'number': number_part,
                        'output': self.output_dir / f"fanyi-{number_part}_with_qr.mp4"
                    })
                    logger.info(f"找到配对: {video_file.name} <-> {qr_file.name}")
                else:
                    logger.warning(f"未找到对应的二维码: {qr_file}")
        
        return pairs
    
    def resize_qr_code(self, qr_image_path, target_size):
        """调整二维码大小并保持透明度"""
        try:
            # 使用PIL打开图片
            qr_img = Image.open(qr_image_path)
            
            # 转换为RGBA模式以支持透明度
            if qr_img.mode != 'RGBA':
                qr_img = qr_img.convert('RGBA')
            
            # 调整大小，使用高质量重采样
            qr_img = qr_img.resize((target_size, target_size), Image.Resampling.LANCZOS)
            
            # 应用透明度
            if self.opacity < 1.0:
                # 创建一个新的图像，应用透明度
                alpha = qr_img.split()[-1]  # 获取alpha通道
                alpha = alpha.point(lambda p: int(p * self.opacity))  # 应用透明度
                qr_img.putalpha(alpha)
            
            # 转换为OpenCV格式 (BGR)
            qr_cv = cv2.cvtColor(np.array(qr_img), cv2.COLOR_RGBA2BGRA)
            
            return qr_cv
            
        except Exception as e:
            logger.error(f"调整二维码大小失败: {e}")
            return None
    
    def overlay_qr_on_frame(self, frame, qr_image):
        """在视频帧上叠加二维码"""
        try:
            frame_height, frame_width = frame.shape[:2]
            qr_height, qr_width = qr_image.shape[:2]
            
            # 计算二维码在右下角的位置
            x_offset = frame_width - qr_width - self.margin
            y_offset = frame_height - qr_height - self.margin
            
            # 确保位置不会超出边界
            x_offset = max(0, x_offset)
            y_offset = max(0, y_offset)
            
            # 获取要覆盖的区域
            roi = frame[y_offset:y_offset + qr_height, x_offset:x_offset + qr_width]
            
            if qr_image.shape[2] == 4:  # 如果二维码有alpha通道
                # 分离BGR和alpha通道
                qr_bgr = qr_image[:, :, :3]
                qr_alpha = qr_image[:, :, 3] / 255.0
                
                # 应用alpha混合
                for c in range(3):
                    roi[:, :, c] = (qr_alpha * qr_bgr[:, :, c] + 
                                   (1 - qr_alpha) * roi[:, :, c])
            else:
                # 直接覆盖（如果没有alpha通道）
                roi[:] = qr_image
            
            return frame
            
        except Exception as e:
            logger.error(f"叠加二维码失败: {e}")
            return frame
    
    def compose_video_with_qr(self, video_path, qr_path, output_path):
        """将二维码合成到视频中"""
        try:
            logger.info(f"开始处理: {video_path.name}")
            
            # 打开视频文件
            cap = cv2.VideoCapture(str(video_path))
            if not cap.isOpened():
                logger.error(f"无法打开视频文件: {video_path}")
                return False
            
            # 获取视频属性
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            logger.info(f"视频信息: {width}x{height}, {fps}fps, {total_frames}帧")
            
            # 调整二维码大小
            qr_image = self.resize_qr_code(qr_path, self.qr_size)
            if qr_image is None:
                logger.error(f"无法处理二维码图片: {qr_path}")
                cap.release()
                return False
            
            # 设置视频编码器
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
            
            if not out.isOpened():
                logger.error(f"无法创建输出视频: {output_path}")
                cap.release()
                return False
            
            # 处理每一帧
            frame_count = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # 在帧上叠加二维码
                frame_with_qr = self.overlay_qr_on_frame(frame, qr_image)
                
                # 写入输出视频
                out.write(frame_with_qr)
                
                frame_count += 1
                if frame_count % 30 == 0:  # 每30帧显示一次进度
                    progress = (frame_count / total_frames) * 100
                    logger.info(f"处理进度: {progress:.1f}% ({frame_count}/{total_frames})")
            
            # 释放资源
            cap.release()
            out.release()
            
            logger.info(f"✓ 视频合成完成: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"视频合成失败: {e}")
            return False
    
    def run(self):
        """运行主程序"""
        logger.info("开始视频二维码合成任务")
        
        # 检查目录
        if not self.images_dir.exists():
            logger.error(f"images目录不存在: {self.images_dir}")
            return False
        
        if not self.videos_dir.exists():
            logger.error(f"videos目录不存在: {self.videos_dir}")
            return False
        
        # 获取视频和二维码配对
        pairs = self.get_video_qr_pairs()
        if not pairs:
            logger.warning("没有找到可处理的视频和二维码配对")
            return False
        
        logger.info(f"找到 {len(pairs)} 个配对需要处理")
        
        # 处理每个配对
        success_count = 0
        for pair in pairs:
            try:
                logger.info(f"处理配对 {pair['number']}: {pair['video'].name} + {pair['qr'].name}")
                
                if self.compose_video_with_qr(pair['video'], pair['qr'], pair['output']):
                    success_count += 1
                    logger.info(f"✓ 配对 {pair['number']} 处理完成")
                else:
                    logger.error(f"✗ 配对 {pair['number']} 处理失败")
                
                logger.info("-" * 50)
                
            except Exception as e:
                logger.error(f"处理配对 {pair['number']} 时发生错误: {e}")
        
        logger.info(f"任务完成！成功处理 {success_count}/{len(pairs)} 个视频")
        
        if success_count > 0:
            logger.info(f"合成的视频保存在: {self.output_dir.absolute()}")
        
        return success_count > 0


def main():
    """主函数"""
    print("=" * 60)
    print("视频二维码合成器")
    print("=" * 60)
    print("功能：将images目录下的二维码合成到videos目录下对应的视频右下角")
    print()
    
    try:
        composer = VideoQRComposer()
        
        # 显示当前状态
        pairs = composer.get_video_qr_pairs()
        if not pairs:
            print("没有找到可处理的视频和二维码配对")
            print("请确保:")
            print("1. videos目录下有 fanyi-*_generated.mp4 文件")
            print("2. images目录下有对应的 qr*.jpg 文件")
            return
        
        print(f"找到 {len(pairs)} 个配对:")
        for pair in pairs:
            print(f"  {pair['video'].name} + {pair['qr'].name} -> {pair['output'].name}")
        
        print()
        print(f"二维码设置:")
        print(f"  大小: {composer.qr_size}x{composer.qr_size} 像素")
        print(f"  位置: 右下角，距离边缘 {composer.margin} 像素")
        print(f"  透明度: {composer.opacity * 100}%")
        
        print()
        response = input("是否开始合成？(y/n): ")
        if response.lower() != 'y':
            print("操作已取消")
            return
        
        print()
        success = composer.run()
        
        if success:
            print("=" * 60)
            print("✓ 视频二维码合成完成！")
            print(f"合成的视频保存在: {composer.output_dir.absolute()}")
            print("=" * 60)
        else:
            print("=" * 60)
            print("✗ 合成失败，请检查日志")
            print("=" * 60)
            
    except KeyboardInterrupt:
        print("\n操作被用户中断")
    except Exception as e:
        logger.error(f"程序执行失败: {e}")
        print(f"\n程序执行失败: {e}")


if __name__ == "__main__":
    main()
