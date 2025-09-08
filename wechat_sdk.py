#!/usr/bin/env python3
"""
微信JS-SDK和API封装
"""

import hashlib
import time
import random
import string
import requests
import json
import logging

logger = logging.getLogger(__name__)

class WechatSDK:
    def __init__(self, appid, appsecret):
        self.appid = appid
        self.appsecret = appsecret
        self.access_token = None
        self.access_token_expires = 0
        self.jsapi_ticket = None
        self.jsapi_ticket_expires = 0
        
    def get_access_token(self):
        """获取access_token"""
        # 检查是否已有有效的access_token
        if self.access_token and time.time() < self.access_token_expires:
            return self.access_token
            
        try:
            url = f"https://api.weixin.qq.com/cgi-bin/token"
            params = {
                'grant_type': 'client_credential',
                'appid': self.appid,
                'secret': self.appsecret
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if 'access_token' in data:
                self.access_token = data['access_token']
                # access_token有效期7200秒，提前5分钟过期
                self.access_token_expires = time.time() + data.get('expires_in', 7200) - 300
                logger.info("微信access_token获取成功")
                return self.access_token
            else:
                logger.error(f"获取access_token失败: {data}")
                return None
                
        except Exception as e:
            logger.error(f"获取access_token异常: {e}")
            return None
    
    def get_jsapi_ticket(self):
        """获取jsapi_ticket"""
        # 检查是否已有有效的jsapi_ticket
        if self.jsapi_ticket and time.time() < self.jsapi_ticket_expires:
            return self.jsapi_ticket
            
        access_token = self.get_access_token()
        if not access_token:
            return None
            
        try:
            url = f"https://api.weixin.qq.com/cgi-bin/ticket/getticket"
            params = {
                'access_token': access_token,
                'type': 'jsapi'
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get('errcode') == 0:
                self.jsapi_ticket = data['ticket']
                # jsapi_ticket有效期7200秒，提前5分钟过期
                self.jsapi_ticket_expires = time.time() + data.get('expires_in', 7200) - 300
                logger.info("微信jsapi_ticket获取成功")
                return self.jsapi_ticket
            else:
                logger.error(f"获取jsapi_ticket失败: {data}")
                return None
                
        except Exception as e:
            logger.error(f"获取jsapi_ticket异常: {e}")
            return None
    
    def generate_js_config(self, url):
        """生成JS-SDK配置"""
        logger.info(f"开始生成JS-SDK配置，URL: {url}")

        # 清理URL - 移除hash部分
        clean_url = url.split('#')[0] if url else ''
        logger.info(f"清理后的URL: {clean_url}")

        jsapi_ticket = self.get_jsapi_ticket()
        timestamp = int(time.time())
        noncestr = ''.join(random.choices(string.ascii_letters + string.digits, k=16))

        if jsapi_ticket:
            # 有jsapi_ticket时生成真实签名
            sign_str = f"jsapi_ticket={jsapi_ticket}&noncestr={noncestr}&timestamp={timestamp}&url={clean_url}"
            signature = hashlib.sha1(sign_str.encode('utf-8')).hexdigest()

            logger.info(f"签名字符串: {sign_str}")
            logger.info(f"生成的签名: {signature}")
            logger.info(f"AppId: {self.appid}")
            logger.info(f"Timestamp: {timestamp}")
            logger.info(f"NonceStr: {noncestr}")
        else:
            # 没有jsapi_ticket时生成模拟签名（用于开发测试）
            logger.warning("无法获取jsapi_ticket，生成模拟配置")
            signature = 'mock_signature_for_development'

        config = {
            'appId': self.appid,
            'timestamp': timestamp,
            'nonceStr': noncestr,
            'signature': signature
        }

        logger.info(f"最终配置: {config}")
        return config
    
    def download_media(self, media_id):
        """下载微信媒体文件"""
        access_token = self.get_access_token()
        if not access_token:
            return None
            
        try:
            url = f"https://api.weixin.qq.com/cgi-bin/media/get"
            params = {
                'access_token': access_token,
                'media_id': media_id
            }
            
            response = requests.get(url, params=params, timeout=30)
            
            # 检查响应头，确保是图片文件
            content_type = response.headers.get('content-type', '')
            if not content_type.startswith('image/'):
                # 可能是错误响应，尝试解析JSON
                try:
                    error_data = response.json()
                    logger.error(f"下载媒体文件失败: {error_data}")
                    return None
                except:
                    logger.error(f"下载媒体文件失败: 未知错误")
                    return None
            
            if response.status_code == 200:
                logger.info(f"微信媒体文件下载成功，大小: {len(response.content)} bytes")
                return response.content
            else:
                logger.error(f"下载媒体文件失败，状态码: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"下载媒体文件异常: {e}")
            return None

    def upload_media(self, file_path, media_type='image'):
        """上传媒体文件到微信服务器"""
        access_token = self.get_access_token()
        if not access_token:
            logger.error("无法获取access_token")
            return None

        try:
            # 微信上传媒体文件API
            url = f"https://api.weixin.qq.com/cgi-bin/media/upload?access_token={access_token}&type={media_type}"

            # 准备文件数据
            with open(file_path, 'rb') as f:
                files = {
                    'media': (file_path.name, f, 'image/jpeg')
                }

                response = requests.post(url, files=files, timeout=30)

            if response.status_code == 200:
                result = response.json()

                if 'media_id' in result:
                    logger.info(f"媒体文件上传成功: {result['media_id']}")
                    return result['media_id']
                else:
                    logger.error(f"上传失败: {result}")
                    return None
            else:
                logger.error(f"上传请求失败: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"上传媒体文件异常: {e}")
            return None

def create_wechat_sdk():
    """创建微信SDK实例"""
    import os

    appid = os.getenv('WECHAT_APPID', 'wx2dfdec3e7ae9a3ff')
    appsecret = os.getenv('WECHAT_APPSECRET', 'd5bc14defd9f1f28c885553e558bf7d0')

    if not appid or not appsecret:
        logger.warning("微信配置未设置")
        return None

    try:
        sdk = WechatSDK(appid, appsecret)
        # 测试获取access_token
        access_token = sdk.get_access_token()
        if access_token:
            logger.info("微信SDK初始化成功")
            return sdk
        else:
            logger.warning("微信SDK初始化失败：无法获取access_token，可能需要配置IP白名单")
            # 即使无法获取access_token，也返回SDK实例，用于生成JS配置
            return sdk
    except Exception as e:
        logger.error(f"微信SDK初始化异常: {e}")
        # 即使出现异常，也返回SDK实例，用于基本功能
        return WechatSDK(appid, appsecret)
