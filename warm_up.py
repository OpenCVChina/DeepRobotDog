# 机器狗起立前校准
import time
import struct
import threading
import os
import psutil
from utils.Controller import Controller

os.system(f'sudo clear')  # 引导用户给予root权限，避免忘记sudo运行此脚本

# global config
client_address = ("192.168.1.103", 43897)
server_address = ("192.168.1.120", 43893)
# creat a controller
controller = Controller(server_address)

has_arm = True
try:
    from utils.ArmController import ArmController
    arm_controller = ArmController("/dev/ttyUSB0")
    arm_controller.set_pose(1)
except Exception as e:
    print("no arm")
    has_arm = False

global stop_heartbeat
stop_heartbeat = False

# start to exchange heartbeat pack
def heart_exchange(con):
    pack = struct.pack('<3i', 0x21040001, 0, 0)
    while True:
        if stop_heartbeat:
            return
        con.send(pack)
        time.sleep(0.25)  # 4Hz
heart_exchange_thread = threading.Thread(target=heart_exchange, args=(controller,))
heart_exchange_thread.start()

# stand up
pack = struct.pack('<3i', 0x21010202, 0, 0)
print(1)
controller.send(pack)
time.sleep(5)
print(2)
controller.send(pack)
time.sleep(5)
print(3)
controller.send(pack)

print("Waiting 15s......")
time.sleep(15)
if has_arm:
    arm_controller.set_pose(2)
print("Rotating...")
controller.send(struct.pack('<3i', 0x21010135, 13000, 0))
time.sleep(3)  # need time to turn 360 degrees
controller.send(struct.pack('<3i', 0x21010135, 0, 0))
time.sleep(5)
print(4)
controller.send(pack)
stop_heartbeat = True

# 杀掉占用最高的进程
print("kill the biggest python process")
# 遍历所有进程
py_procs = {}
for proc in psutil.process_iter():
    # 获取进程信息
    info = proc.as_dict(attrs=['pid', 'name', 'memory_percent'])
    # 如果是python进程，添加到字典中
    if info['name'] in ['python', 'python3']:
        py_procs[info['pid']] = info['memory_percent']

# 定义一个计数器变量
count = 1
# 如果字典不为空且计数器大于0
while py_procs and count > 0:
    # 找到memory_percent最大的键值对
    max_pid = max(py_procs, key=py_procs.get)
    max_mem = py_procs[max_pid]
    # 杀掉该进程
    os.system(f'sudo kill -9 {max_pid}')
    # 打印结果
    print(f'Killed process {max_pid} with memory_percent {max_mem}')
    # 从字典中删除该键值对
    del py_procs[max_pid]
    # 计数器加一
    count -= 1
