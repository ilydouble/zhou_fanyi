#!/usr/bin/env python3
"""
LivePortrait视频生成器
功能：
1. 检测pics文件夹下的图片质量
2. 对通过检测的图片生成视频
3. 使用sound/qiezi.wav作为音频
4. 输出到videos文件夹
"""

import os
import time
import requests
from pathlib import Path
from typing import List, Dict, Optional
from dotenv import load_dotenv
import logging
from oss_uploader import OSSUploader
import config

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT
)
logger = logging.getLogger(__name__)

class LivePortraitVideoGenerator:
    def __init__(self):
        self.api_key = os.getenv('ALIYUN_API_KEY')
        if not self.api_key:
            raise ValueError("请在.env文件中设置ALIYUN_API_KEY")

        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        # API端点
        self.detect_url = config.API_ENDPOINTS['detect']
        self.video_synthesis_url = config.API_ENDPOINTS['video_synthesis']
        self.task_query_url = config.API_ENDPOINTS['task_query']

        # 文件路径
        self.pics_dir = Path(config.PICS_DIR)
        self.sound_file = Path(config.SOUND_FILE)
        self.videos_dir = Path(config.VIDEOS_DIR)

        # 确保输出目录存在
        self.videos_dir.mkdir(exist_ok=True)

        # 支持的图片格式
        self.supported_image_formats = config.SUPPORTED_IMAGE_FORMATS

        # 初始化OSS上传服务
        try:
            self.oss_uploader = OSSUploader()
            logger.info("OSS上传服务初始化成功")
        except Exception as e:
            logger.error(f"OSS上传服务初始化失败: {e}")
            raise
    
    def get_image_files(self) -> List[Path]:
        """获取pics目录下的所有图片文件"""
        image_files = []
        for file_path in self.pics_dir.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in self.supported_image_formats:
                image_files.append(file_path)
        return sorted(image_files)
    
    def upload_file_to_oss(self, file_path: Path) -> Optional[str]:
        """
        上传文件到OSS并获取公网URL
        """
        try:
            if not file_path.exists():
                logger.error(f"文件不存在: {file_path}")
                return None

            # 根据文件类型选择上传方法
            if file_path.suffix.lower() in self.supported_image_formats:
                url = self.oss_uploader.upload_image(file_path)
            elif file_path.suffix.lower() in {'.wav', '.mp3'}:
                url = self.oss_uploader.upload_audio(file_path)
            else:
                url = self.oss_uploader.upload_file(file_path)

            if url:
                logger.info(f"文件上传成功: {file_path} -> {url}")
            else:
                logger.error(f"文件上传失败: {file_path}")

            return url
        except Exception as e:
            logger.error(f"上传文件失败: {e}")
            return None
    
    def detect_image_quality(self, image_url: str) -> Dict:
        """检测图片质量是否符合LivePortrait要求"""
        payload = {
            "model": "liveportrait-detect",
            "input": {
                "image_url": image_url
            }
        }
        
        try:
            response = requests.post(self.detect_url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"图片质量检测失败: {e}")
            return {"error": str(e)}
    
    def submit_video_generation_task(self, image_url: str, audio_url: str) -> Dict:
        """提交视频生成任务"""
        headers = self.headers.copy()
        headers['X-DashScope-Async'] = 'enable'
        
        payload = {
            "model": "liveportrait",
            "input": {
                "image_url": image_url,
                "audio_url": audio_url
            },
            "parameters": config.VIDEO_GENERATION_PARAMS
        }
        
        try:
            response = requests.post(self.video_synthesis_url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"视频生成任务提交失败: {e}")
            return {"error": str(e)}
    
    def query_task_status(self, task_id: str) -> Dict:
        """查询任务状态"""
        url = f"{self.task_query_url}/{task_id}"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"任务状态查询失败: {e}")
            return {"error": str(e)}
    
    def wait_for_task_completion(self, task_id: str, max_wait_time: int = None) -> Dict:
        """等待任务完成"""
        if max_wait_time is None:
            max_wait_time = config.MAX_WAIT_TIME

        start_time = time.time()

        while time.time() - start_time < max_wait_time:
            result = self.query_task_status(task_id)
            
            if "error" in result:
                return result
            
            task_status = result.get("output", {}).get("task_status", "UNKNOWN")
            logger.info(f"任务 {task_id} 状态: {task_status}")
            
            if task_status == "SUCCEEDED":
                return result
            elif task_status == "FAILED":
                return result
            elif task_status in ["PENDING", "RUNNING"]:
                time.sleep(config.QUERY_INTERVAL)  # 等待后再次查询
            else:
                logger.warning(f"未知任务状态: {task_status}")
                time.sleep(config.QUERY_INTERVAL)
        
        return {"error": "任务超时"}
    
    def download_video(self, video_url: str, output_path: Path) -> bool:
        """下载生成的视频"""
        try:
            response = requests.get(video_url, stream=True)
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"视频已下载到: {output_path}")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"视频下载失败: {e}")
            return False
    
    def process_single_image(self, image_path: Path, audio_url: str) -> bool:
        """处理单个图片：检测质量并生成视频"""
        logger.info(f"处理图片: {image_path}")
        
        # 上传图片到OSS获取URL
        logger.info("上传图片到OSS...")
        image_url = self.upload_file_to_oss(image_path)
        if not image_url:
            logger.error(f"无法上传图片到OSS: {image_path}")
            return False
        
        # 检测图片质量
        logger.info("检测图片质量...")
        detect_result = self.detect_image_quality(image_url)
        
        if "error" in detect_result:
            logger.error(f"图片质量检测失败: {detect_result['error']}")
            return False
        
        if not detect_result.get("output", {}).get("pass", False):
            message = detect_result.get("output", {}).get("message", "未知错误")
            logger.warning(f"图片质量检测未通过: {message}")
            return False
        
        logger.info("图片质量检测通过")
        
        # 提交视频生成任务
        logger.info("提交视频生成任务...")
        task_result = self.submit_video_generation_task(image_url, audio_url)
        
        if "error" in task_result:
            logger.error(f"视频生成任务提交失败: {task_result['error']}")
            return False
        
        task_id = task_result.get("output", {}).get("task_id")
        if not task_id:
            logger.error("未获取到任务ID")
            return False
        
        logger.info(f"任务已提交，任务ID: {task_id}")
        
        # 等待任务完成
        logger.info("等待任务完成...")
        final_result = self.wait_for_task_completion(task_id)
        
        if "error" in final_result:
            logger.error(f"任务执行失败: {final_result['error']}")
            return False
        
        task_status = final_result.get("output", {}).get("task_status")
        if task_status != "SUCCEEDED":
            logger.error(f"任务失败，状态: {task_status}")
            return False
        
        # 下载视频
        video_url = final_result.get("output", {}).get("results", {}).get("video_url")
        if not video_url:
            logger.error("未获取到视频URL")
            return False
        
        # 生成输出文件名
        output_filename = f"{image_path.stem}_generated.mp4"
        output_path = self.videos_dir / output_filename
        
        logger.info(f"下载视频: {video_url}")
        success = self.download_video(video_url, output_path)
        
        if success:
            logger.info(f"视频生成成功: {output_path}")
        
        return success
    
    def run(self):
        """运行主程序"""
        logger.info("开始LivePortrait视频生成任务")
        
        # 检查音频文件
        if not self.sound_file.exists():
            logger.error(f"音频文件不存在: {self.sound_file}")
            return
        
        # 上传音频文件到OSS获取URL
        logger.info("上传音频文件到OSS...")
        audio_url = self.upload_file_to_oss(self.sound_file)
        if not audio_url:
            logger.error("无法上传音频文件到OSS")
            return
        
        # 获取所有图片文件
        image_files = self.get_image_files()
        if not image_files:
            logger.warning("pics目录下没有找到支持的图片文件")
            return
        
        logger.info(f"找到 {len(image_files)} 个图片文件")
        
        # 处理每个图片
        success_count = 0
        for image_path in image_files:
            try:
                if self.process_single_image(image_path, audio_url):
                    success_count += 1
                logger.info("-" * 50)
            except Exception as e:
                logger.error(f"处理图片 {image_path} 时发生错误: {e}")
        
        logger.info(f"任务完成！成功生成 {success_count}/{len(image_files)} 个视频")


if __name__ == "__main__":
    try:
        print("=" * 60)
        print("LivePortrait 视频生成器")
        print("=" * 60)
        print("正在初始化...")

        generator = LivePortraitVideoGenerator()
        generator.run()

        print("=" * 60)
        print("程序执行完成！")
        print("=" * 60)

    except KeyboardInterrupt:
        logger.info("用户中断程序执行")
        print("\n程序已被用户中断")
    except Exception as e:
        logger.error(f"程序执行失败: {e}")
        print(f"\n程序执行失败: {e}")
        print("请检查日志信息或运行 test_setup.py 验证配置")
