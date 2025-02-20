from flask import Flask, render_template_string, redirect, url_for
import psutil
import time
import datetime

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>System Monitor</title>
    <link rel="favicon" href="data:,">
    <style>
        body {
            font-family: monospace;
            background-color: #1a1a1a;
            color: #ffffff;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
        }
        .metric {
            margin-bottom: 20px;
            padding: 15px;
            background-color: #2d2d2d;
            border-radius: 5px;
        }
        .title {
            color: #00ff00;
            margin-bottom: 10px;
        }
        .process-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }
        .process-table th, .process-table td {
            padding: 8px;
            text-align: left;
            border-bottom: 1px solid #444;
        }
        .process-table th {
            background-color: #333;
            color: #00ff00;
        }
        .bar-container {
            width: 200px;
            background-color: #444;
            height: 20px;
            border-radius: 10px;
            overflow: hidden;
        }
        .bar {
            height: 100%;
            background-color: #00ff00;
            transition: width 0.3s ease;
        }
    </style>
    <meta http-equiv="refresh" content="5">
</head>
<body>
    <div class="container">
        <h1>System Monitor</h1>
        <div class="metric">
            <div class="title">CPU Usage</div>
            <div class="bar-container">
                <div class="bar" style="width: {{ cpu_percent }}%"></div>
            </div>
            <p>{{ cpu_percent }}%</p>
        </div>
        
        <div class="metric">
            <div class="title">Memory Usage</div>
            <div class="bar-container">
                <div class="bar" style="width: {{ memory.percent }}%"></div>
            </div>
            <p>
                Used: {{ memory.used_gb }}GB / 
                Total: {{ memory.total_gb }}GB 
                ({{ memory.percent }}%)
            </p>
        </div>

        <div class="metric">
            <div class="title">System Information</div>
            <p>Boot Time: {{ boot_time }}</p>
            <p>CPU Cores: {{ cpu_cores }}</p>
        </div>

        <div class="metric">
            <div class="title">Top Processes</div>
            <table class="process-table">
                <tr>
                    <th>PID</th>
                    <th>Name</th>
                    <th>CPU %</th>
                    <th>Memory %</th>
                    <th>Status</th>
                </tr>
                {% for process in processes %}
                <tr>
                    <td>{{ process.pid }}</td>
                    <td>{{ process.name }}</td>
                    <td>{{ process.cpu_percent }}</td>
                    <td>{{ process.memory_percent }}</td>
                    <td>{{ process.status }}</td>
                </tr>
                {% endfor %}
            </table>
        </div>
    </div>
</body>
</html>
"""

def get_size(bytes):
    """Convert bytes to GB"""
    return round(bytes / (1024 * 1024 * 1024), 2)

@app.route('/')
def index():
    """Redirect root path to htop"""
    return redirect(url_for('htop'))

@app.route('/htop')
def htop():
    # CPU information
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_cores = psutil.cpu_count()
    
    # Memory information
    memory = psutil.virtual_memory()
    memory_info = {
        'total_gb': get_size(memory.total),
        'used_gb': get_size(memory.used),
        'percent': memory.percent
    }
    
    # Boot time
    boot_time = datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
    
    # Process information
    processes = []
    for proc in sorted(psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']), 
                      key=lambda p: p.info['cpu_percent'] or 0, 
                      reverse=True)[:10]:
        try:
            processes.append({
                'pid': proc.info['pid'],
                'name': proc.info['name'],
                'cpu_percent': round(proc.info['cpu_percent'] or 0, 1),
                'memory_percent': round(proc.info['memory_percent'] or 0, 1),
                'status': proc.info['status']
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    return render_template_string(HTML_TEMPLATE,
                                cpu_percent=cpu_percent,
                                cpu_cores=cpu_cores,
                                memory=memory_info,
                                boot_time=boot_time,
                                processes=processes)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)