#!/usr/bin/env python3
"""
IMX708 Camera Publisher Node for ROS 2
Publishes camera feed from Raspberry Pi Camera Module 3
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import subprocess
import numpy as np


class IMX708Publisher(Node):
    def __init__(self):
        super().__init__('imx708_camera_node')
        
        # Declare parameters
        self.declare_parameter('width', 640)
        self.declare_parameter('height', 480)
        self.declare_parameter('fps', 30)
        self.declare_parameter('camera_id', 0)
        
        # Get parameters
        width = self.get_parameter('width').value
        height = self.get_parameter('height').value
        fps = self.get_parameter('fps').value
        camera_id = self.get_parameter('camera_id').value
        
        # Create publisher
        self.publisher_ = self.create_publisher(Image, 'camera/image_raw', 10)
        self.bridge = CvBridge()
        
        # Start rpicam-vid process
        cmd = [
            'rpicam-vid',
            '--camera', str(camera_id),
            '--width', str(width),
            '--height', str(height),
            '--framerate', str(fps),
            '--timeout', '0',
            '--nopreview',
            '--codec', 'mjpeg',
            '--output', '-'
        ]
        
        self.get_logger().info(f'Starting IMX708 camera {camera_id} at {width}x{height}@{fps}fps')
        
        self.process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            bufsize=10**8
        )
        
        self.buffer = b''
        
        # Create timer to read frames
        self.timer = self.create_timer(0.001, self.timer_callback)
        
        self.get_logger().info('IMX708 camera node started')
    
    def timer_callback(self):
        try:
            # Read data chunk
            chunk = self.process.stdout.read(4096)
            if not chunk:
                self.get_logger().error('Camera stream ended')
                return
            
            self.buffer += chunk
            
            # Find JPEG frame boundaries
            start = self.buffer.find(b'\xff\xd8')
            end = self.buffer.find(b'\xff\xd9')
            
            if start != -1 and end != -1 and end > start:
                # Extract JPEG frame
                jpg = self.buffer[start:end+2]
                self.buffer = self.buffer[end+2:]
                
                # Decode to OpenCV format
                frame = cv2.imdecode(
                    np.frombuffer(jpg, dtype=np.uint8),
                    cv2.IMREAD_COLOR
                )
                
                if frame is not None:
                    # Convert to ROS Image message
                    msg = self.bridge.cv2_to_imgmsg(frame, encoding='bgr8')
                    msg.header.stamp = self.get_clock().now().to_msg()
                    msg.header.frame_id = 'camera_link'
                    
                    # Publish
                    self.publisher_.publish(msg)
        
        except Exception as e:
            self.get_logger().error(f'Error in timer callback: {str(e)}')
    
    def destroy_node(self):
        self.get_logger().info('Shutting down IMX708 camera node')
        self.process.terminate()
        self.process.wait()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = IMX708Publisher()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

