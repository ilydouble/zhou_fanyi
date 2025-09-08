# 🎭 周繁漪AI人脸融合项目

基于周繁漪定妆照的AI人脸融合和视频生成项目，包含两个主要功能：
1. **LivePortrait视频生成** - 基于定妆照生成AI口型同步视频
2. **人脸融合Web应用** - 微信H5页面，实现用户照片与定妆照的人脸融合

## 📁 项目结构

```
zhou_fanyi/
├── pics/                      # 6张周繁漪定妆照原图
│   ├── fanyi-1.jpg           # 定妆照1
│   ├── fanyi-2.jpeg          # 定妆照2
│   ├── fanyi-3.jpeg          # 定妆照3
│   ├── fanyi-4.jpeg          # 定妆照4
│   ├── fanyi-5.jpeg          # 定妆照5
│   └── fanyi-6.jpeg          # 定妆照6
├── sound/                     # 音频文件
│   ├── qiezi.wav             # 音频文件1
│   └── qiezi2.wav            # 音频文件2
├── videos/                    # 生成的视频输出目录
├── web/                       # Web应用前端
│   ├── templates/            # 模板图片目录
│   ├── index.html           # 主页面 - 模板选择
│   ├── fanyi-wechat.html    # 微信版人脸融合页面
│   ├── app.js               # 主页逻辑
│   └── templates_config.json # 模板配置文件
├── config.py                  # 项目配置文件
├── video_generator.py         # LivePortrait视频生成主程序
├── generate_templates.py      # 模板生成脚本
├── web_server.py             # Flask Web服务器
├── face_fusion_sdk.py        # 阿里云人脸融合SDK
├── oss_uploader.py           # OSS文件上传工具
└── demo.py                   # 演示脚本
```

## 🚀 使用方法

### 1. 环境准备

#### 安装依赖
```bash
pip install -r requirements.txt
```

#### 配置环境变量
创建 `.env` 文件：
```env
# 阿里云API密钥（LivePortrait视频生成）
ALIYUN_API_KEY=your_dashscope_api_key

# 阿里云API密钥（人脸融合服务）
ALIYUN_ACCESS_KEY_ID=your_access_key_id
ALIYUN_ACCESS_KEY_SECRET=your_access_key_secret

# OSS配置（上海区域）
OSS_ACCESS_KEY_ID=your_access_key_id
OSS_ACCESS_KEY_SECRET=your_access_key_secret
OSS_BUCKET_NAME=your_bucket_name
OSS_ENDPOINT=oss-cn-shanghai.aliyuncs.com
OSS_BASE_PATH=liveportrait
```

### 2. LivePortrait视频生成

#### 配置参数
项目配置在 `config.py` 中定义：
```python
# 文件路径配置
PICS_DIR = "pics"                    # 输入图片目录（6张定妆照）
SOUND_FILE = "sound/qiezi2.wav"      # 音频文件路径
VIDEOS_DIR = "videos"                # 输出视频目录

# 视频生成参数
VIDEO_GENERATION_PARAMS = {
    "template_id": "normal",         # 动作模板: normal, calm, active
    "eye_move_freq": 0.5,           # 眨眼频率 (0-1)
    "video_fps": 24,                # 视频帧率 (15-30)
    "mouth_move_strength": 1.0,     # 嘴部动作幅度 (0-1.5)
    "paste_back": True,             # 是否贴回原图
    "head_move_strength": 0.7       # 头部动作幅度 (0-1)
}
```

#### 生成视频
```bash
# 直接运行主程序
python video_generator.py

# 或使用演示脚本（包含环境检查）
python demo.py
```

程序会：
1. 自动检测 `pics/` 目录下的6张定妆照
2. 对每张图片进行质量检测
3. 使用 `sound/qiezi2.wav` 作为音频源
4. 生成口型同步视频到 `videos/` 目录

### 3. 生成Web模板

将 `pics/` 目录下的定妆照拷贝到 `web/templates/` 目录并生成缩略图：

```bash
python generate_templates.py
```

此脚本会：
1. 将 `pics/fanyi-*.jpg` 拷贝到 `web/templates/template*.jpg`
2. 生成对应的缩略图 `template*_thumb.jpg` (200x200像素)
3. 自动转换图片格式为JPG
4. 清理旧的模板文件

### 4. Web应用部署

#### 上传模板到OSS
```bash
python simple_upload.py
```

#### 启动Web服务器
```bash
python web_server.py
```

服务器将在 `http://localhost:8081` 启动

#### 注册模板到阿里云
```bash
curl -X POST http://localhost:8081/api/register-templates
```

## 📱 Web应用使用

### 访问方式

#### 桌面端访问
- 主页: http://localhost:8081/
- 直接访问模板: http://localhost:8081/fanyi-wechat?template=1

#### 微信中访问
1. 将服务器部署到公网（如使用域名 `yyts.top`）
2. 在微信中打开: https://yyts.top/
3. 选择喜欢的定妆照风格
4. 拍照或上传照片
5. 等待AI人脸融合完成
6. 保存或分享结果

### 功能特性

- 🎨 **6种周繁漪定妆照** - 不同造型风格选择
- 📱 **微信优化** - 支持微信内拍照和相册选择
- 🤖 **真实AI人脸融合** - 阿里云专业API，效果自然逼真
- ⚡ **即时处理** - 几秒钟内获得融合结果
- 💾 **自动保存** - 结果可保存到相册或分享朋友圈
- 📱 **响应式设计** - 适配各种屏幕尺寸

### 访问路由

- 主页: `/`
- 定妆照1: `/fanyi-wechat?template=1`
- 定妆照2: `/fanyi-wechat?template=2`
- 定妆照3: `/fanyi-wechat?template=3`
- 定妆照4: `/fanyi-wechat?template=4`
- 定妆照5: `/fanyi-wechat?template=5`
- 定妆照6: `/fanyi-wechat?template=6`

## 🛠️ 工具文件

- **docs/二维码生成器.html** - 为应用生成分享二维码
- **web/README.md** - 详细的Web应用文档和API说明
- **test_setup.py** - 环境配置测试脚本

## 🎯 核心技术

- **阿里云DashScope API** - LivePortrait视频生成
- **阿里云人脸融合API** - 专业AI人脸融合服务
- **OSS云存储** - 文件上传和管理
- **Flask Web框架** - 后端API服务
- **响应式前端** - 移动端和微信优化

## 📞 技术支持

- 详细Web应用文档: `web/README.md`
- API参考文档: `docs/` 目录
- 视频生成配置: `config.py`

## 📄 许可证

MIT License
