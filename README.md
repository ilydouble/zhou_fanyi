# 🎭 周繁漪AI人脸融合项目

基于周繁漪定妆照的真实AI人脸融合Web应用，使用阿里云人脸融合API实现高质量的人脸融合效果。

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置环境变量
创建 `.env` 文件：
```env
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

### 3. 上传并注册模板
```bash
# 上传模板到OSS
python simple_upload.py

# 启动服务器
python web_server.py

# 注册模板到阿里云（在另一个终端）
curl -X POST http://localhost:8081/api/register-templates
```

### 4. 访问应用
- 主页: http://localhost:8081/
- 手机访问: http://192.168.1.24:8081

## 📁 项目结构

```
zhou_fanyi/
├── web/                    # 前端文件
│   ├── index.html         # 主页面 - 模板选择
│   ├── fanyi.html         # 融合页面 - AI人脸融合
│   ├── app.js             # 主页逻辑
│   ├── fanyi.js           # 融合页逻辑
│   └── templates_config.json  # 模板配置（含阿里云模板ID）
├── pics/                  # 周繁漪定妆照原图
├── images/results/        # 融合结果保存目录
├── web_server.py          # Flask后端服务
├── face_fusion_sdk.py     # 阿里云人脸融合SDK
├── oss_uploader.py        # OSS文件上传
├── simple_upload.py       # 模板上传脚本
└── 二维码生成器.html      # 二维码生成工具
```

## ✨ 功能特性

- 🤖 **真实AI人脸融合** - 阿里云专业API，效果自然逼真
- 🎨 **5种周繁漪定妆照** - 已注册为阿里云官方模板
- 📱 **移动端优化** - 响应式设计，支持拍照上传
- ⚡ **即时处理** - 几秒钟内获得融合结果
- 💾 **自动保存** - 结果自动下载到本地
- 🔗 **直链访问** - 支持通过URL直接访问特定模板
- 📱 **二维码分享** - 内置二维码生成器，方便分享

## 🔗 访问路由

- 主页: `/`
- 定妆照1: `/fanyi?template=1`
- 定妆照2: `/fanyi?template=2`
- 定妆照3: `/fanyi?template=3`
- 定妆照4: `/fanyi?template=4`
- 定妆照5: `/fanyi?template=5`

## 📊 当前状态

- ✅ **模板系统** - 5个周繁漪定妆照已上传并注册
- ✅ **阿里云集成** - 真实人脸融合API已接入
- ✅ **文件上传** - OSS集成完成
- ✅ **前端界面** - 响应式设计，移动端优化
- ✅ **人脸融合** - 真实AI融合功能已实现
- ✅ **结果处理** - 自动下载和本地保存

## 🛠️ 工具文件

- **二维码生成器.html** - 为应用生成分享二维码
- **web/README.md** - 详细的使用文档和API说明

## 🎯 核心技术

- **阿里云人脸融合API** - 专业AI服务
- **OSS云存储** - 文件上传和管理
- **Flask Web框架** - 后端API服务
- **响应式前端** - 移动端优化

## 📞 技术支持

详细文档请查看 `web/README.md`

## 📄 许可证

MIT License
