#!/usr/bin/env python3
"""
周繁漪人脸融合 Web 服务器
支持微信H5和普通H5版本
"""

import os
import sys
import time
import uuid
import json
import logging
from pathlib import Path

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

# 导入现有的OSS上传器和人脸融合API
from oss_uploader import OSSUploader
from face_fusion_sdk import create_face_fusion_sdk_client
from wechat_sdk import create_wechat_sdk

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask应用配置
app = Flask(__name__)
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# 文件上传配置
UPLOAD_FOLDER = Path('web/uploads')
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# 模板配置
TEMPLATES_CONFIG_FILE = 'web/templates_config.json'

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def handle_wechat_upload(local_id):
    """处理微信localId上传"""
    try:
        if not wechat_sdk:
            return jsonify({
                'success': False,
                'message': '微信SDK未初始化'
            }), 500

        print(f"开始处理微信图片上传，localId: {local_id}")

        # 1. 下载微信媒体文件
        media_data = wechat_sdk.download_media(local_id)
        if not media_data:
            return jsonify({
                'success': False,
                'message': '下载微信媒体文件失败'
            }), 500

        # 2. 保存到临时文件
        timestamp = int(time.time())
        temp_filename = f"wechat_{timestamp}_{uuid.uuid4().hex[:8]}.jpg"
        temp_path = Path(UPLOAD_FOLDER) / temp_filename

        # 确保上传目录存在
        temp_path.parent.mkdir(parents=True, exist_ok=True)

        with open(temp_path, 'wb') as f:
            f.write(media_data)

        print(f"微信图片已保存到临时文件: {temp_path}")

        # 3. 上传到OSS
        if oss_uploader:
            oss_url = oss_uploader.upload_file(temp_path, f"face_fusion/user_images/{temp_filename}")

            # 删除临时文件
            temp_path.unlink()

            if oss_url:
                print(f"微信图片上传到OSS成功: {oss_url}")
                return jsonify({
                    'success': True,
                    'url': oss_url,
                    'message': '微信图片上传成功'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'OSS上传失败'
                }), 500
        else:
            # 如果没有OSS，返回本地路径
            local_url = f"/uploads/{temp_filename}"
            print(f"微信图片保存到本地: {local_url}")
            return jsonify({
                'success': True,
                'url': local_url,
                'message': '微信图片上传成功（本地存储）'
            })

    except Exception as e:
        print(f"微信上传处理失败: {e}")
        return jsonify({
            'success': False,
            'message': f'微信上传处理失败: {str(e)}'
        }), 500

# 初始化OSS上传器
oss_uploader = None
try:
    oss_uploader = OSSUploader()
    if oss_uploader:
        print("OSS上传器初始化成功")
    else:
        print("OSS上传器初始化失败")
except Exception as e:
    print(f"OSS上传器初始化错误: {e}")
    oss_uploader = None

# 初始化人脸融合客户端
face_fusion_client = None
try:
    face_fusion_client = create_face_fusion_sdk_client()
    if face_fusion_client:
        print("人脸融合SDK客户端初始化成功")
    else:
        print("人脸融合SDK客户端初始化失败")
except Exception as e:
    print(f"人脸融合客户端初始化错误: {e}")
    face_fusion_client = None

# 初始化微信SDK
wechat_sdk = None
try:
    wechat_sdk = create_wechat_sdk()
    if wechat_sdk:
        print("微信SDK初始化成功")
    else:
        print("微信SDK初始化失败")
except Exception as e:
    print(f"微信SDK初始化错误: {e}")
    wechat_sdk = None

# 加载模板配置
def load_templates_config():
    """加载模板配置"""
    try:
        with open(TEMPLATES_CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载模板配置失败: {e}")
        return {
            "templates": [
                {
                    "id": "1",
                    "name": "周繁漪风格1",
                    "description": "经典造型",
                    "thumbnailUrl": "/templates/template1.jpg",
                    "templateUrl": "/templates/template1.jpg",
                    "url": "/fanyi?template=1"
                }
            ]
        }

templates_config = load_templates_config()



# 路由定义
@app.route('/')
def index():
    """主页"""
    return send_from_directory('web', 'index.html')

@app.route('/fanyi')
def fanyi():
    """人脸融合页面"""
    return send_from_directory('web', 'fanyi.html')

@app.route('/fanyi-wechat')
def fanyi_wechat():
    """微信版人脸融合页面"""
    return send_from_directory('web', 'fanyi-wechat.html')



@app.route('/oss-manager')
def oss_manager():
    """OSS存储管理页面"""
    return send_from_directory('web', 'oss-manager.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """静态文件服务"""
    return send_from_directory('web', filename)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """上传文件访问"""
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/templates/<filename>')
def template_file(filename):
    """模板文件访问"""
    return send_from_directory('web/templates', filename)

@app.route('/api/templates')
def get_templates():
    """获取模板列表"""
    try:
        return jsonify({
            'success': True,
            'data': templates_config.get('templates', [])
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取模板列表失败: {str(e)}'
        }), 500

@app.route('/api/template/<template_id>')
def get_template(template_id):
    """获取单个模板信息"""
    try:
        templates = templates_config.get('templates', [])
        template = next((t for t in templates if t['id'] == template_id), None)

        if template:
            return jsonify({
                'success': True,
                'data': template
            })
        else:
            return jsonify({
                'success': False,
                'message': '模板不存在'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取模板失败: {str(e)}'
        }), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """文件上传接口 - 支持普通文件和微信localId"""
    try:
        # 检查是否是微信localId上传
        if 'wechat_local_id' in request.form:
            return handle_wechat_upload(request.form['wechat_local_id'])

        # 检查是否有文件
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'message': '没有选择文件'
            }), 400

        file = request.files['file']

        # 检查文件名
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': '没有选择文件'
            }), 400

        # 检查文件类型
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'message': '不支持的文件类型'
            }), 400

        # 生成安全的文件名
        timestamp = int(time.time())
        filename = secure_filename(file.filename)
        _, ext = os.path.splitext(filename)
        safe_filename = f"{timestamp}_{uuid.uuid4().hex[:8]}{ext}"

        # 保存文件
        file_path = UPLOAD_FOLDER / safe_filename
        file.save(file_path)

        # 上传到OSS
        if oss_uploader:
            oss_url = oss_uploader.upload_file(file_path, f"face_fusion/user_images/{safe_filename}")

            # 删除本地文件
            file_path.unlink()

            if oss_url:
                return jsonify({
                    'success': True,
                    'url': oss_url,
                    'message': '文件上传成功'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'OSS上传失败'
                }), 500
        else:
            # 如果没有OSS，返回本地路径
            return jsonify({
                'success': True,
                'url': f'/uploads/{safe_filename}',
                'message': '文件上传成功（本地存储）'
            })

    except Exception as e:
        print(f"文件上传失败: {e}")
        return jsonify({
            'success': False,
            'message': f'文件上传失败: {str(e)}'
        }), 500

@app.route('/api/wechat/config', methods=['POST'])
def wechat_config():
    """获取微信JS-SDK配置"""
    try:
        if not wechat_sdk:
            return jsonify({
                'success': False,
                'message': '微信SDK未初始化'
            }), 500

        data = request.get_json()
        url = data.get('url', '')

        # 使用真实的微信SDK生成配置
        config = wechat_sdk.generate_js_config(url)

        if config:
            return jsonify({
                'success': True,
                'data': config
            })
        else:
            return jsonify({
                'success': False,
                'message': '微信配置生成失败'
            }), 500

    except Exception as e:
        print(f"微信配置获取失败: {e}")
        return jsonify({
            'success': False,
            'message': f'微信配置获取失败: {str(e)}'
        }), 500

@app.route('/wechat-signature', methods=['GET'])
def wechat_signature():
    """微信签名接口 - 按照你的例子实现"""
    try:
        if not wechat_sdk:
            return jsonify({
                'error': '微信SDK未初始化'
            }), 500

        url = request.args.get('url', '')

        if not url:
            return jsonify({
                'error': '缺少URL参数'
            }), 400

        print(f"生成微信签名，URL: {url}")

        # 使用微信SDK生成配置
        config = wechat_sdk.generate_js_config(url)

        if config:
            print(f"签名生成成功: {config}")
            # 直接返回配置，不包装在success字段中
            return jsonify(config)
        else:
            return jsonify({
                'error': '微信配置生成失败'
            }), 500

    except Exception as e:
        print(f"微信签名生成失败: {e}")
        return jsonify({
            'error': f'签名生成失败: {str(e)}'
        }), 500





@app.route('/api/wechat/download-image', methods=['POST'])
def wechat_download_image():
    """从微信服务器下载图片"""
    try:
        if not wechat_sdk:
            return jsonify({
                'success': False,
                'message': '微信SDK未初始化'
            }), 500

        data = request.get_json()
        server_id = data.get('serverId', '')

        if not server_id:
            return jsonify({
                'success': False,
                'message': '缺少serverId参数'
            }), 400

        print(f"开始从微信服务器下载图片，serverId: {server_id}")

        # 1. 从微信服务器下载图片
        media_data = wechat_sdk.download_media(server_id)
        if not media_data:
            return jsonify({
                'success': False,
                'message': '从微信服务器下载图片失败'
            }), 500

        # 2. 保存到临时文件
        timestamp = int(time.time())
        temp_filename = f"wechat_server_{timestamp}_{uuid.uuid4().hex[:8]}.jpg"
        temp_path = Path(UPLOAD_FOLDER) / temp_filename

        # 确保上传目录存在
        temp_path.parent.mkdir(parents=True, exist_ok=True)

        with open(temp_path, 'wb') as f:
            f.write(media_data)

        print(f"微信图片已保存到临时文件: {temp_path}")

        # 3. 上传到OSS
        if oss_uploader:
            oss_url = oss_uploader.upload_file(temp_path, f"face_fusion/user_images/{temp_filename}")

            # 删除临时文件
            temp_path.unlink()

            if oss_url:
                print(f"微信图片上传到OSS成功: {oss_url}")
                return jsonify({
                    'success': True,
                    'url': oss_url,
                    'message': '微信图片处理成功'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'OSS上传失败'
                }), 500
        else:
            # 如果没有OSS，返回本地路径
            local_url = f"/uploads/{temp_filename}"
            print(f"微信图片保存到本地: {local_url}")
            return jsonify({
                'success': True,
                'url': local_url,
                'message': '微信图片处理成功（本地存储）'
            })

    except Exception as e:
        print(f"微信图片下载处理失败: {e}")
        return jsonify({
            'success': False,
            'message': f'微信图片下载处理失败: {str(e)}'
        }), 500

@app.route('/api/face-fusion', methods=['POST'])
def face_fusion():
    """人脸融合API"""
    try:
        if not face_fusion_client:
            return jsonify({
                'success': False,
                'message': '人脸融合服务未初始化'
            }), 500

        data = request.get_json()
        user_image_url = data.get('userImageUrl')
        template_id = data.get('templateId')

        if not user_image_url or not template_id:
            return jsonify({
                'success': False,
                'message': '缺少必要参数'
            }), 400

        # 获取模板信息
        templates = templates_config.get('templates', [])
        template = next((t for t in templates if t['id'] == template_id), None)

        if not template:
            return jsonify({
                'success': False,
                'message': '模板不存在'
            }), 404

        # 使用预先注册的阿里云模板ID
        aliyun_template_id = template.get('aliyunTemplateId')
        if not aliyun_template_id:
            return jsonify({
                'success': False,
                'message': f'模板 {template_id} 未注册到阿里云'
            }), 500

        print(f"开始人脸融合: 用户图片={user_image_url}, 模板ID={aliyun_template_id}")

        # 调用人脸融合API
        result = face_fusion_client.merge_face(
            user_image_url=user_image_url,
            template_id=aliyun_template_id
        )

        if result and result.get('success'):
            return jsonify({
                'success': True,
                'data': result.get('data', {}),
                'message': '人脸融合成功'
            })
        else:
            return jsonify({
                'success': False,
                'message': result.get('message', '人脸融合失败')
            }), 500

    except Exception as e:
        print(f"人脸融合失败: {e}")
        return jsonify({
            'success': False,
            'message': f'人脸融合失败: {str(e)}'
        }), 500



@app.route('/api/wechat/save-image', methods=['POST'])
def wechat_save_image():
    """微信保存图片到相册 - 正确的流程"""
    try:
        if not wechat_sdk:
            return jsonify({
                'success': False,
                'message': '微信SDK未初始化'
            }), 500

        data = request.get_json()
        image_url = data.get('imageUrl', '')

        if not image_url:
            return jsonify({
                'success': False,
                'message': '缺少图片URL'
            }), 400

        print(f"开始处理图片保存到微信: {image_url}")

        # 1. 从OSS下载图片到服务器
        import requests
        response = requests.get(image_url, timeout=30)
        if response.status_code != 200:
            return jsonify({
                'success': False,
                'message': '从OSS下载图片失败'
            }), 500

        # 2. 保存到临时文件
        timestamp = int(time.time())
        temp_filename = f"save_{timestamp}_{uuid.uuid4().hex[:8]}.jpg"
        temp_path = Path(UPLOAD_FOLDER) / temp_filename

        with open(temp_path, 'wb') as f:
            f.write(response.content)

        print(f"图片已下载到服务器: {temp_path}")

        # 3. 上传图片到微信服务器
        media_id = wechat_sdk.upload_media(temp_path, media_type='image')

        if not media_id:
            return jsonify({
                'success': False,
                'message': '上传到微信服务器失败'
            }), 500

        print(f"图片已上传到微信服务器，media_id: {media_id}")

        # 4. 删除临时文件
        temp_path.unlink()

        # 5. 返回微信media_id
        return jsonify({
            'success': True,
            'mediaId': media_id,
            'message': '图片已上传到微信服务器'
        })

    except Exception as e:
        print(f"微信保存图片处理失败: {e}")
        return jsonify({
            'success': False,
            'message': f'处理失败: {str(e)}'
        }), 500

@app.route('/api/cleanup', methods=['POST'])
def manual_cleanup():
    """手动清理OSS过期文件"""
    try:
        if not oss_uploader:
            return jsonify({
                'success': False,
                'message': 'OSS上传器未初始化'
            }), 500

        # 获取清理参数
        data = request.get_json() or {}
        max_age_hours = data.get('max_age_hours', 24)

        # 执行清理
        deleted_count = oss_uploader.cleanup_old_files(max_age_hours=max_age_hours)

        return jsonify({
            'success': True,
            'deleted_count': deleted_count,
            'message': f'清理完成，删除了 {deleted_count} 个过期文件'
        })

    except Exception as e:
        print(f"手动清理失败: {e}")
        return jsonify({
            'success': False,
            'message': f'清理失败: {str(e)}'
        }), 500

@app.route('/api/oss/status')
def oss_status():
    """查看OSS存储状态"""
    try:
        if not oss_uploader:
            return jsonify({
                'success': False,
                'message': 'OSS上传器未初始化'
            }), 500

        # 列出文件
        files = oss_uploader.list_files()

        # 计算统计信息
        total_files = len(files)
        total_size = sum(file.get('size', 0) for file in files)

        # 按时间分类
        current_time = time.time()
        recent_files = []
        old_files = []

        for file in files:
            file_age_hours = (current_time - file.get('last_modified', current_time).timestamp()) / 3600
            if file_age_hours > 24:
                old_files.append(file)
            else:
                recent_files.append(file)

        return jsonify({
            'success': True,
            'data': {
                'total_files': total_files,
                'total_size_mb': round(total_size / 1024 / 1024, 2),
                'recent_files': len(recent_files),
                'old_files': len(old_files),
                'files': files[:10]  # 只返回前10个文件作为示例
            }
        })

    except Exception as e:
        print(f"获取OSS状态失败: {e}")
        return jsonify({
            'success': False,
            'message': f'获取状态失败: {str(e)}'
        }), 500



if __name__ == '__main__':
    print("🚀 启动周繁漪人脸融合服务器...")
    print(f"📁 上传目录: {UPLOAD_FOLDER}")
    print(f"🔧 OSS上传器: {'✅ 已启用' if oss_uploader else '❌ 未启用'}")
    print(f"🎭 人脸融合: {'✅ 已启用' if face_fusion_client else '❌ 未启用'}")
    print(f"📱 微信SDK: {'✅ 已启用' if wechat_sdk else '❌ 未启用'}")
    print("=" * 50)

    # 启动服务器
    app.run(
        host='0.0.0.0',
        port=80,  # 使用80端口
        debug=False,
        threaded=True
    )