import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, Command
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.actions import AppendEnvironmentVariable


def generate_launch_description():
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')
    pkg_lab = get_package_share_directory('robot_scene')
    xacro_file = os.path.join(pkg_lab, 'urdf', 'robot_model.xacro')

    # Bổ sung đường dẫn thư mục models vào biến môi trường của Gazebo
    set_env_vars_resources = AppendEnvironmentVariable(
            'GZ_SIM_RESOURCE_PATH',
            os.path.join(pkg_lab, 'models')
    )

    world_path = PathJoinSubstitution([
        FindPackageShare('robot_scene'),
        'worlds','map.sdf'
    ])

    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')),
        launch_arguments={
            'gz_args': ['-r ', world_path], 
        }.items()
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='both',
        parameters=[
            {'use_sim_time': True},
            {'robot_description': Command(['xacro ', LaunchConfiguration('urdf_model')])},
        ]
    )

    rviz = Node(
       package='rviz2',
       executable='rviz2',
       parameters=[{'use_sim_time': True}],
       arguments=['-d', os.path.join(pkg_lab, 'config', 'config.rviz')],
    )

    spawn = Node(
        package='ros_gz_sim', 
        executable='create', 
        arguments=[ '-name', 'diff_drive', '-topic', 'robot_description', '-x', '7', '-y', '1', '-z', '0.15'], 
        # arguments=[ '-name', 'diff_drive', '-topic', 'robot_description', '-x', '10.5', '-y', '7', '-z', '0.15', '-Y', '1.5708'], 
        output='screen'
    )

    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[{
            'config_file': os.path.join(pkg_lab, 'config', 'ros_gz_bridge.yaml'),
            'qos_overrides./tf_static.publisher.durability': 'transient_local',
        }],
        output='screen'
    )

    # --- KHỞI CHẠY ROS2_CONTROL CONTROLLERS ---
    spawn_joint_state_broadcaster = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster", "--controller-manager", "/controller_manager"],
        output="screen"
    )

    spawn_diff_drive_controller = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["diff_drive_controller", "--controller-manager", "/controller_manager"],
        output="screen"
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'urdf_model',
            default_value=xacro_file,
            description='Full path to the Xacro file'
        ),
        set_env_vars_resources,
        gz_sim,
        robot_state_publisher,
        spawn,
        bridge,
        TimerAction(period=4.0, actions=[spawn_joint_state_broadcaster]),
        TimerAction(period=6.0, actions=[spawn_diff_drive_controller]),
        rviz,
    ])
