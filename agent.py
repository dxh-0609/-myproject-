# agent.py
import psutil
import requests
import time
import os
import socket

# 获取主机名作为唯一标识
HOST_NAME = socket.gethostname()

# 服务器地址
SERVER_URL = os.getenv('SERVER_URL', 'http://web:5000/api/report')

print(f"Monitor Agent Started for Host: {HOST_NAME}. Target: {SERVER_URL}")

while True:
    try:
        # 1. 获取系统信息
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_info = psutil.virtual_memory()
        memory_percent = memory_info.percent
        
        # 2. 构造数据包（添加主机标识）
        payload = {
            "host": HOST_NAME,
            "cpu": cpu_percent,
            "memory": memory_percent
        }
        
        # 3. 发送给后端
        response = requests.post(SERVER_URL, json=payload)
        print(f"Host {HOST_NAME} - Sent: {payload}, Status: {response.status_code}")
        
    except Exception as e:
        print(f"Error: {e}")
    
    # 每2秒采集一次
    time.sleep(2)
