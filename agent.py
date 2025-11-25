# agent.py - 增强版
import psutil
import requests
import time
import os
import socket
import platform

# 获取主机信息
HOST_NAME = socket.gethostname()
SYSTEM_INFO = {
    'hostname': HOST_NAME,
    'os': platform.system(),
    'platform': platform.platform(),
    'processor': platform.processor()
}

SERVER_URL = os.getenv('SERVER_URL', 'http://web:5000/api/report')

def get_system_stats():
    """获取完整的系统统计信息"""
    # CPU信息
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_cores = psutil.cpu_count()
    cpu_freq = psutil.cpu_freq()
    
    # 内存信息
    memory = psutil.virtual_memory()
    swap = psutil.swap_memory()
    
    # 磁盘信息
    disk = psutil.disk_usage('/')
    disk_io = psutil.disk_io_counters()
    
    # 网络信息
    net_io = psutil.net_io_counters()
    
    # 系统负载（Linux）
    load_avg = os.getloadavg() if hasattr(os, 'getloadavg') else (0, 0, 0)
    
    return {
        'host': HOST_NAME,
        'system_info': SYSTEM_INFO,
        'cpu': {
            'percent': cpu_percent,
            'cores': cpu_cores,
            'frequency': cpu_freq.current if cpu_freq else 0
        },
        'memory': {
            'percent': memory.percent,
            'total': memory.total,
            'available': memory.available,
            'used': memory.used
        },
        'disk': {
            'percent': disk.percent,
            'total': disk.total,
            'used': disk.used,
            'free': disk.free
        },
        'network': {
            'bytes_sent': net_io.bytes_sent if net_io else 0,
            'bytes_recv': net_io.bytes_recv if net_io else 0
        },
        'load_avg': load_avg,
        'timestamp': time.time()
    }

print(f"Enhanced Monitor Agent Started for {HOST_NAME}. Target: {SERVER_URL}")

while True:
    try:
        # 获取完整系统统计
        stats = get_system_stats()
        
        # 发送到后端
        response = requests.post(SERVER_URL, json=stats)
        print(f"Host {HOST_NAME} - Sent stats, Status: {response.status_code}")
        
    except Exception as e:
        print(f"Error: {e}")
    
    time.sleep(2)
