# 模板图片目录

这个目录用于存放人脸融合的模板图片。

## 文件结构

```
templates/
├── template1.jpg          
├── template1_thumb.jpg    
├── template2.jpg          
├── template2_thumb.jpg    
├── template3.jpg          
├── template3_thumb.jpg    
├── template4.jpg          
├── template4_thumb.jpg    
├── template5.jpg          
├── template5_thumb.jpg    
├── template6.jpg          
└── template6_thumb.jpg    
```

## 图片要求

### 模板图片 (template*.jpg)
- 分辨率：建议 512x512 或更高
- 格式：JPG、PNG
- 大小：< 5MB
- 内容：包含清晰的人脸，适合融合

### 缩略图 (template*_thumb.jpg)
- 分辨率：建议 200x200
- 格式：JPG、PNG
- 大小：< 500KB
- 内容：模板的缩略版本，用于前端展示

## 添加新模板

1. 准备模板图片和缩略图
2. 按照命名规范放入此目录
3. 在 `web_server.py` 的 `get_templates()` 函数中添加新模板配置
4. 在 `web/app.js` 的模板配置中添加对应项

## 注意事项

- 模板图片应该包含清晰的正脸
- 避免过度化妆或特效
- 确保图片版权合规
- 建议提供多种风格的模板供用户选择
