#!/usr/bin/env python3

"""
Reactive Follow Gap Navigation
Author: EON

Pipeline

LaserScan
    ↓
Preprocess
    ↓
Find Closest Obstacle
    ↓
Create Safety Bubble
    ↓
Find Largest Gap
    ↓
Find Best Point
    ↓
Compute Twist
    ↓
Publish /cmd_vel
"""

import math
from typing import List, Tuple

import numpy as np

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSReliabilityPolicy

from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist


class ReactiveGapFollow(Node):

    def __init__(self):

        super().__init__("reactive_gap_follow")

        ##########################################################
        # Parameters
        ##########################################################

        self.declare_parameter("scan_topic", "/scan")
        self.declare_parameter("cmd_topic", "/cmd_vel")

        self.declare_parameter("max_range", 3.5)
        self.declare_parameter("min_range", 0.05)

        self.declare_parameter("bubble_radius", 10)

        self.declare_parameter("max_speed", 0.40)
        self.declare_parameter("min_speed", 0.08)

        self.declare_parameter("steering_gain", 1.2)

        ##########################################################

        self.scan_topic = self.get_parameter(
            "scan_topic").value

        self.cmd_topic = self.get_parameter(
            "cmd_topic").value

        self.max_range = self.get_parameter(
            "max_range").value

        self.min_range = self.get_parameter(
            "min_range").value

        self.bubble_radius = self.get_parameter(
            "bubble_radius").value

        self.max_speed = self.get_parameter(
            "max_speed").value

        self.min_speed = self.get_parameter(
            "min_speed").value

        self.steering_gain = self.get_parameter(
            "steering_gain").value

        ##########################################################

        qos_scan = QoSProfile(depth=10)
        qos_scan.reliability = QoSReliabilityPolicy.BEST_EFFORT

        self.scan_sub = self.create_subscription(
            LaserScan,
            self.scan_topic,
            self.scan_callback,
            qos_scan
        )

        self.cmd_pub = self.create_publisher(
            Twist,
            self.cmd_topic,
            10
        )

        self.get_logger().info(
            "Reactive Gap Follow Started."
        )

    ############################################################
    # STEP 1
    # Preprocess Scan
    ############################################################

    def preprocess_scan(
        self,
        ranges: List[float]
    ) -> np.ndarray:

        """
        Clean LaserScan data.

        Steps

        1. Convert to NumPy

        2. Replace NaN

        3. Replace Inf

        4. Clamp distances

        5. Smooth using moving average
        """

        ranges = np.array(
            ranges,
            dtype=np.float32
        )

        ranges = np.nan_to_num(
            ranges,
            nan=self.max_range,
            posinf=self.max_range,
            neginf=self.min_range
        )

        ranges = np.clip(
            ranges,
            self.min_range,
            self.max_range
        )

        #######################################################

        window_size = 5

        kernel = np.ones(window_size)

        kernel /= window_size

        filtered = np.convolve(
            ranges,
            kernel,
            mode="same"
        )

        return filtered

    ############################################################
    # STEP 2
    # Find Closest Obstacle
    ############################################################

    def find_closest_obstacle(
        self,
        ranges: np.ndarray
    ) -> int:

        """
        Returns the index of the closest obstacle.
        """

        return int(np.argmin(ranges))

    ############################################################
    # STEP 3
    # Create Safety Bubble
    ############################################################

    def create_safety_bubble(
        self,
        ranges: np.ndarray,
        obstacle_index: int
    ) -> np.ndarray:

        """
        Removes points around the closest obstacle.

        This prevents the robot from trying
        to squeeze through tiny openings.
        """

        start = max(
            0,
            obstacle_index - self.bubble_radius
        )

        end = min(
            len(ranges) - 1,
            obstacle_index + self.bubble_radius
        )

        ranges[start:end] = 0.0

        return ranges

    ############################################################
    # STEP 4
    # Largest Gap
    ############################################################

    def find_largest_gap(
        self,
        ranges: np.ndarray
    ) -> Tuple[int, int]:

        """
        Finds the largest sequence
        of non-zero values.
        """

        max_start = 0
        max_end = 0

        current_start = 0

        inside_gap = False

        for i in range(len(ranges)):

            if ranges[i] > 0:

                if not inside_gap:

                    current_start = i
                    inside_gap = True

            else:

                if inside_gap:

                    current_end = i

                    if (
                        current_end - current_start
                        >
                        max_end - max_start
                    ):

                        max_start = current_start
                        max_end = current_end

                    inside_gap = False

        if inside_gap:

            current_end = len(ranges)

            if (
                current_end - current_start
                >
                max_end - max_start
            ):

                max_start = current_start
                max_end = current_end

        return max_start, max_end
    
        ############################################################
    # STEP 5
    # Best Point
    ############################################################

    def find_best_point(
        self,
        ranges: np.ndarray,
        start: int,
        end: int
    ) -> int:
        """
        Select the best point inside the largest gap.

        Strategy:
            Choose the furthest point.
            If several points share the same distance,
            choose the middle of them.
        """

        if end <= start:
            return start

        gap = ranges[start:end]

        if len(gap) == 0:
            return start

        max_distance = np.max(gap)

        candidate_indices = np.where(gap == max_distance)[0]

        if len(candidate_indices) == 0:
            return (start + end) // 2

        middle = candidate_indices[len(candidate_indices) // 2]

        return start + int(middle)

    ############################################################
    # STEP 6
    # Convert Target into Twist
    ############################################################

    def compute_twist(
        self,
        scan: LaserScan,
        target_index: int
    ) -> Twist:

        twist = Twist()

        #######################################################
        # Convert beam index into angle
        #######################################################

        target_angle = (
            scan.angle_min +
            target_index * scan.angle_increment
        )

        #######################################################
        # Angular Velocity
        #######################################################

        angular = target_angle * self.steering_gain

        #######################################################
        # Limit steering
        #######################################################

        angular = max(
            -1.5,
            min(
                1.5,
                angular
            )
        )

        #######################################################
        # Speed Control
        #######################################################

        steering_ratio = min(
            abs(angular) / 1.5,
            1.0
        )

        speed = (
            self.max_speed -
            steering_ratio *
            (self.max_speed - self.min_speed)
        )

        twist.linear.x = speed
        twist.angular.z = angular

        return twist

    ############################################################
    # STEP 7
    # Main Algorithm
    ############################################################

    def scan_callback(
        self,
        scan: LaserScan
    ):

        #######################################################
        # 1. Preprocess
        #######################################################

        ranges = self.preprocess_scan(
            scan.ranges
        )

        #######################################################
        # 2. Find closest obstacle
        #######################################################

        closest = self.find_closest_obstacle(
            ranges
        )

        #######################################################
        # 3. Create safety bubble
        #######################################################

        ranges = self.create_safety_bubble(
            ranges,
            closest
        )

        #######################################################
        # 4. Find largest free gap
        #######################################################

        gap_start, gap_end = self.find_largest_gap(
            ranges
        )

        #######################################################
        # 5. Choose best point
        #######################################################

        best_point = self.find_best_point(
            ranges,
            gap_start,
            gap_end
        )

        #######################################################
        # 6. Compute motion
        #######################################################

        twist = self.compute_twist(
            scan,
            best_point
        )

        #######################################################
        # 7. Publish
        #######################################################

        self.cmd_pub.publish(
            twist
        )

        #######################################################
        # Debug
        #######################################################

        self.get_logger().debug(
            f"Closest={closest}  "
            f"Gap=({gap_start},{gap_end})  "
            f"Best={best_point}  "
            f"Speed={twist.linear.x:.2f}  "
            f"Turn={twist.angular.z:.2f}"
        )


###############################################################
# Main
###############################################################

def main(args=None):

    rclpy.init(args=args)

    node = ReactiveGapFollow()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    node.destroy_node()

    rclpy.shutdown()


if __name__ == "__main__":
    main()