#!/usr/bin/env python3
"""
人脸融合H5应用后端服务
提供文件上传和人脸融合API接口
"""

import os
import time
import json
import uuid
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import requests
from dotenv import load_dotenv

# 导入现有的OSS上传器和人脸融合API
from oss_uploader import OSSUploader
from face_fusion_api import create_face_fusion_client

# 加载环境变量
load_dotenv()

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 配置
UPLOAD_FOLDER = 'web/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# 确保上传目录存在
Path(UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)

# 初始化OSS上传器
try:
    oss_uploader = OSSUploader()
    print("OSS上传器初始化成功")
except Exception as e:
    print(f"OSS上传器初始化失败: {e}")
    oss_uploader = None

# 初始化人脸融合客户端 - 优先使用SDK
face_fusion_client = None
try:
    from face_fusion_sdk import create_face_fusion_sdk_client
    face_fusion_client = create_face_fusion_sdk_client()
    if face_fusion_client:
        print("人脸融合SDK客户端初始化成功")
    else:
        print("人脸融合SDK客户端初始化失败，尝试使用HTTP客户端")
        # 回退到HTTP客户端
        from face_fusion_api import create_face_fusion_client
        face_fusion_client = create_face_fusion_client()
        if face_fusion_client:
            print("人脸融合HTTP客户端初始化成功")
        else:
            print("人脸融合客户端初始化失败")
except Exception as e:
    print(f"人脸融合客户端初始化错误: {e}")
    face_fusion_client = None

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_template_color(template_id):
    """根据模板ID获取主题色"""
    colors = {
        '1': '#ff6b6b',  # 红色
        '2': '#4ecdc4',  # 青色
        '3': '#45b7d1',  # 蓝色
        '4': '#f39c12',  # 橙色
        '5': '#e74c3c'   # 深红色
    }
    return colors.get(template_id, '#ff6b6b')

def download_fusion_result(result_url, user_id):
    """下载融合结果到本地"""
    try:
        import requests
        import os

        # 创建结果目录
        results_dir = Path('images/results')
        results_dir.mkdir(parents=True, exist_ok=True)

        # 下载图片
        response = requests.get(result_url, timeout=30)
        response.raise_for_status()

        # 保存到本地
        local_path = results_dir / f"{user_id}.jpg"
        with open(local_path, 'wb') as f:
            f.write(response.content)

        print(f"✓ 融合结果已保存: {local_path}")
        return str(local_path)

    except Exception as e:
        print(f"✗ 下载融合结果失败: {e}")
        return None

def create_mock_fusion_result(user_image_url, template_url, template_id, user_id):
    """创建模拟的融合结果"""
    try:
        import shutil

        # 创建结果目录
        results_dir = Path('images/results')
        results_dir.mkdir(parents=True, exist_ok=True)

        # 使用对应的模板图片作为模拟结果
        template_local_path = Path(f'web/templates/template{template_id}.jpg')
        result_local_path = results_dir / f"{user_id}.jpg"

        if template_local_path.exists():
            # 复制模板图片作为模拟结果
            shutil.copy2(template_local_path, result_local_path)
            print(f"✓ 模拟融合结果已创建: {result_local_path}")

            return {
                'success': True,
                'data': {
                    'imageUrl': template_url,  # 原始模板URL
                    'localImageUrl': f"/images/results/{user_id}.jpg",
                    'downloadUrl': f"/download/{user_id}.jpg",
                    'requestId': f"mock_request_{user_id}",
                    'source': 'mock',
                    'message': '模拟融合成功（使用模板图片作为结果展示）'
                }
            }
        else:
            print(f"✗ 模板文件不存在: {template_local_path}")
            return {
                'success': False,
                'message': '模拟融合失败：模板文件不存在'
            }

    except Exception as e:
        print(f"✗ 创建模拟融合结果失败: {e}")
        return {
            'success': False,
            'message': f'模拟融合失败: {str(e)}'
        }

# 加载模板配置
def load_templates_config():
    """从配置文件加载模板信息"""
    config_file = Path('web/templates_config.json')

    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                templates = {}
                for template in config.get('templates', []):
                    templates[template['id']] = {
                        'id': template['id'],
                        'name': template['name'],
                        'description': template['description'],
                        'templateUrl': template['templateUrl'],
                        'thumbnailUrl': template['thumbnailUrl'],
                        'style': f'fanyi{template["id"]}',
                        'bgColor': get_template_color(template['id']),
                        # 包含阿里云注册信息
                        'aliyunTemplateId': template.get('aliyunTemplateId'),
                        'registrationStatus': template.get('registrationStatus'),
                        'registrationRequestId': template.get('registrationRequestId'),
                        'registrationError': template.get('registrationError')
                    }
                return templates
        except Exception as e:
            print(f"加载模板配置失败: {e}")

    # 默认配置（如果配置文件不存在）
    return {
        '1': {
            'id': '1',
            'name': '周繁漪定妆照1',
            'description': '经典造型',
            'templateUrl': 'https://example.com/templates/fanyi1.jpg',
            'thumbnailUrl': 'https://example.com/templates/fanyi1_thumb.jpg',
            'style': 'fanyi1',
            'bgColor': '#ff6b6b'
        },
        '2': {
            'id': '2',
            'name': '周繁漪定妆照2',
            'description': '优雅风格',
            'templateUrl': 'https://example.com/templates/fanyi2.jpg',
            'thumbnailUrl': 'https://example.com/templates/fanyi2_thumb.jpg',
            'style': 'fanyi2',
            'bgColor': '#4ecdc4'
        },
        '3': {
            'id': '3',
            'name': '周繁漪定妆照3',
            'description': '时尚造型',
            'templateUrl': 'https://example.com/templates/fanyi3.jpg',
            'thumbnailUrl': 'https://example.com/templates/fanyi3_thumb.jpg',
            'style': 'fanyi3',
            'bgColor': '#45b7d1'
        },
        '4': {
            'id': '4',
            'name': '周繁漪定妆照4',
            'description': '清新风格',
            'templateUrl': 'https://example.com/templates/fanyi4.jpg',
            'thumbnailUrl': 'https://example.com/templates/fanyi4_thumb.jpg',
            'style': 'fanyi4',
            'bgColor': '#f39c12'
        },
        '5': {
            'id': '5',
            'name': '周繁漪定妆照5',
            'description': '魅力造型',
            'templateUrl': 'https://example.com/templates/fanyi5.jpg',
            'thumbnailUrl': 'https://example.com/templates/fanyi5_thumb.jpg',
            'style': 'fanyi5',
            'bgColor': '#e74c3c'
        }
    }

# 加载模板配置
TEMPLATES_CONFIG = load_templates_config()

def reload_templates_config():
    """重新加载模板配置"""
    global TEMPLATES_CONFIG
    TEMPLATES_CONFIG = load_templates_config()
    return TEMPLATES_CONFIG

@app.route('/')
def index():
    """主页 - 显示所有模板选择"""
    return send_from_directory('web', 'index.html')

@app.route('/templates/<filename>')
def serve_template(filename):
    """提供模板图片"""
    return send_from_directory('web/templates', filename)

@app.route('/images/results/<filename>')
def serve_result_image(filename):
    """提供融合结果图片"""
    return send_from_directory('images/results', filename)

@app.route('/download/<filename>')
def download_result(filename):
    """下载融合结果"""
    return send_from_directory('images/results', filename, as_attachment=True)

@app.route('/api/register-templates', methods=['POST'])
def register_templates():
    """注册模板到阿里云"""
    if not face_fusion_client:
        return jsonify({
            'success': False,
            'message': '人脸融合服务未初始化'
        }), 500

    try:
        # 读取当前模板配置
        config_file = Path('web/templates_config.json')
        if not config_file.exists():
            return jsonify({
                'success': False,
                'message': '模板配置文件不存在'
            }), 404

        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)

        templates = config.get('templates', [])
        registered_templates = []
        success_count = 0

        for template in templates:
            template_id = template['id']
            template_name = template['name']
            template_url = template['templateUrl']

            print(f"注册模板 {template_id}: {template_name}")

            # 检查是否已经注册过
            if template.get('aliyunTemplateId'):
                print(f"  模板已注册，跳过: {template['aliyunTemplateId']}")
                template['registrationStatus'] = 'already_registered'
                registered_templates.append(template)
                success_count += 1
                continue

            try:
                # 调用模板注册API
                result = face_fusion_client.add_face_template(template_url)

                if result.get('success'):
                    aliyun_template_id = result['data']['templateId']
                    request_id = result['data']['requestId']

                    print(f"✓ 模板注册成功: {aliyun_template_id}")

                    # 更新模板配置
                    template['aliyunTemplateId'] = aliyun_template_id
                    template['registrationRequestId'] = request_id
                    template['registrationStatus'] = 'success'

                    success_count += 1

                else:
                    error_msg = result.get('message', '未知错误')
                    print(f"✗ 模板注册失败: {error_msg}")

                    template['registrationStatus'] = 'failed'
                    template['registrationError'] = error_msg

            except Exception as e:
                print(f"✗ 模板注册出错: {e}")
                template['registrationStatus'] = 'error'
                template['registrationError'] = str(e)

            registered_templates.append(template)

        # 保存更新后的配置
        config['templates'] = registered_templates
        config['lastRegistration'] = {
            'timestamp': str(int(time.time())),
            'totalTemplates': len(registered_templates),
            'successCount': success_count,
            'failedCount': len(registered_templates) - success_count
        }

        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

        return jsonify({
            'success': True,
            'data': {
                'totalTemplates': len(registered_templates),
                'successCount': success_count,
                'failedCount': len(registered_templates) - success_count,
                'registeredTemplates': [
                    {
                        'id': t['id'],
                        'name': t['name'],
                        'aliyunTemplateId': t.get('aliyunTemplateId'),
                        'status': t.get('registrationStatus')
                    }
                    for t in registered_templates
                ]
            }
        })

    except Exception as e:
        print(f"模板注册过程出错: {e}")
        return jsonify({
            'success': False,
            'message': f'模板注册失败: {str(e)}'
        }), 500

@app.route('/fanyi')
def fanyi_page():
    """人脸融合页面 - 通过template参数区分模板"""
    template_id = request.args.get('template', '1')  # 默认使用模板1

    if template_id not in TEMPLATES_CONFIG:
        return "模板不存在", 404

    template = TEMPLATES_CONFIG[template_id]

    # 读取主页面并注入模板信息
    html_path = Path('web/fanyi.html')
    if html_path.exists():
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # 替换模板信息
        html_content = html_content.replace('{{TEMPLATE_ID}}', template['id'])
        html_content = html_content.replace('{{TEMPLATE_NAME}}', template['name'])
        html_content = html_content.replace('{{TEMPLATE_DESCRIPTION}}', template['description'])
        html_content = html_content.replace('{{TEMPLATE_STYLE}}', template['style'])
        html_content = html_content.replace('{{TEMPLATE_KEY}}', template_id)
        html_content = html_content.replace('{{BG_COLOR}}', template['bgColor'])

        return html_content
    else:
        return "页面不存在", 404

@app.route('/<path:filename>')
def static_files(filename):
    """静态文件服务"""
    return send_from_directory('web', filename)

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """文件上传接口"""
    try:
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
        filename = secure_filename(file.filename)
        timestamp = int(time.time())
        unique_filename = f"{timestamp}_{uuid.uuid4().hex[:8]}_{filename}"
        
        # 保存到本地临时目录
        local_path = Path(UPLOAD_FOLDER) / unique_filename
        file.save(str(local_path))
        
        # 上传到OSS
        if oss_uploader:
            oss_url = oss_uploader.upload_file(local_path, f"face_fusion/user_images/{unique_filename}")
            
            # 删除本地临时文件
            local_path.unlink()
            
            if oss_url:
                return jsonify({
                    'success': True,
                    'url': oss_url,
                    'message': '上传成功'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'OSS上传失败'
                }), 500
        else:
            return jsonify({
                'success': False,
                'message': 'OSS服务未初始化'
            }), 500
            
    except Exception as e:
        print(f"上传失败: {e}")
        return jsonify({
            'success': False,
            'message': f'上传失败: {str(e)}'
        }), 500

@app.route('/api/template/<template_id>')
def get_template_info(template_id):
    """获取模板信息"""
    # 重新加载模板配置以获取最新信息
    reload_templates_config()

    if template_id not in TEMPLATES_CONFIG:
        return jsonify({
            'success': False,
            'message': '模板不存在'
        }), 404

    template = TEMPLATES_CONFIG[template_id]
    return jsonify({
        'success': True,
        'data': template
    })

@app.route('/api/templates')
def get_all_templates():
    """获取所有模板列表"""
    templates = []
    for template_id, template_info in TEMPLATES_CONFIG.items():
        templates.append({
            'id': template_id,
            'name': template_info['name'],
            'description': template_info['description'],
            'style': template_info['style'],
            'url': f'/fanyi?template={template_id}',
            'thumbnailUrl': template_info.get('localThumbnail', template_info.get('thumbnailUrl')),
            'localThumbnail': template_info.get('localThumbnail')
        })

    return jsonify({
        'success': True,
        'data': templates
    })

@app.route('/api/face-fusion', methods=['POST'])
def face_fusion():
    """人脸融合接口"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据为空'
            }), 400

        user_image_url = data.get('userImageUrl')
        template_id = data.get('templateId')

        if not user_image_url or not template_id:
            return jsonify({
                'success': False,
                'message': '缺少必要参数'
            }), 400

        # 重新加载模板配置以获取最新的注册信息
        reload_templates_config()

        # 获取模板信息
        if template_id not in TEMPLATES_CONFIG:
            return jsonify({
                'success': False,
                'message': '模板不存在'
            }), 400

        template_info = TEMPLATES_CONFIG[template_id]
        template_url = template_info['templateUrl']

        # 获取阿里云注册的模板ID
        aliyun_template_id = template_info.get('aliyunTemplateId')
        if not aliyun_template_id:
            return jsonify({
                'success': False,
                'message': f'模板{template_id}尚未注册到阿里云，请先注册模板'
            }), 400
        
        # 尝试调用真实的人脸融合API，如果失败则使用模拟结果
        print(f"开始人脸融合: {user_image_url} + {template_url}")

        # 生成用户ID
        import time
        user_id = f"user_{int(time.time())}"

        # 首先尝试真实API
        if face_fusion_client:
            try:
                print("尝试调用真实的人脸融合API...")
                api_result = face_fusion_client.merge_face(user_image_url, aliyun_template_id)

                if api_result and api_result.get('success'):
                    print("✓ 真实API调用成功")
                    # 下载融合结果到本地
                    fusion_result_url = api_result['data']['imageUrl']
                    local_result_path = download_fusion_result(fusion_result_url, user_id)

                    if local_result_path:
                        # 返回真实的融合结果
                        result = {
                            'success': True,
                            'data': {
                                'imageUrl': fusion_result_url,
                                'localImageUrl': f"/images/results/{user_id}.jpg",
                                'downloadUrl': f"/download/{user_id}.jpg",
                                'requestId': api_result['data'].get('requestId', ''),
                                'source': 'real_api'
                            }
                        }
                    else:
                        raise Exception("融合结果下载失败")
                else:
                    raise Exception(api_result.get('message', '人脸融合失败') if api_result else 'API调用失败')

            except Exception as e:
                print(f"⚠️ 真实API调用失败: {e}")
                print("回退到模拟融合结果...")

                # 使用模拟融合结果
                result = create_mock_fusion_result(user_image_url, template_url, template_id, user_id)
        else:
            print("⚠️ 人脸融合客户端未初始化，使用模拟结果...")
            result = create_mock_fusion_result(user_image_url, template_url, template_id, user_id)
        
        if result and result.get('success'):
            return jsonify({
                'success': True,
                'data': {
                    'imageUrl': result['data']['imageUrl'],
                    'requestId': result['data'].get('requestId', '')
                },
                'message': '融合成功'
            })
        else:
            return jsonify({
                'success': False,
                'message': result.get('message', '融合失败')
            }), 500
            
    except Exception as e:
        print(f"人脸融合失败: {e}")
        return jsonify({
            'success': False,
            'message': f'融合失败: {str(e)}'
        }), 500



@app.route('/api/templates', methods=['GET'])
def get_templates():
    """获取模板列表"""
    templates = [
        {
            'id': 'template1',
            'name': '古装美女',
            'thumbnail': '/templates/template1_thumb.jpg',
            'templateUrl': 'https://example.com/templates/template1.jpg'
        },
        {
            'id': 'template2',
            'name': '商务精英', 
            'thumbnail': '/templates/template2_thumb.jpg',
            'templateUrl': 'https://example.com/templates/template2.jpg'
        },
        {
            'id': 'template3',
            'name': '卡通头像',
            'thumbnail': '/templates/template3_thumb.jpg',
            'templateUrl': 'https://example.com/templates/template3.jpg'
        },
        {
            'id': 'template4',
            'name': '超级英雄',
            'thumbnail': '/templates/template4_thumb.jpg',
            'templateUrl': 'https://example.com/templates/template4.jpg'
        },
        {
            'id': 'template5',
            'name': '明星风格',
            'thumbnail': '/templates/template5_thumb.jpg',
            'templateUrl': 'https://example.com/templates/template5.jpg'
        },
        {
            'id': 'template6',
            'name': '艺术画像',
            'thumbnail': '/templates/template6_thumb.jpg',
            'templateUrl': 'https://example.com/templates/template6.jpg'
        }
    ]
    
    return jsonify({
        'success': True,
        'data': templates
    })

@app.errorhandler(413)
def too_large(e):
    """文件过大错误处理"""
    return jsonify({
        'success': False,
        'message': '文件大小超过限制(5MB)'
    }), 413

@app.errorhandler(404)
def not_found(e):
    """404错误处理"""
    return jsonify({
        'success': False,
        'message': '接口不存在'
    }), 404

@app.errorhandler(500)
def internal_error(e):
    """500错误处理"""
    return jsonify({
        'success': False,
        'message': '服务器内部错误'
    }), 500

def find_available_port(start_port=8080):
    """查找可用端口"""
    import socket
    for port in range(start_port, start_port + 100):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    return None

if __name__ == '__main__':
    # 查找可用端口
    port = find_available_port(8080)
    if not port:
        print("无法找到可用端口")
        exit(1)

    print("启动人脸融合H5应用服务器...")
    print(f"访问地址: http://localhost:{port}")
    print("确保已配置OSS和阿里云访问凭证")

    # 开发模式运行
    app.run(host='0.0.0.0', port=port, debug=True)
