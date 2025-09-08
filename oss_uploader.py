#!/usr/bin/env python3
"""
阿里云OSS文件上传服务
用于为LivePortrait API提供可访问的文件URL

功能特点:
- 自动上传文件到OSS
- 生成带签名的URL（支持私有Bucket）
- 自动文件分类（图片/音频）
- 支持自定义有效期
"""

import oss2
import os
import time
from pathlib import Path
from typing import Optional
import logging
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

logger = logging.getLogger(__name__)

class OSSUploader:
    def __init__(self):
        # OSS认证信息 - 从环境变量或直接配置
        self.access_key_id = os.getenv('OSS_ACCESS_KEY_ID', 'yourkey')
        self.access_key_secret = os.getenv('OSS_ACCESS_KEY_SECRET', 'yoursecret')
        self.bucket_name = os.getenv('OSS_BUCKET_NAME', 'yourname')
        self.endpoint = os.getenv('OSS_ENDPOINT', 'yourendpoint')
        
        # OSS基础路径
        self.base_oss_path = os.getenv('OSS_BASE_PATH', 'liveportrait')
        
        # 初始化OSS客户端
        try:
            self.auth = oss2.Auth(self.access_key_id, self.access_key_secret)
            self.bucket = oss2.Bucket(self.auth, f'https://{self.endpoint}', self.bucket_name)
            
            # 测试连接
            self._test_connection()
            logger.info("OSS连接初始化成功")
            
        except Exception as e:
            logger.error(f"OSS初始化失败: {e}")
            raise
    
    def _test_connection(self):
        """测试OSS连接"""
        try:
            # 尝试列出bucket信息来测试连接
            self.bucket.get_bucket_info()
        except Exception as e:
            raise Exception(f"OSS连接测试失败: {e}")

    def generate_signed_url(self, oss_object_key: str, expire_hours: int = 24) -> Optional[str]:
        """
        生成OSS签名URL，用于API访问私有文件

        Args:
            oss_object_key: OSS对象键（文件路径）
            expire_hours: 签名URL有效期（小时），默认24小时

        Returns:
            签名URL，失败返回None
        """
        try:
            # 生成签名URL
            expire_seconds = expire_hours * 3600
            signed_url = self.bucket.sign_url('GET', oss_object_key, expire_seconds)

            logger.info(f"生成签名URL成功: {oss_object_key}, 有效期: {expire_hours}小时")
            return signed_url

        except Exception as e:
            logger.error(f"生成签名URL失败: {e}")
            return None

    def generate_public_url(self, oss_object_key: str) -> str:
        """
        生成OSS公开访问URL（不带签名）
        注意：需要bucket设置为公开读取权限

        Args:
            oss_object_key: OSS对象键（文件路径）

        Returns:
            公开访问URL
        """
        # 构建公开访问URL
        public_url = f"https://{self.bucket_name}.{self.endpoint}/{oss_object_key}"
        logger.info(f"生成公开URL: {oss_object_key}")
        return public_url

    def _test_url_access(self, url: str) -> bool:
        """
        测试URL是否可以访问

        Args:
            url: 要测试的URL

        Returns:
            True如果可以访问，False如果不能访问
        """
        try:
            import requests
            response = requests.head(url, timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def upload_file(self, local_file_path: Path, custom_path: Optional[str] = None, use_public_url: bool = False) -> Optional[str]:
        """
        上传文件到OSS并返回公网URL

        Args:
            local_file_path: 本地文件路径
            custom_path: 自定义OSS路径，如果不提供则使用文件名
            use_public_url: 是否使用公开URL（不带签名），默认False使用签名URL

        Returns:
            文件的公网URL，失败返回None
        """
        try:
            if not local_file_path.exists():
                logger.error(f"本地文件不存在: {local_file_path}")
                return None

            # 构建OSS对象键
            if custom_path:
                oss_object_key = f"{self.base_oss_path}/{custom_path}"
            else:
                # 使用时间戳避免文件名冲突
                timestamp = int(time.time())
                file_extension = local_file_path.suffix
                oss_object_key = f"{self.base_oss_path}/{timestamp}_{local_file_path.name}"

            # 确保路径使用正斜杠
            oss_object_key = oss_object_key.replace('\\', '/')

            logger.info(f"开始上传文件: {local_file_path} -> {oss_object_key}")

            # 执行上传
            result = self.bucket.put_object_from_file(oss_object_key, str(local_file_path))

            if result.status == 200:
                if use_public_url:
                    # 生成公开URL（用于模板等需要API访问的文件）
                    public_url = self.generate_public_url(oss_object_key)
                    logger.info(f"文件上传成功，生成公开URL: {oss_object_key}")
                    return public_url
                else:
                    # 生成签名URL（用于用户上传的文件）
                    signed_url = self.generate_signed_url(oss_object_key, expire_hours=24)
                    if signed_url:
                        logger.info(f"文件上传成功，生成签名URL: {oss_object_key}")
                        return signed_url
                    else:
                        logger.error(f"文件上传成功但生成签名URL失败: {oss_object_key}")
                        return None
            else:
                logger.error(f"文件上传失败，状态码: {result.status}")
                return None
                
        except oss2.exceptions.NoSuchBucket:
            logger.error(f"Bucket不存在: {self.bucket_name}")
            return None
        except oss2.exceptions.AccessDenied:
            logger.error("OSS访问权限不足，请检查AccessKey权限")
            return None
        except FileNotFoundError:
            logger.error(f"本地文件不存在: {local_file_path}")
            return None
        except Exception as e:
            logger.error(f"上传文件时发生错误: {e}")
            return None
    
    def upload_image(self, image_path: Path) -> Optional[str]:
        """上传图片文件"""
        custom_path = f"images/{image_path.name}"
        return self.upload_file(image_path, custom_path)
    
    def upload_audio(self, audio_path: Path) -> Optional[str]:
        """上传音频文件"""
        custom_path = f"audio/{audio_path.name}"
        return self.upload_file(audio_path, custom_path)
    
    def delete_file(self, oss_object_key: str) -> bool:
        """删除OSS上的文件"""
        try:
            self.bucket.delete_object(oss_object_key)
            logger.info(f"文件删除成功: {oss_object_key}")
            return True
        except Exception as e:
            logger.error(f"删除文件失败: {e}")
            return False
    
    def list_files(self, prefix: str = None) -> list:
        """列出OSS上的文件"""
        try:
            if prefix is None:
                prefix = self.base_oss_path
            
            files = []
            for obj in oss2.ObjectIterator(self.bucket, prefix=prefix):
                # 为每个文件生成签名URL
                signed_url = self.generate_signed_url(obj.key, expire_hours=1)
                files.append({
                    'key': obj.key,
                    'size': obj.size,
                    'last_modified': obj.last_modified,
                    'url': signed_url
                })
            
            return files
        except Exception as e:
            logger.error(f"列出文件失败: {e}")
            return []
    
    def cleanup_old_files(self, max_age_hours: int = 24):
        """清理超过指定时间的文件"""
        try:
            current_time = time.time()
            deleted_count = 0
            
            for obj in oss2.ObjectIterator(self.bucket, prefix=self.base_oss_path):
                # 计算文件年龄
                file_age_hours = (current_time - obj.last_modified.timestamp()) / 3600
                
                if file_age_hours > max_age_hours:
                    if self.delete_file(obj.key):
                        deleted_count += 1
            
            logger.info(f"清理完成，删除了 {deleted_count} 个过期文件")
            return deleted_count
            
        except Exception as e:
            logger.error(f"清理文件失败: {e}")
            return 0

# 测试函数
def test_oss_uploader():
    """测试OSS上传功能"""
    try:
        uploader = OSSUploader()
        
        # 测试上传一个小文件
        test_file = Path("test.txt")
        test_file.write_text("这是一个测试文件")
        
        url = uploader.upload_file(test_file, "test/test.txt")
        if url:
            print(f"测试上传成功: {url}")
            
            # 清理测试文件
            test_file.unlink()
            
            return True
        else:
            print("测试上传失败")
            return False
            
    except Exception as e:
        print(f"测试失败: {e}")
        return False

if __name__ == "__main__":
    test_oss_uploader()
