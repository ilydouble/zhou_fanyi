#!/usr/bin/env python3
"""
测试LivePortrait API就绪状态
验证文件上传和URL生成是否满足API要求
"""

from pathlib import Path
from oss_uploader import OSSUploader
import time

def test_api_requirements():
    """测试是否满足LivePortrait API要求"""
    print("=== LivePortrait API就绪测试 ===")
    
    try:
        uploader = OSSUploader()
        print("✓ OSS上传器初始化成功")
        
        # 测试图片上传
        pics_dir = Path("pics")
        image_files = list(pics_dir.glob("*.jpg")) + list(pics_dir.glob("*.jpeg"))
        
        if not image_files:
            print("✗ 没有找到测试图片")
            return False
        
        test_image = image_files[0]
        print(f"📸 测试图片: {test_image}")
        
        # 上传图片
        image_url = uploader.upload_image(test_image)
        if not image_url:
            print("✗ 图片上传失败")
            return False
        
        print(f"✓ 图片上传成功")
        print(f"🔗 图片URL: {image_url}")
        
        # 检查URL格式
        url_checks = [
            ("URL以https开头", image_url.startswith("https://")),
            ("URL包含域名", "oss-cn-beijing.aliyuncs.com" in image_url),
            ("URL包含文件路径", "liveportrait" in image_url),
            ("URL格式正确", "?" in image_url or image_url.endswith(('.jpg', '.jpeg', '.png')))
        ]
        
        all_checks_passed = True
        for check_name, check_result in url_checks:
            if check_result:
                print(f"✓ {check_name}")
            else:
                print(f"✗ {check_name}")
                all_checks_passed = False
        
        # 测试音频上传
        audio_file = Path("sound/qiezi.wav")
        if not audio_file.exists():
            print("✗ 音频文件不存在")
            return False
        
        print(f"🎵 测试音频: {audio_file}")
        
        # 上传音频
        audio_url = uploader.upload_audio(audio_file)
        if not audio_url:
            print("✗ 音频上传失败")
            return False
        
        print(f"✓ 音频上传成功")
        print(f"🔗 音频URL: {audio_url}")
        
        # 检查音频URL格式
        audio_checks = [
            ("音频URL以https开头", audio_url.startswith("https://")),
            ("音频URL包含域名", "oss-cn-beijing.aliyuncs.com" in audio_url),
            ("音频URL包含文件路径", "liveportrait" in audio_url),
            ("音频URL格式正确", "?" in audio_url or audio_url.endswith(('.wav', '.mp3')))
        ]
        
        for check_name, check_result in audio_checks:
            if check_result:
                print(f"✓ {check_name}")
            else:
                print(f"✗ {check_name}")
                all_checks_passed = False
        
        return all_checks_passed
        
    except Exception as e:
        print(f"✗ 测试过程中发生错误: {e}")
        return False

def test_api_payload_format():
    """测试API请求格式"""
    print("\n=== API请求格式测试 ===")
    
    try:
        uploader = OSSUploader()
        
        # 获取测试文件URL
        test_image = Path("pics").glob("*.jpg").__next__()
        test_audio = Path("sound/qiezi.wav")
        
        image_url = uploader.upload_image(test_image)
        audio_url = uploader.upload_audio(test_audio)
        
        if not image_url or not audio_url:
            print("✗ 文件上传失败")
            return False
        
        # 模拟API请求格式
        detect_payload = {
            "model": "liveportrait-detect",
            "input": {
                "image_url": image_url
            }
        }
        
        video_payload = {
            "model": "liveportrait",
            "input": {
                "image_url": image_url,
                "audio_url": audio_url
            },
            "parameters": {
                "template_id": "normal",
                "eye_move_freq": 0.5,
                "video_fps": 24,
                "mouth_move_strength": 1.0,
                "paste_back": True,
                "head_move_strength": 0.7
            }
        }
        
        print("✓ 图像检测API请求格式:")
        print(f"  模型: {detect_payload['model']}")
        print(f"  图片URL: {detect_payload['input']['image_url'][:80]}...")
        
        print("✓ 视频生成API请求格式:")
        print(f"  模型: {video_payload['model']}")
        print(f"  图片URL: {video_payload['input']['image_url'][:80]}...")
        print(f"  音频URL: {video_payload['input']['audio_url'][:80]}...")
        print(f"  参数: {len(video_payload['parameters'])} 个配置项")
        
        return True
        
    except Exception as e:
        print(f"✗ API格式测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("LivePortrait API就绪状态检查")
    print("=" * 50)
    
    tests = [
        ("API要求检查", test_api_requirements),
        ("API格式测试", test_api_payload_format)
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
        print("🎉 LivePortrait API就绪！")
        print("✅ 文件上传功能正常")
        print("✅ URL格式符合API要求")
        print("✅ 可以开始视频生成")
        print("\n🚀 运行以下命令开始生成视频:")
        print("   python video_generator.py")
    else:
        print("⚠️  部分功能未就绪，请检查配置")
    
    return passed == total

if __name__ == "__main__":
    main()
