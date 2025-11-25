from flask import Flask, render_template, jsonify, request, send_file
import datetime
from collections import defaultdict
import sqlite3
import json
import os
from contextlib import closing
import csv
import io
from datetime import datetime, timedelta

app = Flask(__name__)

# 数据库配置
DATABASE = 'monitor.db'

def init_db():
    """初始化数据库"""
    with closing(sqlite3.connect(DATABASE)) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS monitor_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                host TEXT NOT NULL,
                cpu REAL NOT NULL,
                memory REAL NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                host TEXT NOT NULL,
                type TEXT NOT NULL,
                value REAL NOT NULL,
                threshold REAL NOT NULL,
                message TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                resolved BOOLEAN DEFAULT FALSE
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        ''')
        conn.commit()

def get_db():
    """获取数据库连接"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# 初始化数据库
init_db()

# 内存中的最新数据（用于实时显示）
latest_data = defaultdict(list)

# 1. 前端页面路由
@app.route('/')
def index():
    return render_template('index.html')

# 2. API: 接收监控数据
@app.route('/api/report', methods=['POST'])
def report_data():
    data = request.json
    host_name = data.get('host', 'unknown')
    cpu = data.get('cpu', 0)
    memory = data.get('memory', 0)
    
    # 添加时间戳
    current_time = datetime.now().strftime('%H:%M:%S')
    data['time'] = current_time
    
    # 存储到内存（用于实时显示）
    latest_data[host_name].append(data)
    if len(latest_data[host_name]) > 50:  # 保留最近50条
        latest_data[host_name].pop(0)
    
    # 存储到数据库
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO monitor_data (host, cpu, memory) VALUES (?, ?, ?)',
            (host_name, cpu, memory)
        )
        conn.commit()
    except Exception as e:
        print(f"数据库错误: {e}")
    finally:
        conn.close()
    
    # 检查告警
    check_alerts(host_name, cpu, memory)
    
    return jsonify({"status": "success"})

def check_alerts(host, cpu, memory):
    """检查是否触发告警"""
    # 默认阈值
    cpu_threshold = 80.0
    memory_threshold = 85.0
    
    alerts = []
    
    if cpu > cpu_threshold:
        alerts.append({
            'type': 'cpu',
            'value': cpu,
            'threshold': cpu_threshold,
            'message': f'CPU使用率过高: {cpu}% > {cpu_threshold}%'
        })
    
    if memory > memory_threshold:
        alerts.append({
            'type': 'memory', 
            'value': memory,
            'threshold': memory_threshold,
            'message': f'内存使用率过高: {memory}% > {memory_threshold}%'
        })
    
    # 保存告警到数据库
    if alerts:
        conn = get_db()
        cursor = conn.cursor()
        for alert in alerts:
            cursor.execute('''
                INSERT INTO alerts (host, type, value, threshold, message)
                VALUES (?, ?, ?, ?, ?)
            ''', (host, alert['type'], alert['value'], alert['threshold'], alert['message']))
        conn.commit()
        conn.close()

# 3. API: 获取实时数据
@app.route('/api/data', methods=['GET'])
def get_data():
    host = request.args.get('host')
    if host:
        return jsonify(latest_data.get(host, []))
    else:
        return jsonify(dict(latest_data))

# 4. API: 获取主机列表
@app.route('/api/hosts', methods=['GET'])
def get_hosts():
    hosts = list(latest_data.keys())
    return jsonify(hosts)

# 5. API: 获取历史数据
@app.route('/api/history', methods=['GET'])
def get_history():
    host = request.args.get('host')
    hours = int(request.args.get('hours', 24))  # 默认24小时
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        if host:
            cursor.execute('''
                SELECT host, cpu, memory, timestamp 
                FROM monitor_data 
                WHERE host = ? AND timestamp > datetime('now', ?)
                ORDER BY timestamp
            ''', (host, f'-{hours} hours'))
        else:
            cursor.execute('''
                SELECT host, cpu, memory, timestamp 
                FROM monitor_data 
                WHERE timestamp > datetime('now', ?)
                ORDER BY timestamp
            ''', (f'-{hours} hours',))
        
        data = []
        for row in cursor.fetchall():
            data.append({
                'host': row['host'],
                'cpu': row['cpu'],
                'memory': row['memory'],
                'time': row['timestamp']
            })
        
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

# 6. API: 导出数据为CSV
@app.route('/api/export/csv', methods=['GET'])
def export_csv():
    host = request.args.get('host')
    hours = int(request.args.get('hours', 24))
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        if host:
            cursor.execute('''
                SELECT host, cpu, memory, timestamp 
                FROM monitor_data 
                WHERE host = ? AND timestamp > datetime('now', ?)
                ORDER BY timestamp
            ''', (host, f'-{hours} hours'))
        else:
            cursor.execute('''
                SELECT host, cpu, memory, timestamp 
                FROM monitor_data 
                WHERE timestamp > datetime('now', ?)
                ORDER BY timestamp
            ''', (f'-{hours} hours',))
        
        # 创建CSV
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Host', 'CPU Usage (%)', 'Memory Usage (%)', 'Timestamp'])
        
        for row in cursor.fetchall():
            writer.writerow([row['host'], row['cpu'], row['memory'], row['timestamp']])
        
        output.seek(0)
        
        filename = f"monitor_data_{host or 'all'}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

# 7. API: 获取告警信息
@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # 获取未解决的告警
        cursor.execute('''
            SELECT * FROM alerts 
            WHERE resolved = FALSE 
            ORDER BY timestamp DESC
            LIMIT 50
        ''')
        
        alerts = []
        for row in cursor.fetchall():
            alerts.append({
                'id': row['id'],
                'host': row['host'],
                'type': row['type'],
                'value': row['value'],
                'threshold': row['threshold'],
                'message': row['message'],
                'timestamp': row['timestamp']
            })
        
        return jsonify(alerts)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

# 8. API: 解决告警
@app.route('/api/alerts/<int:alert_id>/resolve', methods=['POST'])
def resolve_alert(alert_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('UPDATE alerts SET resolved = TRUE WHERE id = ?', (alert_id,))
        conn.commit()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
