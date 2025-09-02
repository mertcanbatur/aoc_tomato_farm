# Author: Abdurrahman Yilmaz - Modified for Gazebo Harmonic
# Date: August 27, 2025
# Description: Load tomato farm world file into Gazebo Harmonic.

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration, PythonExpression
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    # Set the path to the ROS-GZ package
    pkg_ros_gz_sim = FindPackageShare(package='ros_gz_sim').find('ros_gz_sim')
    
    # Set the path to this package.
    pkg_share = FindPackageShare(package='tomato_farm_simulator').find('tomato_farm_simulator')
    
    # Set the path to the world file
    # You can change this to switch between different farm sizes:
    # Available options: '2mx3m', '4mx3m', '6mx4m', etc.
    farm = '2mx3m'  # Use the generated farm model
    world_file_name = 'tomato_farm_simple.world'
    world_path = os.path.join(pkg_share, 'worlds', world_file_name)
    
    # Check if world file exists, if not create a simple one
    if not os.path.exists(world_path):
        world_path = os.path.join(pkg_share, 'worlds', 'empty.world')
    
    # Set the path to the SDF model files.
    gazebo_models_path = os.path.join(pkg_share, 'models', farm)
    
    # Set environment variables for Gazebo to find models
    # GZ_SIM_RESOURCE_PATH should point to the directory containing model folders
    if "GZ_SIM_RESOURCE_PATH" in os.environ:
        os.environ["GZ_SIM_RESOURCE_PATH"] = gazebo_models_path + ":" + os.environ["GZ_SIM_RESOURCE_PATH"]
    else:
        os.environ["GZ_SIM_RESOURCE_PATH"] = gazebo_models_path
    
    # Also set GAZEBO_MODEL_PATH for compatibility
    os.environ["GAZEBO_MODEL_PATH"] = gazebo_models_path

    # Launch configuration variables
    headless = LaunchConfiguration('headless')
    use_sim_time = LaunchConfiguration('use_sim_time')
    world = LaunchConfiguration('world')

    # Declare launch arguments
    declare_headless_cmd = DeclareLaunchArgument(
        name='headless',
        default_value='False',
        description='Whether to run headless (no GUI)')

    declare_use_sim_time_cmd = DeclareLaunchArgument(
        name='use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true')

    declare_world_cmd = DeclareLaunchArgument(
        name='world',
        default_value=world_path,
        description='Full path to the world model file to load')

    # Start Gazebo Harmonic
    start_gazebo_cmd = ExecuteProcess(
        cmd=['gz', 'sim', '-r', world],
        output='screen'
    )

    # Start ROS-GZ bridge
    start_bridge_cmd = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
        ],
        output='screen'
    )

    # Create the launch description
    ld = LaunchDescription()

    # Add launch arguments
    ld.add_action(declare_headless_cmd)
    ld.add_action(declare_use_sim_time_cmd)
    ld.add_action(declare_world_cmd)

    # Add actions
    ld.add_action(start_gazebo_cmd)
    ld.add_action(start_bridge_cmd)

    return ld
