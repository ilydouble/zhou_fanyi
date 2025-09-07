#!/usr/bin/env python3
"""
LivePortrait 视频生成器演示脚本 (OSS版本)
使用阿里云OSS对象存储提供文件访问
"""

import subprocess
import sys
from pathlib import Path
import time

def run_command(command, description):
    """运行命令并显示结果"""
    print(f"\n{'='*50}")
    print(f"执行: {description}")
    print(f"命令: {command}")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if result.stdout:
            print("输出:")
            print(result.stdout)
        
        if result.stderr:
            print("错误:")
            print(result.stderr)
        
        if result.returncode == 0:
            print(f"✓ {description} 成功完成")
        else:
            print(f"✗ {description} 执行失败 (返回码: {result.returncode})")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"✗ 执行命令时出错: {e}")
        return False

def check_oss_credentials():
    """检查OSS凭证配置"""
    print("\n=== OSS配置检查 ===")
    
    from dotenv import load_dotenv
    import os
    
    load_dotenv()
    
    required_vars = [
        'OSS_ACCESS_KEY_ID',
        'OSS_ACCESS_KEY_SECRET', 
        'OSS_BUCKET_NAME',
        'OSS_ENDPOINT'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # 只显示前几个字符，保护敏感信息
            display_value = value[:10] + "..." if len(value) > 10 else value
            print(f"✓ {var}: {display_value}")
        else:
            print(f"✗ {var}: 未配置")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n请在.env文件中配置以下变量: {', '.join(missing_vars)}")
        return False
    
    return True

def test_oss_upload():
    """测试OSS上传功能"""
    print("\n=== OSS上传测试 ===")
    
    try:
        from oss_uploader import OSSUploader
        
        # 创建测试文件
        test_file = Path("test_upload.txt")
        test_content = f"OSS上传测试 - {time.strftime('%Y-%m-%d %H:%M:%S')}"
        test_file.write_text(test_content, encoding='utf-8')
        
        print(f"创建测试文件: {test_file}")
        
        # 初始化上传器
        uploader = OSSUploader()
        
        # 上传测试文件
        print("正在上传测试文件...")
        url = uploader.upload_file(test_file, "test/demo_test.txt")
        
        if url:
            print(f"✓ 测试上传成功!")
            print(f"  文件URL: {url}")
            
            # 清理本地测试文件
            test_file.unlink()
            print("✓ 本地测试文件已清理")
            
            return True
        else:
            print("✗ 测试上传失败")
            test_file.unlink()
            return False
            
    except Exception as e:
        print(f"✗ OSS上传测试失败: {e}")
        if test_file.exists():
            test_file.unlink()
        return False

def main():
    """主演示函数"""
    print("LivePortrait 视频生成器 - OSS版本演示")
    print("这个版本使用阿里云OSS对象存储提供文件访问")
    print("=" * 60)
    
    # 检查Python版本
    print(f"Python版本: {sys.version}")
    
    # 步骤1: 安装依赖
    print("\n步骤1: 安装依赖包")
    if not run_command("pip install -r requirements.txt", "安装依赖包"):
        print("依赖安装失败，请手动安装")
        return
    
    # 步骤2: 检查OSS配置
    print("\n步骤2: 检查OSS配置")
    if not check_oss_credentials():
        print("OSS配置不完整，请检查.env文件")
        return
    
    # 步骤3: 测试OSS上传
    print("\n步骤3: 测试OSS上传功能")
    if not test_oss_upload():
        print("OSS上传测试失败，请检查配置和网络连接")
        return
    
    # 步骤4: 运行环境测试
    print("\n步骤4: 运行完整环境测试")
    if not run_command("python test_setup.py", "环境配置测试"):
        print("环境测试失败，请检查配置")
        return
    
    # 步骤5: 显示当前文件状态
    print("\n步骤5: 检查输入文件")
    pics_dir = Path('pics')
    image_files = list(pics_dir.glob('*.jpg')) + list(pics_dir.glob('*.jpeg')) + list(pics_dir.glob('*.png'))
    
    print(f"当前pics目录下有 {len(image_files)} 个图片文件:")
    for img in image_files:
        print(f"  - {img.name}")
    
    sound_file = Path('sound/qiezi.wav')
    if sound_file.exists():
        print(f"✓ 音频文件存在: {sound_file}")
    else:
        print(f"✗ 音频文件不存在: {sound_file}")
        return
    
    # 步骤6: 询问是否继续
    print(f"\n步骤6: 确认执行")
    print("注意事项:")
    print("- 图片和音频文件将上传到OSS对象存储")
    print("- 视频生成过程可能需要几分钟时间")
    print("- 请确保网络连接稳定")
    print("- 请注意API使用配额和费用")
    
    response = input(f"\n是否开始处理这 {len(image_files)} 个图片？(y/n): ")
    if response.lower() != 'y':
        print("演示已取消")
        return
    
    # 步骤7: 运行主程序
    print("\n步骤7: 开始视频生成")
    print("正在启动视频生成器...")
    print("请耐心等待，这个过程可能需要几分钟...")
    
    start_time = time.time()
    
    if run_command("python video_generator.py", "视频生成"):
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n✓ 视频生成完成！总耗时: {duration:.1f} 秒")
        
        # 显示结果
        videos_dir = Path('videos')
        video_files = list(videos_dir.glob('*_generated.mp4'))
        
        print(f"\n生成结果:")
        print(f"共生成 {len(video_files)} 个视频:")
        for video in video_files:
            file_size = video.stat().st_size / (1024 * 1024)  # MB
            print(f"  - {video.name} ({file_size:.1f} MB)")
        
        print(f"\n视频保存在: {videos_dir.absolute()}")
        
        # 清理建议
        print(f"\n清理建议:")
        print("- 生成的视频已保存到本地")
        print("- OSS上的临时文件会在24小时后自动清理")
        print("- 如需立即清理，可以手动删除OSS上的文件")
        
    else:
        print("视频生成失败，请检查日志")

if __name__ == "__main__":
    main()
