import time
import csv
try:
    import roslibpy
except ImportError:
    print('w: could not import ROS 2 related libraries!')


# GLOBAL VARIABLES
x_list = []
y_list = []

duration = 120  # seconds to record



def main(csv_path = ''):
    # Connect to ROS
    client = connect_to_ros()
    
    # never fail silently! makes for fustrating bug hunting
    if not client:
        print('e: client failed to initialise')
        return

    # Subscribe to odometry
    subscribe_to_odom(client)

    # Main thread tracks 120 seconds
    start_time = time.time()
    while time.time() - start_time < duration:
        time.sleep(0.1)  # keep program alive

    # Stop ROS client and save CSV
    print(f"{duration} seconds reached. Stopping collection.")
    client.terminate()
    create_csv(csv_path)


def connect_to_ros():
    try:
        client = roslibpy.Ros(host='127.0.0.1', port=9090)
        client.run()
        print("Connected to ROS Bridge Server")
        return client
    except Exception as e:
        print("Failed to connect:", e)
        return 
    


def subscribe_to_odom(client):

    subscription = roslibpy.Topic(client, '/odom', 'nav_msgs/Odometry')

    def odom_callback(message):

        x = message['pose']['pose']['position']['x']
        y = message['pose']['pose']['position']['y']
        x_list.append(x)
        y_list.append(y)
        print(f"x={x:.3f}, y={y:.3f}")


    subscription.subscribe(odom_callback)




def create_csv(csv_path='odom_data.csv'):
    with open(csv_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['x','y'])
        for x, y in zip(x_list, y_list):
            writer.writerow([x, y])
    print(f"CSV file created with {len(x_list)} samples.")




if __name__ == '__main__':
    main()