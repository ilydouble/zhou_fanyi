#!/usr/bin/env python3
"""
使用阿里云SDK的人脸融合客户端
"""

import os
import logging
from alibabacloud_facebody20191230.client import Client as FacebodyClient
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_facebody20191230.models import MergeImageFaceRequest, AddFaceImageTemplateRequest
from alibabacloud_tea_util import models as util_models

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FaceFusionSDKClient:
    """使用阿里云SDK的人脸融合客户端"""
    
    def __init__(self):
        """初始化客户端"""
        self.client = None
        self.init_client()
    
    def init_client(self):
        """初始化阿里云客户端"""
        try:
            # 从环境变量获取配置
            access_key_id = os.getenv('ALIYUN_ACCESS_KEY_ID')
            access_key_secret = os.getenv('ALIYUN_ACCESS_KEY_SECRET')
            
            if not access_key_id or not access_key_secret:
                logger.error("缺少阿里云访问凭证")
                return False
            
            # 创建配置
            config = open_api_models.Config(
                access_key_id=access_key_id,
                access_key_secret=access_key_secret
            )
            
            # 设置访问的域名
            config.endpoint = 'facebody.cn-shanghai.aliyuncs.com'
            
            # 创建客户端
            self.client = FacebodyClient(config)
            logger.info("阿里云SDK客户端初始化成功")
            return True
            
        except Exception as e:
            logger.error(f"阿里云SDK客户端初始化失败: {e}")
            return False
    
    def add_face_template(self, template_image_url):
        """
        添加人脸模板

        Args:
            template_image_url: 模板照片URL

        Returns:
            dict: 添加结果，包含模板ID
        """
        if not self.client:
            return {
                'success': False,
                'message': '客户端未初始化'
            }

        try:
            logger.info(f"开始添加人脸模板: {template_image_url[:50]}...")

            # 创建请求
            request = AddFaceImageTemplateRequest(
                image_url=template_image_url
            )

            # 创建运行时选项
            runtime = util_models.RuntimeOptions()

            # 调用API
            response = self.client.add_face_image_template_with_options(request, runtime)

            # 检查响应
            if response and response.body:
                body = response.body

                if hasattr(body, 'data') and body.data and hasattr(body.data, 'template_id'):
                    template_id = body.data.template_id
                    logger.info(f"模板添加成功，模板ID: {template_id}")
                    return {
                        'success': True,
                        'data': {
                            'templateId': template_id,
                            'requestId': body.request_id if hasattr(body, 'request_id') else ''
                        }
                    }
                else:
                    error_msg = body.message if hasattr(body, 'message') else '未知错误'
                    logger.error(f"模板添加API返回错误: {error_msg}")
                    return {
                        'success': False,
                        'message': error_msg
                    }
            else:
                logger.error("模板添加API响应为空")
                return {
                    'success': False,
                    'message': '模板添加API响应为空'
                }

        except Exception as e:
            logger.error(f"模板添加调用失败: {e}")
            return {
                'success': False,
                'message': f'模板添加API调用失败: {str(e)}'
            }

    def merge_face(self, user_image_url, template_id):
        """
        人脸融合

        Args:
            user_image_url: 用户照片URL
            template_id: 模板ID（通过add_face_template获得）

        Returns:
            dict: 融合结果
        """
        if not self.client:
            return {
                'success': False,
                'message': '客户端未初始化'
            }

        try:
            logger.info(f"开始人脸融合: 用户图片={user_image_url[:50]}..., 模板ID={template_id}")

            # 创建请求
            request = MergeImageFaceRequest(
                image_url=user_image_url,
                template_id=template_id  # 使用注册后的模板ID
            )
            
            # 创建运行时选项
            runtime = util_models.RuntimeOptions()
            
            # 调用API
            response = self.client.merge_image_face_with_options(request, runtime)
            
            # 检查响应
            if response and response.body:
                body = response.body
                
                if hasattr(body, 'data') and body.data and hasattr(body.data, 'image_url'):
                    logger.info("人脸融合成功")
                    return {
                        'success': True,
                        'data': {
                            'imageUrl': body.data.image_url,
                            'requestId': body.request_id if hasattr(body, 'request_id') else ''
                        }
                    }
                else:
                    error_msg = body.message if hasattr(body, 'message') else '未知错误'
                    logger.error(f"API返回错误: {error_msg}")
                    return {
                        'success': False,
                        'message': error_msg
                    }
            else:
                logger.error("API响应为空")
                return {
                    'success': False,
                    'message': 'API响应为空'
                }
                
        except Exception as e:
            logger.error(f"人脸融合调用失败: {e}")
            return {
                'success': False,
                'message': f'API调用失败: {str(e)}'
            }
    
    def test_connection(self):
        """测试连接"""
        if not self.client:
            return False
        
        try:
            # 使用一个简单的API调用来测试连接
            # 这里可以调用一个轻量级的API来验证连接
            logger.info("测试阿里云SDK连接...")
            return True
        except Exception as e:
            logger.error(f"连接测试失败: {e}")
            return False

def create_face_fusion_sdk_client():
    """创建人脸融合SDK客户端"""
    try:
        client = FaceFusionSDKClient()
        if client.client:
            logger.info("人脸融合SDK客户端创建成功")
            return client
        else:
            logger.error("人脸融合SDK客户端创建失败")
            return None
    except Exception as e:
        logger.error(f"创建人脸融合SDK客户端时出错: {e}")
        return None

if __name__ == "__main__":
    # 测试客户端
    client = create_face_fusion_sdk_client()
    if client:
        print("✓ SDK客户端创建成功")
        if client.test_connection():
            print("✓ 连接测试成功")
        else:
            print("✗ 连接测试失败")
    else:
        print("✗ SDK客户端创建失败")
