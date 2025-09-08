#!/usr/bin/env python3
"""
LivePortrait 视频生成器演示脚本
"""

import subprocess
import sys
from pathlib import Path

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

def main():
    """主演示函数"""
    print("LivePortrait 视频生成器 - 演示脚本")
    print("这个脚本将演示完整的视频生成流程")
    
    # 检查Python版本
    print(f"\nPython版本: {sys.version}")
    
    # 步骤1: 安装依赖
    if not run_command("pip install -r requirements.txt", "安装依赖包"):
        print("依赖安装失败，请手动安装")
        return
    
    # 步骤2: 运行环境测试
    if not run_command("python test_setup.py", "环境配置测试"):
        print("环境测试失败，请检查配置")
        return
    
    # 步骤3: 显示当前文件状态
    pics_dir = Path('pics')
    image_files = list(pics_dir.glob('*.jpg')) + list(pics_dir.glob('*.jpeg')) + list(pics_dir.glob('*.png'))
    
    print(f"\n当前pics目录下有 {len(image_files)} 个图片文件:")
    for img in image_files:
        print(f"  - {img.name}")
    
    # 步骤4: 询问是否继续
    response = input(f"\n是否开始处理这 {len(image_files)} 个图片？(y/n): ")
    if response.lower() != 'y':
        print("演示已取消")
        return
    
    # 步骤5: 运行主程序
    print("\n开始视频生成...")
    print("注意：这个过程可能需要几分钟时间，请耐心等待")
    
    if run_command("python video_generator.py", "视频生成"):
        # 显示结果
        videos_dir = Path('videos')
        video_files = list(videos_dir.glob('*_generated.mp4'))
        
        print(f"\n生成完成！共生成 {len(video_files)} 个视频:")
        for video in video_files:
            print(f"  - {video.name}")
        
        print(f"\n视频保存在: {videos_dir.absolute()}")
    else:
        print("视频生成失败，请检查日志")

if __name__ == "__main__":
    main()
