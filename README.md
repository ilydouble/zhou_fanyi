# LivePortrait 视频生成器

这个项目使用阿里云的LivePortrait API来检测图像质量并生成人像动态视频。

## 功能特性

- 自动检测 `pics` 文件夹下的图片质量
- 对通过检测的图片生成人像动态视频
- 使用 `sound/qiezi.wav` 作为音频源
- 生成的视频保存到 `videos` 文件夹

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置

1. 确保 `.env` 文件中包含你的阿里云API密钥和OSS配置：
```
ALIYUN_API_KEY=your_api_key_here

# OSS配置
OSS_ACCESS_KEY_ID=your_access_key_id
OSS_ACCESS_KEY_SECRET=your_access_key_secret
OSS_BUCKET_NAME=your_bucket_name
OSS_ENDPOINT=oss-cn-beijing.aliyuncs.com
OSS_BASE_PATH=liveportrait
```

2. 确保以下目录结构存在：
```
├── pics/          # 放置要处理的图片
├── sound/         # 包含 qiezi.wav 音频文件
├── videos/        # 生成的视频输出目录
├── .env           # API密钥配置
└── video_generator.py  # 主程序
```

## 使用方法

### 快速开始

1. 将要处理的图片放入 `pics` 文件夹
2. 确保 `sound/qiezi.wav` 文件存在
3. 运行环境测试：
```bash
python test_setup.py
```

4. 运行主程序：
```bash
python video_generator.py
```

### 演示模式

运行完整的演示流程（OSS版本）：
```bash
python demo_oss.py
```

或运行本地版本（需要可公网访问的服务器）：
```bash
python demo.py
```

### 自定义配置

编辑 `config.py` 文件来自定义参数：
- 视频生成参数（帧率、动作幅度等）
- 文件路径配置
- 服务器端口设置

## 支持的文件格式

### 图片格式
- JPEG (.jpg, .jpeg)
- PNG (.png)
- BMP (.bmp)
- WebP (.webp)

### 音频格式
- WAV (.wav)
- MP3 (.mp3)

## 图片要求

- 文件大小 < 10MB
- 宽高比 ≤ 2
- 最大边长 ≤ 4096像素
- 必须包含清晰的人脸

## 音频要求

- 文件大小 < 15MB
- 时长：1秒 < 时长 < 5分钟
- 需包含清晰、响亮的人声
- 去除环境噪音和背景音乐

## 工作流程

1. **文件上传**：自动上传图片和音频到阿里云OSS，生成签名URL
2. **图片质量检测**：使用 `liveportrait-detect` 模型检测图片是否符合要求
3. **视频生成**：对通过检测的图片使用 `liveportrait` 模型生成动态视频
4. **任务监控**：监控异步任务状态直到完成
5. **结果下载**：下载生成的视频到本地

## 技术特点

### 🔐 签名URL安全访问
- 使用OSS签名URL技术，支持私有Bucket
- 自动生成24小时有效期的签名链接
- 无需公开Bucket权限，保护文件安全

### ⚡ 自动化流程
- 自动上传文件到OSS对象存储
- 智能文件分类（图片/音频）
- 异步任务状态监控
- 自动结果下载

## 注意事项

- 文件会自动上传到阿里云OSS对象存储
- 签名URL有效期为24小时，足够API处理使用
- 视频生成是异步过程，可能需要几分钟时间
- 生成的视频文件名格式：`{原图片名}_generated.mp4`
- 如果图片质量检测不通过，会跳过该图片并记录原因

## 错误处理

程序包含完整的错误处理和日志记录：
- 网络请求错误
- API调用错误
- 文件操作错误
- 任务超时处理

## 日志输出

程序会输出详细的日志信息，包括：
- 处理进度
- 检测结果
- 任务状态
- 错误信息

## API限制

请注意阿里云API的使用限制和计费规则。详细信息请参考：
- [LivePortrait图像检测API参考](docs/LivePortrait图像检测API参考.md)
- [LivePortrait视频生成API参考](docs/LivePortrait%20视频生成API参考.md)
