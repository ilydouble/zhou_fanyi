class FaceFusionApp {
    constructor() {
        this.templates = [];
        this.init();
    }

    init() {
        this.loadTemplates();
        this.bindEvents();
    }

    async loadTemplates() {
        try {
            const response = await fetch('/api/templates');
            const result = await response.json();

            if (result.success) {
                this.templates = result.data;
                this.renderTemplates();
            } else {
                this.showToast('模板加载失败');
            }
        } catch (error) {
            console.error('加载模板失败:', error);
            this.showToast('模板加载失败');
        }
    }

    renderTemplates() {
        const templateGrid = document.getElementById('templateGrid');
        templateGrid.innerHTML = '';

        this.templates.forEach(template => {
            const templateItem = document.createElement('div');
            templateItem.className = 'template-item';
            templateItem.dataset.templateId = template.id;

            // 创建模板卡片
            templateItem.innerHTML = `
                <div class="template-card">
                    ${this.createTemplateImage(template)}
                    <div class="template-overlay">
                        <div class="template-name">${template.name}</div>
                        <div class="template-desc">${template.description}</div>
                    </div>
                </div>
            `;

            templateItem.addEventListener('click', () => {
                window.location.href = template.url;
            });

            templateGrid.appendChild(templateItem);
        });
    }

    createTemplateImage(template) {
        // 优先使用本地缩略图，如果失败则使用OSS URL，最后使用占位符
        const localThumbnail = `/templates/template${template.id}.jpg`;
        const fallbackUrl = template.thumbnailUrl;

        // 检查是否有本地缩略图
        if (template.localThumbnail || this.hasLocalThumbnail(template.id)) {
            // 使用本地缩略图，失败时回退到OSS URL
            if (fallbackUrl && !fallbackUrl.includes('example.com')) {
                return `<img class="template-image" src="${localThumbnail}" alt="${template.name}" onerror="this.src='${fallbackUrl}'; this.onerror=function(){this.parentNode.innerHTML='<div class=&quot;template-placeholder&quot;>周繁漪<br>${template.name}</div>';}">`;
            } else {
                return `<img class="template-image" src="${localThumbnail}" alt="${template.name}" onerror="this.parentNode.innerHTML='<div class=&quot;template-placeholder&quot;>周繁漪<br>${template.name}</div>'">`;
            }
        } else if (template.thumbnailUrl && !template.thumbnailUrl.includes('example.com')) {
            // 直接使用OSS缩略图
            return `<img class="template-image" src="${template.thumbnailUrl}" alt="${template.name}" onerror="this.parentNode.innerHTML='<div class=\\"template-placeholder\\">周繁漪<br>${template.name}</div>'">`;
        } else {
            // 使用占位符
            return `<div class="template-placeholder">周繁漪<br>${template.name}</div>`;
        }
    }

    hasLocalThumbnail(templateId) {
        // 检查本地是否存在缩略图文件
        // 这里简单返回true，假设本地缩略图都存在
        // 实际项目中可以通过AJAX请求检查文件是否存在
        return true;
    }

    getTemplateColor(style) {
        const colors = {
            'fanyi1': 'ff6b6b',
            'fanyi2': '💄',
            'fanyi3': '667eea',
            'fanyi4': '764ba2',
            'fanyi5': 'ff9a9e'
        };
        return colors[style] || 'ff6b6b';
    }

    getTemplateIcon(style) {
        const icons = {
            'fanyi1': '🎭',
            'fanyi2': '💄',
            'fanyi3': '✨',
            'fanyi4': '🌟',
            'fanyi5': '💫'
        };
        return icons[style] || '🎭';
    }
    
    bindEvents() {
        // 主页面只需要模板选择功能
        // 其他功能在各个模板页面中实现
    }

    showToast(message) {
        const toast = document.getElementById('toast');
        if (toast) {
            toast.textContent = message;
            toast.classList.add('show');

            setTimeout(() => {
                toast.classList.remove('show');
            }, 3000);
        }
    }
}

// 初始化应用
document.addEventListener('DOMContentLoaded', () => {
    new FaceFusionApp();
});
