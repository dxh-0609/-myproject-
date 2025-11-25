# agent.py
import psutil
import requests
import time
import os

# 服务器地址 (在docker-compose中，我们用服务名 'web' 访问后端)
# 如果你在本地运行，这里可能是 http://127.0.0.1:5000/api/report
SERVER_URL = os.getenv('SERVER_URL', 'http://web:5000/api/report')

print(f"Monitor Agent Started. Target: {SERVER_URL}")

while True:
    try:
        # 1. 获取系统信息
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_info = psutil.virtual_memory()
        memory_percent = memory_info.percent

        # 2. 构造数据包
        payload = {
            "cpu": cpu_percent,
            "memory": memory_percent
        }

        # 3. 发送给后端
        response = requests.post(SERVER_URL, json=payload)
        print(f"Sent: {payload}, Status: {response.status_code}")

    except Exception as e:
        print(f"Error: {e}")
    
    # 每2秒采集一次
    time.sleep(2)
