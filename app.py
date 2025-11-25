from flask import Flask, render_template, jsonify, request
import datetime
from collections import defaultdict

app = Flask(__name__)

# 修改数据结构：按主机名存储监控数据
monitor_data = defaultdict(list)

# 1. 前端页面路由
@app.route('/')
def index():
    return render_template('index.html')

# 2. API: 接收监控数据
@app.route('/api/report', methods=['POST'])
def report_data():
    data = request.json
    # 添加时间戳
    data['time'] = datetime.datetime.now().strftime('%H:%M:%S')
    
    host_name = data.get('host', 'unknown')
    monitor_data[host_name].append(data)
    
    # 只保留每个主机最近20条数据
    if len(monitor_data[host_name]) > 20:
        monitor_data[host_name].pop(0)
        
    return jsonify({"status": "success"})

# 3. API: 提供所有主机数据
@app.route('/api/data', methods=['GET'])
def get_data():
    host = request.args.get('host')
    if host:
        # 返回指定主机的数据
        return jsonify(monitor_data.get(host, []))
    else:
        # 返回所有主机数据
        return jsonify(dict(monitor_data))

# 4. 新API: 获取主机列表
@app.route('/api/hosts', methods=['GET'])
def get_hosts():
    hosts = list(monitor_data.keys())
    return jsonify(hosts)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
