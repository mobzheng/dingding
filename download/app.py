import os
from winproxy import ProxySetting  # 导入模块
from flask import Flask, render_template, request, jsonify
import queue
import threading
import time

app = Flask(__name__)

# 实例化类
p = ProxySetting()

q = queue.Queue()

isstart = False


@app.route('/')
def index():
    return render_template('index.html')


# 开始抓包
@app.route('/capture')
def start():
    threading.Thread(target=capture, daemon=True).start()
    return 'success'


def capture():
    # 打开 or 关闭 系统代理
    p.enable = True

    # 设置指定的ip:port
    p.server = 'http=http://127.0.0.1:8888;https=http://127.0.0.1:8888'

    # 写入到注册表，可理解为 令修改系统代理生效
    p.registry_write()

    if isstart:
        return None
    # 开启临时代理
    os.system(f'mitmdump -s addons.py -p 8888 -q -w {int(time.time())}.log')


@app.route('/stop')
def stop():
    p.enable = False
    p.registry_write()
    return 'success'


@app.route('/poll')
def source():
    try:
        data = q.get(timeout=60)
        ret = []
        for v in data.values():
            ret.append(v)
        return jsonify({'data': ret})
    except queue.Empty:
        return jsonify({'data': None})


@app.route('/push', methods=['POST'])
def push():
    data = request.json
    while q.full():
        q.get_nowait()
    q.put_nowait(data)
    return 'success'


app.run(host='0.0.0.0')
# http=http://127.0.0.1:8888;https=http://127.0.0.1:8888
