from launch import LaunchDescription
from launch_ros.actions import Node, LifecycleNode
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import PathJoinSubstitution, LaunchConfiguration
import os



def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time')

    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
        description='Use simulation (Gazebo) clock if true'
    )
    bringup_pkg = FindPackageShare('bender_bringup')

    nav2_params_folder = PathJoinSubstitution([
        bringup_pkg,
        'params',
        'navigation'
    ])
    
    behavior_params = PathJoinSubstitution([
        nav2_params_folder,
        'behavior_server.yaml'
    ])
    
    controller_params = PathJoinSubstitution([
        nav2_params_folder,
        'controller_server.yaml'
    ])
    
    planner_params = PathJoinSubstitution([
        nav2_params_folder,
        'planner_server.yaml'
    ])
    
    bt_params = PathJoinSubstitution([
        nav2_params_folder,
        'bt_navigator.yaml'
    ])
    
    waypoint_follower_params = PathJoinSubstitution([
        nav2_params_folder,
        'waypoint_follower.yaml'
    ])
    
    lifecycle_manager_params = PathJoinSubstitution([
        nav2_params_folder,
        'lifecycle_manager.yaml'
    ])

    bender_localization = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                bringup_pkg,
                'launch',
                'localization',
                'bender_localization.launch.py'
            ])
        )
    )
    controller_server = LifecycleNode(
        package='nav2_controller',
        executable='controller_server',
        name='controller_server',
        namespace='',
        output='screen',
        parameters=[controller_params],
    )

    planner_server = LifecycleNode(
        package='nav2_planner',
        executable='planner_server',
        name='planner_server',
        namespace='',
        output='screen',
        parameters=[planner_params],
    )

    behavior_server = LifecycleNode(
        package='nav2_behaviors',
        executable='behavior_server',
        name='behavior_server',
        namespace='',
        output='screen',
        parameters=[behavior_params],
    )


    bt_navigator = LifecycleNode(
        package='nav2_bt_navigator',
        executable='bt_navigator',
        name='bt_navigator',
        namespace='',
        output='screen',
        parameters=[bt_params],
    )

    waypoint_follower = LifecycleNode(
        package = 'nav2_waypoint_follower',
        executable = 'waypoint_follower',
        name = 'waypoint_follower',
        namespace = '',
        output = 'screen',
        parameters = [waypoint_follower_params]
    )

    # Lifecycle Manager
    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager',
        namespace='',
        output='screen',
        parameters=[lifecycle_manager_params]
    )

    return LaunchDescription([
        declare_use_sim_time,
        bender_localization,
        controller_server,
        planner_server,
        behavior_server,
        bt_navigator,
        waypoint_follower,
        lifecycle_manager
    ])
