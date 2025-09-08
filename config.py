#!/usr/bin/env python3
"""
配置文件：LivePortrait 视频生成器的参数配置
"""

# 文件路径配置
PICS_DIR = "pics"                    # 输入图片目录
SOUND_FILE = "sound/qiezi2.wav"       # 音频文件路径
VIDEOS_DIR = "videos"                # 输出视频目录
TEMPLATES_DIR = "web/templates"      # 模板目录

# 文件服务器配置
FILE_SERVER_PORT = 8000              # 本地文件服务器端口

# 缩略图配置
THUMBNAIL_SIZE = (200, 200)          # 缩略图尺寸
THUMBNAIL_QUALITY = 85               # 缩略图质量 (1-100)

# 视频二维码合成配置
QR_SIZE = 120                        # 二维码大小（像素）
QR_MARGIN = 20                       # 距离边缘的边距
QR_OPACITY = 0.9                     # 二维码透明度 (0-1)
VIDEOS_WITH_QR_DIR = "videos_with_qr" # 合成视频输出目录

# 视频生成参数
VIDEO_GENERATION_PARAMS = {
    "template_id": "normal",         # 动作模板: normal, calm, active
    "eye_move_freq": 0.5,           # 眨眼频率 (0-1)
    "video_fps": 24,                # 视频帧率 (15-30)
    "mouth_move_strength": 0.7,     # 嘴部动作幅度 (0-1.5)
    "paste_back": True,             # 是否贴回原图
    "head_move_strength": 0.5       # 头部动作幅度 (0-1)
}

# 任务配置
MAX_WAIT_TIME = 600                 # 最大等待时间（秒）
QUERY_INTERVAL = 10                 # 状态查询间隔（秒）

# 支持的文件格式
SUPPORTED_IMAGE_FORMATS = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}
SUPPORTED_AUDIO_FORMATS = {'.wav', '.mp3'}

# API端点
API_ENDPOINTS = {
    'detect': 'https://dashscope.aliyuncs.com/api/v1/services/aigc/image2video/face-detect',
    'video_synthesis': 'https://dashscope.aliyuncs.com/api/v1/services/aigc/image2video/video-synthesis/',
    'task_query': 'https://dashscope.aliyuncs.com/api/v1/tasks'
}

# 日志配置
LOG_LEVEL = "INFO"                  # 日志级别: DEBUG, INFO, WARNING, ERROR
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
