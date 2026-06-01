import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    pkg_sim = get_package_share_directory('robot_scene')
    
    # 1. Gọi file Launch mô phỏng (Bao gồm Gazebo, RViz, Spawn robot, Bridge)
    sim_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_sim, 'launch', 'bringup.launch.py')
        )
    )

    rqt_image_view_node = Node(
        package='rqt_image_view',
        executable='rqt_image_view',
        name='rqt_image_view_node',
        arguments=['/camera/image_debug'], 
        output='screen'
    )

    control_docking = Node(
        package='robot_controller',
        executable='control_docking',
        name='control_docking',
        output='screen'
    )

    return LaunchDescription([
        sim_launch,
        TimerAction(period=9.0, actions=[control_docking]),
        rqt_image_view_node,
    ])
