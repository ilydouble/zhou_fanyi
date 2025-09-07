#!/usr/bin/env python3
"""
简单的HTTP文件服务器
用于为LivePortrait API提供可访问的文件URL
"""

import os
import threading
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class FileServer:
    def __init__(self, port=8000, directory="."):
        self.port = port
        self.directory = Path(directory).resolve()
        self.server = None
        self.server_thread = None
        self.base_url = f"http://localhost:{port}"
    
    def start(self):
        """启动文件服务器"""
        os.chdir(self.directory)
        
        class CustomHandler(SimpleHTTPRequestHandler):
            def log_message(self, format, *args):
                # 减少日志输出
                pass
        
        self.server = HTTPServer(('localhost', self.port), CustomHandler)
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()
        
        logger.info(f"文件服务器已启动: {self.base_url}")
        logger.info(f"服务目录: {self.directory}")
        
        # 等待服务器启动
        time.sleep(1)
    
    def stop(self):
        """停止文件服务器"""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            logger.info("文件服务器已停止")
    
    def get_file_url(self, file_path):
        """获取文件的HTTP URL"""
        relative_path = Path(file_path).relative_to(self.directory)
        return f"{self.base_url}/{relative_path.as_posix()}"

if __name__ == "__main__":
    # 测试文件服务器
    server = FileServer()
    try:
        server.start()
        print(f"服务器运行在: {server.base_url}")
        print("按 Ctrl+C 停止服务器")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        server.stop()
        print("服务器已停止")
