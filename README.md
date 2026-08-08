# Project Eon

Project Eon is a ROS 2-based mobile robotics project for an autonomous lower-base robot platform with perception, navigation, and bring-up components.

## Project overview

This repository contains the software stack used to run the robot locally. It is organized into a typical ROS 2 workspace layout under `src/` with packages for:

- `camera` – camera publisher nodes
- `eon_bringup` – launch configuration for startup orchestration
- `eon_navigation` – reactive gap-follow navigation logic
- `arducam_rclpy_tof_pointcloud` – Arducam TOF point cloud publisher

In addition, the repository includes:

- `hardware/` – Arduino code and setup assets for the lower-base motor controller and audio hardware
- `docs/` – setup guides and notes collected during development
- `archive/setup_history/` – a snapshot of the earlier project version for reference

## Hardware components

The hardware side of the project includes:

- lower-base motor control firmware for Arduino
- audio setup files for the ReSpeaker 2-Mics HAT
- supporting notes for device configuration and environment setup

The Arduino sketch is located at:

- `hardware/arduino_lower_base/ArdunioCodeForEon2/ArdunioCodeForEon2.ino`

The audio setup script is located at:

- `hardware/setup_respeaker.sh`

## Software components

### ROS 2 packages

The main ROS 2 packages are:

- `src/arducam/arducam_rclpy_tof_pointcloud`
- `src/camera`
- `src/eon_bringup`
- `src/eon_navigation`

### Launching the system

From the workspace root:

```bash
source install/setup.bash
ros2 launch eon_bringup launch.xml
```

## Setup and installation

### 1. Prerequisites

Install the following on your machine:

- Ubuntu 22.04/24.04
- ROS 2
- Python 3
- colcon
- setuptools

### 2. Clone the repository

```bash
git clone https://github.com/Shahil-Shaikh/Projecet-Eon.git
cd Projecet-Eon
```

### 3. Build the workspace

```bash
colcon build
source install/setup.bash
```

### 4. Run the robot stack

```bash
ros2 launch eon_bringup launch.xml
```

## Notes for future development

- Keep hardware-specific files under `hardware/`
- Keep ROS packages under `src/`
- Keep setup guides and documentation under `docs/`
- Keep historical versions under `archive/`

## License

This project is intended for educational and development use. Please review package-level license declarations before redistribution.
