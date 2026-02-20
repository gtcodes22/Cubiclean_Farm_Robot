# -*- coding:utf-8 -*-
'''!
  @file interimcode.py
  @brief 
  @author Rameez Shiekh
  @maintainer N/A
  @version  V1.0
  @data 2026-02-13
'''
import roslibpy
import time
import matlab.engine
import socket

# ---------------- ROSLIBPY Odometry Sampling ----------------
client = roslibpy.Ros(host='10.143.203.59', port=9090)
client.run()

x_list = []
y_list = []
max_samples = 300
last_sample_time = 0
sample_interval = 1.0
shutdown_requested = False

def odom_callback(message):
    global last_sample_time, shutdown_requested
    current_time = time.time()
    if current_time - last_sample_time >= sample_interval:
        x = message['pose']['pose']['position']['x']
        y = message['pose']['pose']['position']['y']
        x_list.append(x)
        y_list.append(y)
        last_sample_time = current_time
        print(f"Sample {len(x_list)}: x={x:.3f}, y={y:.3f}")

        if len(x_list) >= max_samples:
            subscription.unsubscribe()
            shutdown_requested = True

subscription = roslibpy.Topic(client, '/odom', 'nav_msgs/Odometry')
subscription.subscribe(odom_callback)

while client.is_connected and not shutdown_requested:
    time.sleep(0.1)

client.terminate()
print("ROS client terminated.")

# ---------------- MATLAB Scatter Plot ----------------
eng = matlab.engine.start_matlab()
eng.addpath(r'C:\Users\ramee\OneDrive\Documents\Group Project\MATLAB')

x_matlab = matlab.double(x_list)
y_matlab = matlab.double(y_list)
image_filename = r'C:\Users\ramee\OneDrive\Documents\Group Project\MATLAB\odom_scatter.jpg'

eng.plot_scatter(x_matlab, y_matlab, image_filename, nargout=0)
eng.quit()




'''# ---------------- Send Image via TCP ----------------
SERVER_IP = "10.143.203.200"
SERVER_PORT = 5000

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_IP, SERVER_PORT))
print("Connected to server.")

with open(image_filename, "rb") as f:
    image_bytes = f.read()

print("image bytes: ", image_bytes[:50])

client_socket.sendall(len(image_bytes).to_bytes(4, "big"))
client_socket.sendall(image_bytes)

print(f"Sent {len(image_bytes)} bytes.")
client_socket.close()
'''