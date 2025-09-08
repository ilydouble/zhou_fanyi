#!/usr/bin/env python3
"""
检查当前服务器的出口IP地址
"""

import requests
import json

def check_external_ip():
    """检查外部IP地址"""
    services = [
        'https://api.ipify.org?format=json',
        'https://httpbin.org/ip',
        'https://api.ip.sb/ip',
        'https://ifconfig.me/ip'
    ]
    
    print("🔍 检查服务器出口IP地址...")
    
    for service in services:
        try:
            response = requests.get(service, timeout=5)
            if response.status_code == 200:
                if service.endswith('json'):
                    data = response.json()
                    ip = data.get('ip') or data.get('origin', '').split(',')[0].strip()
                else:
                    ip = response.text.strip()
                
                print(f"✅ {service}: {ip}")
            else:
                print(f"❌ {service}: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ {service}: {e}")

def test_wechat_api():
    """测试微信API访问"""
    print("\n🔍 测试微信API访问...")
    
    # 使用你的真实配置
    appid = 'wx2dfdec3e7ae9a3ff'
    appsecret = 'd5bc14defd9f1f28c885553e558bf7d0'
    
    url = f"https://api.weixin.qq.com/cgi-bin/token"
    params = {
        'grant_type': 'client_credential',
        'appid': appid,
        'secret': appsecret
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        print(f"📡 微信API响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        if 'access_token' in data:
            print("✅ 微信API访问成功！IP白名单配置正确")
            return True
        elif data.get('errcode') == 40164:
            print("⚠️ IP白名单错误，需要添加正确的IP地址")
            return False
        else:
            print(f"❌ 其他错误: {data}")
            return False
            
    except Exception as e:
        print(f"❌ 微信API访问失败: {e}")
        return False

if __name__ == '__main__':
    print("🚀 IP地址和微信API检测工具")
    print("=" * 50)
    
    # 检查外部IP
    check_external_ip()
    
    # 测试微信API
    test_wechat_api()
    
    print("\n📋 配置建议:")
    print("1. 将上述所有IP地址都添加到微信公众平台的IP白名单中")
    print("2. 等待5-10分钟让配置生效")
    print("3. 重启服务器测试")
    print("4. 如果仍有问题，检查网络代理或防火墙设置")
