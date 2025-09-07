#!/usr/bin/env python3
"""
测试脚本：验证环境配置和文件结构
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import requests

def test_environment():
    """测试环境配置"""
    print("=== 环境配置测试 ===")
    
    # 加载环境变量
    load_dotenv()
    
    # 检查API密钥
    api_key = os.getenv('ALIYUN_API_KEY')
    if api_key:
        print(f"✓ API密钥已配置: {api_key[:10]}...")
    else:
        print("✗ API密钥未配置，请检查.env文件")
        return False
    
    return True

def test_file_structure():
    """测试文件结构"""
    print("\n=== 文件结构测试 ===")
    
    required_dirs = ['pics', 'sound', 'videos']
    required_files = ['sound/qiezi.wav']
    
    # 检查目录
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists() and dir_path.is_dir():
            print(f"✓ 目录存在: {dir_name}")
        else:
            print(f"✗ 目录不存在: {dir_name}")
            return False
    
    # 检查必需文件
    for file_name in required_files:
        file_path = Path(file_name)
        if file_path.exists() and file_path.is_file():
            print(f"✓ 文件存在: {file_name}")
        else:
            print(f"✗ 文件不存在: {file_name}")
            return False
    
    # 检查pics目录下的图片
    pics_dir = Path('pics')
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}
    image_files = [f for f in pics_dir.iterdir() 
                   if f.is_file() and f.suffix.lower() in image_extensions]
    
    if image_files:
        print(f"✓ 找到 {len(image_files)} 个图片文件:")
        for img in image_files:
            print(f"  - {img.name}")
    else:
        print("✗ pics目录下没有找到图片文件")
        return False
    
    return True

def test_dependencies():
    """测试依赖包"""
    print("\n=== 依赖包测试 ===")

    required_packages = ['requests', 'dotenv', 'oss2']

    for package in required_packages:
        try:
            if package == 'dotenv':
                import dotenv
                print(f"✓ {package} 已安装")
            else:
                __import__(package)
                print(f"✓ {package} 已安装")
        except ImportError:
            print(f"✗ {package} 未安装")
            return False

    return True

def test_network():
    """测试网络连接"""
    print("\n=== 网络连接测试 ===")

    try:
        response = requests.get('https://dashscope.aliyuncs.com', timeout=10)
        print("✓ 可以访问阿里云服务")
    except requests.exceptions.RequestException as e:
        print(f"✗ 网络连接失败: {e}")
        return False

    return True

def test_oss_connection():
    """测试OSS连接"""
    print("\n=== OSS连接测试 ===")

    try:
        from oss_uploader import OSSUploader
        uploader = OSSUploader()
        print("✓ OSS连接成功")
        return True
    except Exception as e:
        print(f"✗ OSS连接失败: {e}")
        return False

def main():
    """主测试函数"""
    print("LivePortrait 视频生成器 - 环境测试")
    print("=" * 50)
    
    tests = [
        ("环境配置", test_environment),
        ("文件结构", test_file_structure),
        ("依赖包", test_dependencies),
        ("网络连接", test_network),
        ("OSS连接", test_oss_connection)
    ]
    
    all_passed = True
    
    for test_name, test_func in tests:
        try:
            if not test_func():
                all_passed = False
        except Exception as e:
            print(f"✗ {test_name}测试出错: {e}")
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✓ 所有测试通过！可以运行 video_generator.py")
    else:
        print("✗ 部分测试失败，请检查配置")
    
    return all_passed

if __name__ == "__main__":
    main()
