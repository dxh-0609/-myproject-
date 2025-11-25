# app.py
from flask import Flask, render_template, jsonify, request
import datetime

app = Flask(__name__)

# 模拟数据库，存储监控数据
monitor_data = []

# 1. 前端页面路由
@app.route('/')
def index():
    return render_template('index.html')

# 2. API: 接收监控数据 (由 Member C 的脚本发送)
@app.route('/api/report', methods=['POST'])
def report_data():
    data = request.json
    # 添加时间戳
    data['time'] = datetime.datetime.now().strftime('%H:%M:%S')
    monitor_data.append(data)
    # 只保留最近20条数据，防止内存溢出
    if len(monitor_data) > 20:
        monitor_data.pop(0)
    return jsonify({"status": "success"})

# 3. API: 提供数据给前端 (供 Member B 使用)
@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify(monitor_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
