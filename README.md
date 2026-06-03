# auto-aruco-diffdrive

Practice 2026 - ROS 2 simulation project for an autonomous differential-drive robot that follows a track, detects ArUco markers, turns into a docking area, and performs automatic docking.

## Overview

This project simulates a differential-drive mobile robot in Gazebo Sim. The robot uses:

- A differential-drive controller from `ros2_control`.
- A camera sensor for white-path and ArUco marker detection.
- A 2D lidar sensor for simple obstacle/wall avoidance.
- OpenCV ArUco detection for marker-based navigation.
- A Kalman filter to smooth the estimated pose of the docking marker.
- A PD controller to generate docking velocity commands.
- RViz for robot, TF, and sensor visualization.

The main mission flow is:

1. Spawn the robot in the Gazebo world.
2. Follow the simulated track using camera image processing.
3. Avoid nearby obstacles/walls using lidar sectors.
4. Detect ArUco marker ID `3` to prepare and execute the turn toward the docking area.
5. Detect ArUco marker ID `23` at the docking station.
6. Estimate marker pose, filter it with Kalman filter, generate a waypoint, and dock automatically.
7. Stop the robot after docking is complete.

## Repository Structure

```text
.
├── README.md
└── workspace
    └── src
        ├── robot_controller
        │   ├── launch
        │   │   └── run.launch.py
        │   ├── robot_controller
        │   │   ├── aruco_detector.py
        │   │   ├── control_docking.py
        │   │   ├── kalman_filter.py
        │   │   ├── pd_controller.py
        │   │   └── utils.py
        │   ├── package.xml
        │   └── setup.py
        └── robot_scene
            ├── config
            │   ├── config.rviz
            │   ├── diff_control.yaml
            │   └── ros_gz_bridge.yaml
            ├── launch
            │   └── bringup.launch.py
            ├── models
            │   ├── aruco_1
            │   └── aruco_2
            ├── urdf
            │   ├── robot_model.xacro
            │   ├── robot_model.gazebo
            │   ├── wheel.xacro
            │   ├── inertial.xacro
            │   └── materials.xacro
            └── worlds
                └── map.sdf
```

## Packages

### `robot_scene`

This package contains the simulation scene:

- Robot URDF/Xacro model.
- Gazebo-specific robot plugins and sensors.
- Gazebo world file.
- ArUco marker models.
- ROS-Gazebo bridge configuration.
- `ros2_control` differential-drive controller configuration.
- RViz configuration.

### `robot_controller`

This package contains the autonomous control logic:

- Camera callback.
- Lidar callback.
- White-path detection.
- ArUco marker detection.
- Kalman filtering.
- PD control.
- Docking state machine.

## Main ROS 2 Topics

| Topic | Type | Direction | Description |
|---|---|---|---|
| `/clock` | `rosgraph_msgs/msg/Clock` | Gazebo to ROS | Simulation time |
| `/camera/image_raw` | `sensor_msgs/msg/Image` | Gazebo to ROS | Raw camera image |
| `/camera/camera_info` | `sensor_msgs/msg/CameraInfo` | Gazebo to ROS | Camera calibration information |
| `/camera/image_debug` | `sensor_msgs/msg/Image` | ROS | Debug image with detected markers |
| `/diff_drive/scan` | `sensor_msgs/msg/LaserScan` | Gazebo to ROS | Lidar scan used for obstacle/wall avoidance |
| `/diff_drive_controller/cmd_vel` | `geometry_msgs/msg/TwistStamped` | ROS to controller | Velocity command for diff-drive controller |
| `/tf` | `tf2_msgs/msg/TFMessage` | ROS | Dynamic transforms |
| `/tf_static` | `tf2_msgs/msg/TFMessage` | ROS | Static transforms |

## Main Frames

| Frame | Description |
|---|---|
| `base_link` | Main robot body frame |
| `camera_link` | Camera frame attached to the robot |
| `lidar_link` | Lidar frame attached to the robot |
| `odom` | Odometry frame published by the diff-drive controller |
| `filter_aruco_link` | Filtered ArUco marker pose broadcast by the controller |
| `aruco_waypoint1` | Intermediate docking waypoint broadcast by the controller |

## ArUco Markers

The simulation uses two important marker IDs:

| Marker | Model | Purpose |
|---|---|---|
| ID `3` | `robot_scene/models/aruco_1` | Tells the robot to prepare and execute the turn toward the docking area |
| ID `23` | `robot_scene/models/aruco_2` | Docking station marker |

Marker ID `3` is used before docking. When the detected marker area is small, the robot enters `PREPARE_TO_TURN`. When the marker becomes large enough, the robot enters `EXECUTE_TURN`.

Marker ID `23` starts the docking mission. The robot estimates the marker pose, filters it, generates a waypoint, and moves through the docking state machine.

## Docking State Machine

The main mission state is stored in `mission`:

| Mission | Meaning |
|---|---|
| `FOLLOW_TRACK` | Default mode, robot follows the white track |
| `PREPARE_TO_TURN` | Marker ID `3` is detected but still far away |
| `EXECUTE_TURN` | Robot turns toward the docking route |
| `DOCKING_23` | Marker ID `23` is detected, docking logic is active |
| `DOCKED` | Docking is finished and robot stops |

During `DOCKING_23`, the docking step is stored in `docking_step`:

| Step | Meaning |
|---|---|
| `DETECTION` | Waits for stable marker detection |
| `WAYPOINT` | Rotates toward the generated waypoint |
| `COME_TO_WAYPOINT` | Moves toward the waypoint |
| `STATION` | Rotates toward the final docking station |
| `COME_TO_STATION` | Moves into the docking station |
| `END` | Docking completed |

## Requirements

This project is intended for ROS 2 with Gazebo Sim.

Recommended environment:

- Ubuntu with ROS 2 installed.
- Gazebo Sim packages compatible with your ROS 2 distribution.
- Python 3.
- `colcon`.
- OpenCV with ArUco support.
- ROS-Gazebo bridge.
- `ros2_control` and `diff_drive_controller`.
- RViz2.
- `rqt_image_view`.

Common ROS 2 packages used by this project:

```bash
sudo apt install \
  ros-${ROS_DISTRO}-ros-gz-sim \
  ros-${ROS_DISTRO}-ros-gz-bridge \
  ros-${ROS_DISTRO}-robot-state-publisher \
  ros-${ROS_DISTRO}-xacro \
  ros-${ROS_DISTRO}-rviz2 \
  ros-${ROS_DISTRO}-ros2-control \
  ros-${ROS_DISTRO}-ros2-controllers \
  ros-${ROS_DISTRO}-gz-ros2-control \
  ros-${ROS_DISTRO}-cv-bridge \
  ros-${ROS_DISTRO}-rqt-image-view
```

Depending on your ROS 2 distribution, package names can be slightly different.

## Build

From the repository root:

```bash
cd workspace
colcon build --symlink-install
source install/setup.bash
```

If you open a new terminal, source ROS 2 and the workspace again:

```bash
source /opt/ros/${ROS_DISTRO}/setup.bash
cd workspace
source install/setup.bash
```

## Run Full Simulation and Controller

Use this launch file to start the complete system:

```bash
cd workspace
source install/setup.bash
ros2 launch robot_controller run.launch.py
```

This starts:

- Gazebo simulation.
- Robot spawn.
- Robot state publisher.
- ROS-Gazebo bridge.
- Controller manager.
- Joint state broadcaster.
- Diff-drive controller.
- RViz2.
- `rqt_image_view`.
- Autonomous docking controller node.

The controller node starts after a short delay so that Gazebo, sensors, and controllers have time to initialize.

## Run Simulation Only

If you only want to start the scene without the autonomous controller:

```bash
cd workspace
source install/setup.bash
ros2 launch robot_scene bringup.launch.py
```

This is useful for checking:

- Robot model.
- Gazebo world.
- Sensors.
- Bridges.
- Controllers.
- RViz visualization.

## Check Useful Topics

List active topics:

```bash
ros2 topic list
```

Check camera image:

```bash
ros2 topic echo /camera/image_raw --once
```

Check lidar:

```bash
ros2 topic echo /diff_drive/scan --once
```

Check velocity command:

```bash
ros2 topic echo /diff_drive_controller/cmd_vel
```

Check controller status:

```bash
ros2 control list_controllers
```

Check TF tree:

```bash
ros2 run tf2_tools view_frames
```

## Debug Image

The controller publishes a processed camera image to:

```text
/camera/image_debug
```

The full launch file opens `rqt_image_view` with this topic. This helps verify whether ArUco markers are being detected.

If it does not open automatically, run:

```bash
rqt_image_view
```

Then select:

```text
/camera/image_debug
```

## Controller Configuration

The diff-drive controller is configured in:

```text
workspace/src/robot_scene/config/diff_control.yaml
```

Important parameters:

| Parameter | Value | Meaning |
|---|---:|---|
| `update_rate` | `50` | Controller update rate in Hz |
| `wheel_separation` | `0.65` | Distance between left and right wheels |
| `wheel_radius` | `0.1` | Wheel radius |
| `use_stamped_vel` | `true` | Uses `TwistStamped` command messages |
| `cmd_vel_timeout` | `2.0` | Stops if command timeout is reached |
| `linear.x.max_velocity` | `0.5` | Max linear velocity |
| `linear.x.min_velocity` | `-0.5` | Min linear velocity |
| `angular.z.max_velocity` | `1.0` | Max angular velocity |
| `angular.z.min_velocity` | `-1.0` | Min angular velocity |

## Algorithm Summary

### 1. Lidar Processing

The lidar scan is split into three sectors:

- Front sector: `-20` to `20` degrees.
- Left sector: `45` to `90` degrees.
- Right sector: `-90` to `-45` degrees.

The robot switches between:

- `GO`: normal movement.
- `AVOID`: rotate away from close obstacle/wall.

### 2. White-Path Detection

The camera image is cropped to the lower part of the frame. The controller converts this region to grayscale, applies blur and adaptive thresholding, then finds the largest contour.

The contour center is classified as:

- `LEFT`
- `CENTER`
- `RIGHT`

This is used to steer the robot while following the track.

### 3. ArUco Detection

The controller uses OpenCV ArUco detection with dictionary:

```text
DICT_4X4_250
```

Detected markers are drawn on `/camera/image_debug`.

### 4. Marker Pose Estimation

For marker ID `23`, the controller estimates pose using OpenCV and converts the result into:

```text
[x, y, yaw]
```

This measurement is passed into the Kalman filter.

### 5. Kalman Filter

The Kalman filter smooths the marker pose estimate. It helps reduce noise from camera detection before the PD controller generates motion commands.

### 6. PD Docking Control

The PD controller generates control output from target error. The output is converted to polar form:

- Radius-like value for linear velocity.
- Angle-like value for angular velocity.

The velocities are clipped before being sent to the diff-drive controller.

## Notes for Demo

- Wait for Gazebo, RViz, and controllers to fully load before judging robot behavior.
- The controller starts after a delay in `run.launch.py`.
- ArUco detection can depend on marker visibility, camera angle, lighting, and distance.
- If the robot does not move, check whether `diff_drive_controller` is active.
- If the robot does not detect markers, check `/camera/image_debug`.
- If the robot moves but docking is unstable, check marker pose estimation, marker size, and camera calibration.

## Troubleshooting

### Robot does not move

Check controllers:

```bash
ros2 control list_controllers
```

Expected:

```text
joint_state_broadcaster active
diff_drive_controller active
```

Also check velocity commands:

```bash
ros2 topic echo /diff_drive_controller/cmd_vel
```

### No camera image

Check bridge and topic:

```bash
ros2 topic list | grep camera
ros2 topic echo /camera/camera_info --once
```

### No lidar data

Check:

```bash
ros2 topic echo /diff_drive/scan --once
```

### Marker is not detected

Open the debug image:

```bash
rqt_image_view
```

Select:

```text
/camera/image_debug
```

Then check whether the marker is visible and large enough in the image.

### Gazebo cannot find ArUco models

The launch file appends the package `models` directory to `GZ_SIM_RESOURCE_PATH`. If models are missing, rebuild and source the workspace:

```bash
cd workspace
colcon build --symlink-install
source install/setup.bash
```

## Project Status

Current implemented features:

- Gazebo world and robot model.
- Differential-drive robot with camera and lidar.
- ROS-Gazebo topic bridge.
- ROS 2 control diff-drive controller.
- White-path detection.
- Lidar-based avoidance behavior.
- ArUco ID `3` turn trigger.
- ArUco ID `23` docking trigger.
- Kalman filter for marker pose.
- PD controller for docking.
- RViz and debug image visualization.

## Author

Maintainer: `quanmh25`

Email: `maihoangquan250205@gmail.com`



