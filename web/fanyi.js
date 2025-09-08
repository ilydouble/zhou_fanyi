class FanyiFusionApp {
    constructor() {
        this.uploadedImage = null;
        this.resultImageUrl = null;
        this.templateId = TEMPLATE_ID;
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.checkCameraSupport();
        this.loadTemplateInfo();
    }
    
    async loadTemplateInfo() {
        try {
            const response = await fetch(`/api/template/${this.templateId}`);
            const result = await response.json();

            if (result.success) {
                this.templateInfo = result.data;
                console.log('模板信息加载成功:', this.templateInfo);
                this.displayTemplatePreview();
            } else {
                this.showToast('模板信息加载失败');
            }
        } catch (error) {
            console.error('加载模板信息失败:', error);
            this.showToast('模板信息加载失败');
        }
    }

    displayTemplatePreview() {
        if (!this.templateInfo) return;

        const previewImage = document.getElementById('templatePreview');
        const previewName = document.getElementById('templatePreviewName');
        const previewDesc = document.getElementById('templatePreviewDesc');

        // 设置模板信息
        previewName.textContent = this.templateInfo.name;
        previewDesc.textContent = this.templateInfo.description;

        // 设置模板缩略图
        const thumbnailUrl = this.templateInfo.localThumbnail || this.templateInfo.thumbnailUrl;

        if (thumbnailUrl && thumbnailUrl.startsWith('/templates/')) {
            // 使用本地缩略图
            previewImage.src = thumbnailUrl;
            previewImage.onerror = () => {
                // 本地图片失败，尝试OSS
                if (this.templateInfo.thumbnailUrl && !this.templateInfo.thumbnailUrl.includes('example.com')) {
                    previewImage.src = this.templateInfo.thumbnailUrl;
                } else {
                    // 显示占位符
                    previewImage.style.display = 'none';
                    previewImage.parentNode.innerHTML = `
                        <div style="width: 80px; height: 80px; background: #ddd; border-radius: 8px; display: flex; align-items: center; justify-content: center; margin-right: 15px; color: #999; font-size: 12px;">
                            周繁漪
                        </div>
                        <div class="template-preview-info">
                            <div class="template-preview-name">${this.templateInfo.name}</div>
                            <div class="template-preview-desc">${this.templateInfo.description}</div>
                        </div>
                    `;
                }
            };
        } else if (this.templateInfo.thumbnailUrl && !this.templateInfo.thumbnailUrl.includes('example.com')) {
            // 使用OSS缩略图
            previewImage.src = this.templateInfo.thumbnailUrl;
        } else {
            // 显示占位符
            previewImage.style.display = 'none';
            previewImage.parentNode.innerHTML = `
                <div style="width: 80px; height: 80px; background: #ddd; border-radius: 8px; display: flex; align-items: center; justify-content: center; margin-right: 15px; color: #999; font-size: 12px;">
                    周繁漪
                </div>
                <div class="template-preview-info">
                    <div class="template-preview-name">${this.templateInfo.name}</div>
                    <div class="template-preview-desc">${this.templateInfo.description}</div>
                </div>
            `;
        }
    }
    
    bindEvents() {
        // 文件上传
        const fileInput = document.getElementById('fileInput');
        const uploadArea = document.getElementById('uploadArea');
        const generateBtn = document.getElementById('generateBtn');
        const saveBtn = document.getElementById('saveBtn');
        const shareBtn = document.getElementById('shareBtn');
        const resetBtn = document.getElementById('resetBtn');
        
        // 点击上传区域
        uploadArea.addEventListener('click', () => {
            fileInput.click();
        });
        
        // 文件选择
        fileInput.addEventListener('change', (e) => {
            this.handleFileSelect(e.target.files[0]);
        });
        
        // 拖拽上传
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });
        
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            this.handleFileSelect(e.dataTransfer.files[0]);
        });
        
        // 生成按钮
        generateBtn.addEventListener('click', () => {
            this.generateFusion();
        });
        
        // 保存按钮
        saveBtn.addEventListener('click', () => {
            this.saveToLocal();
        });
        
        // 分享按钮
        shareBtn.addEventListener('click', () => {
            this.shareToWechat();
        });
        
        // 重置按钮
        resetBtn.addEventListener('click', () => {
            this.reset();
        });
    }
    
    checkCameraSupport() {
        // 检查是否支持摄像头
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            console.log('支持摄像头拍照');
        }
    }
    
    handleFileSelect(file) {
        if (!file) return;
        
        // 检查文件类型
        if (!file.type.startsWith('image/')) {
            this.showToast('请选择图片文件');
            return;
        }
        
        // 检查文件大小 (5MB)
        if (file.size > 5 * 1024 * 1024) {
            this.showToast('图片大小不能超过5MB');
            return;
        }
        
        // 显示预览
        const reader = new FileReader();
        reader.onload = (e) => {
            const previewImage = document.getElementById('previewImage');
            previewImage.src = e.target.result;
            previewImage.classList.remove('hidden');
            
            // 隐藏上传提示
            document.querySelector('.upload-icon').style.display = 'none';
            document.querySelector('.upload-text').style.display = 'none';
            document.querySelector('.upload-hint').style.display = 'none';
        };
        reader.readAsDataURL(file);
        
        this.uploadedImage = file;
        this.updateGenerateButton();
        this.showToast('照片上传成功');
    }
    
    updateGenerateButton() {
        const generateBtn = document.getElementById('generateBtn');
        generateBtn.disabled = !this.uploadedImage;
    }
    
    async generateFusion() {
        if (!this.uploadedImage) {
            this.showToast('请先上传照片');
            return;
        }
        
        // 显示加载状态
        this.showLoading(true);
        
        try {
            // 1. 上传用户照片到OSS
            const userImageUrl = await this.uploadToOSS(this.uploadedImage);
            if (!userImageUrl) {
                throw new Error('照片上传失败');
            }
            
            // 2. 调用人脸融合API
            const result = await this.callFaceFusionAPI(userImageUrl, this.templateId);
            if (!result || !result.imageUrl) {
                throw new Error('人脸融合失败');
            }
            
            // 3. 显示结果
            const resultImageUrl = result.localImageUrl || result.imageUrl;
            this.showResult(resultImageUrl, result.downloadUrl);
            this.showToast('融合完成！');
            
        } catch (error) {
            console.error('融合失败:', error);
            this.showToast('融合失败，请重试');
        } finally {
            this.showLoading(false);
        }
    }
    
    async uploadToOSS(file) {
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            if (result.success) {
                return result.url;
            } else {
                throw new Error(result.message || '上传失败');
            }
        } catch (error) {
            console.error('上传失败:', error);
            return null;
        }
    }
    
    async callFaceFusionAPI(userImageUrl, templateId) {
        try {
            const response = await fetch('/api/face-fusion', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    userImageUrl: userImageUrl,
                    templateId: templateId
                })
            });
            
            const result = await response.json();
            if (result.success) {
                return {
                    imageUrl: result.data.imageUrl,
                    localImageUrl: result.data.localImageUrl,
                    downloadUrl: result.data.downloadUrl
                };
            } else {
                throw new Error(result.message || '融合失败');
            }
        } catch (error) {
            console.error('API调用失败:', error);
            return null;
        }
    }
    
    showResult(imageUrl, downloadUrl) {
        this.resultImageUrl = imageUrl;
        this.downloadUrl = downloadUrl;

        const resultImage = document.getElementById('resultImage');
        const resultSection = document.getElementById('resultSection');

        resultImage.src = imageUrl;
        resultSection.style.display = 'block';

        // 滚动到结果区域
        resultSection.scrollIntoView({ behavior: 'smooth' });
    }
    
    saveToLocal() {
        if (!this.downloadUrl && !this.resultImageUrl) return;

        // 优先使用下载URL，否则使用结果图片URL
        const downloadLink = this.downloadUrl || this.resultImageUrl;

        // 创建下载链接
        const link = document.createElement('a');
        link.href = downloadLink;
        link.download = `fanyi_fusion_${Date.now()}.jpg`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        this.showToast('图片已保存到相册');
    }
    
    shareToWechat() {
        if (!this.resultImageUrl) return;
        
        // 检查是否在微信环境
        const isWechat = /micromessenger/i.test(navigator.userAgent);
        
        if (isWechat) {
            // 在微信中，显示分享提示
            this.showShareGuide();
        } else {
            // 非微信环境，复制链接
            this.copyToClipboard(this.resultImageUrl);
            this.showToast('链接已复制，可在微信中分享');
        }
    }
    
    showShareGuide() {
        // 创建分享引导遮罩
        const overlay = document.createElement('div');
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.8);
            z-index: 9999;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            text-align: center;
            font-size: 18px;
            padding: 20px;
        `;
        
        overlay.innerHTML = `
            <div>
                <div style="margin-bottom: 20px;">📱</div>
                <div>点击右上角菜单</div>
                <div>选择"分享到朋友圈"</div>
                <div style="margin-top: 30px; font-size: 14px; opacity: 0.7;">点击任意位置关闭</div>
            </div>
        `;
        
        overlay.addEventListener('click', () => {
            document.body.removeChild(overlay);
        });
        
        document.body.appendChild(overlay);
    }
    
    copyToClipboard(text) {
        if (navigator.clipboard) {
            navigator.clipboard.writeText(text);
        } else {
            // 兼容性方案
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
        }
    }
    
    reset() {
        // 重置所有状态
        this.uploadedImage = null;
        this.resultImageUrl = null;
        
        // 重置UI
        const previewImage = document.getElementById('previewImage');
        previewImage.classList.add('hidden');
        previewImage.src = '';
        
        // 显示上传提示
        document.querySelector('.upload-icon').style.display = 'block';
        document.querySelector('.upload-text').style.display = 'block';
        document.querySelector('.upload-hint').style.display = 'block';
        
        // 隐藏结果
        document.getElementById('resultSection').style.display = 'none';
        
        // 重置按钮状态
        this.updateGenerateButton();
        
        // 滚动到顶部
        window.scrollTo({ top: 0, behavior: 'smooth' });
        
        this.showToast('已重置，可以重新制作');
    }
    
    showLoading(show) {
        const loading = document.getElementById('loading');
        const generateBtn = document.getElementById('generateBtn');
        
        if (show) {
            loading.style.display = 'block';
            generateBtn.disabled = true;
            generateBtn.textContent = '处理中...';
        } else {
            loading.style.display = 'none';
            generateBtn.disabled = false;
            generateBtn.textContent = '🎨 开始融合';
            this.updateGenerateButton();
        }
    }
    
    showToast(message) {
        const toast = document.getElementById('toast');
        toast.textContent = message;
        toast.classList.add('show');
        
        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }
}

// 初始化应用
document.addEventListener('DOMContentLoaded', () => {
    new FanyiFusionApp();
});
