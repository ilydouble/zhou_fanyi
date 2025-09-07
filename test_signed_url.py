#!/usr/bin/env python3
"""
测试OSS签名URL功能
验证上传的文件是否可以通过签名URL正常访问
"""

import requests
import time
from pathlib import Path
from oss_uploader import OSSUploader

def test_signed_url_access():
    """测试签名URL是否可以正常访问"""
    print("=== OSS签名URL访问测试 ===")
    
    # 创建测试文件
    test_file = Path("test_access.txt")
    test_content = f"签名URL访问测试 - {time.strftime('%Y-%m-%d %H:%M:%S')}"
    test_file.write_text(test_content, encoding='utf-8')
    
    try:
        # 初始化上传器
        uploader = OSSUploader()
        print("✓ OSS上传器初始化成功")
        
        # 上传测试文件
        print("正在上传测试文件...")
        signed_url = uploader.upload_file(test_file, "test/access_test.txt")
        
        if not signed_url:
            print("✗ 文件上传失败")
            return False
        
        print(f"✓ 文件上传成功")
        print(f"🔗 签名URL: {signed_url[:80]}...")
        
        # 测试URL访问
        print("\n正在测试URL访问...")
        try:
            response = requests.get(signed_url, timeout=10)
            
            if response.status_code == 200:
                downloaded_content = response.text
                if downloaded_content.strip() == test_content.strip():
                    print("✅ 签名URL访问成功，内容验证通过")
                    print(f"📄 下载内容: {downloaded_content}")
                    return True
                else:
                    print("✗ 内容验证失败")
                    print(f"期望: {test_content}")
                    print(f"实际: {downloaded_content}")
                    return False
            else:
                print(f"✗ HTTP访问失败，状态码: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"✗ 网络请求失败: {e}")
            return False
            
    except Exception as e:
        print(f"✗ 测试过程中发生错误: {e}")
        return False
        
    finally:
        # 清理测试文件
        if test_file.exists():
            test_file.unlink()
            print("🧹 本地测试文件已清理")

def test_image_upload():
    """测试图片上传和签名URL生成"""
    print("\n=== 图片上传签名URL测试 ===")
    
    # 查找一个测试图片
    pics_dir = Path("pics")
    image_files = list(pics_dir.glob("*.jpg")) + list(pics_dir.glob("*.jpeg"))
    
    if not image_files:
        print("✗ 没有找到测试图片")
        return False
    
    test_image = image_files[0]
    print(f"📸 测试图片: {test_image}")
    
    try:
        uploader = OSSUploader()
        
        # 上传图片
        print("正在上传图片...")
        signed_url = uploader.upload_image(test_image)
        
        if not signed_url:
            print("✗ 图片上传失败")
            return False
        
        print(f"✓ 图片上传成功")
        print(f"🔗 签名URL: {signed_url[:80]}...")
        
        # 测试图片URL访问（只检查HTTP状态，不下载内容）
        print("正在测试图片URL访问...")
        try:
            response = requests.head(signed_url, timeout=10)
            
            if response.status_code == 200:
                print("✅ 图片签名URL访问成功")
                print(f"📊 Content-Type: {response.headers.get('Content-Type', 'unknown')}")
                print(f"📏 Content-Length: {response.headers.get('Content-Length', 'unknown')} bytes")
                return True
            else:
                print(f"✗ 图片URL访问失败，状态码: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"✗ 图片URL访问失败: {e}")
            return False
            
    except Exception as e:
        print(f"✗ 图片上传测试失败: {e}")
        return False

def test_audio_upload():
    """测试音频上传和签名URL生成"""
    print("\n=== 音频上传签名URL测试 ===")
    
    audio_file = Path("sound/qiezi.wav")
    
    if not audio_file.exists():
        print(f"✗ 音频文件不存在: {audio_file}")
        return False
    
    print(f"🎵 测试音频: {audio_file}")
    
    try:
        uploader = OSSUploader()
        
        # 上传音频
        print("正在上传音频...")
        signed_url = uploader.upload_audio(audio_file)
        
        if not signed_url:
            print("✗ 音频上传失败")
            return False
        
        print(f"✓ 音频上传成功")
        print(f"🔗 签名URL: {signed_url[:80]}...")
        
        # 测试音频URL访问
        print("正在测试音频URL访问...")
        try:
            response = requests.head(signed_url, timeout=10)
            
            if response.status_code == 200:
                print("✅ 音频签名URL访问成功")
                print(f"📊 Content-Type: {response.headers.get('Content-Type', 'unknown')}")
                print(f"📏 Content-Length: {response.headers.get('Content-Length', 'unknown')} bytes")
                return True
            else:
                print(f"✗ 音频URL访问失败，状态码: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"✗ 音频URL访问失败: {e}")
            return False
            
    except Exception as e:
        print(f"✗ 音频上传测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("OSS签名URL功能测试")
    print("=" * 50)
    
    tests = [
        ("文本文件签名URL访问", test_signed_url_access),
        ("图片上传签名URL", test_image_upload),
        ("音频上传签名URL", test_audio_upload)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 执行测试: {test_name}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} - 通过")
            else:
                print(f"❌ {test_name} - 失败")
        except Exception as e:
            print(f"❌ {test_name} - 异常: {e}")
    
    print("\n" + "=" * 50)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有签名URL测试通过！")
        print("✅ OSS文件上传和访问功能正常")
        print("✅ 可以正常为LivePortrait API提供文件访问")
    else:
        print("⚠️  部分测试失败，请检查OSS配置和网络连接")
    
    return passed == total

if __name__ == "__main__":
    main()
