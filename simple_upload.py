#!/usr/bin/env python3
"""
简单上传周繁漪定妆照
"""

from pathlib import Path
from oss_uploader import OSSUploader
import json

def simple_upload():
    """简单上传模板"""
    print("上传周繁漪定妆照...")
    
    try:
        uploader = OSSUploader()
        print("✓ OSS连接成功")
        
        # 定义5个模板
        templates = []
        
        for i in range(1, 6):
            file_path = Path(f'pics/fanyi-{i}.jpg')
            if file_path.exists():
                print(f"上传 fanyi-{i}.jpg...")
                
                # 上传原图 - 使用公开URL用于API调用
                url = uploader.upload_file(
                    file_path,
                    f"face_fusion/templates/fanyi_{i}.jpg",
                    use_public_url=True  # 模板使用公开URL
                )
                
                if url:
                    template = {
                        'id': str(i),
                        'name': f'周繁漪定妆照{i}',
                        'description': f'造型{i}',
                        'templateUrl': url,
                        'thumbnailUrl': url,  # 暂时使用原图作为缩略图
                        'originalFile': f'fanyi-{i}.jpg'
                    }
                    templates.append(template)
                    print(f"✓ 模板{i}上传成功")
                else:
                    print(f"✗ 模板{i}上传失败")
            else:
                print(f"✗ 文件不存在: {file_path}")
        
        # 保存配置
        config = {
            'templates': templates,
            'total': len(templates)
        }
        
        config_file = Path('web/templates_config.json')
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        print(f"✓ 配置已保存: {config_file}")
        print(f"✓ 成功上传 {len(templates)} 个模板")
        
        return templates
        
    except Exception as e:
        print(f"✗ 上传失败: {e}")
        return []

if __name__ == "__main__":
    simple_upload()
