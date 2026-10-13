from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import (
    LaunchConfiguration, NotSubstitution, OrSubstitution, PathJoinSubstitution
)
from launch_ros.substitutions import FindPackageShare



def include_robot_launch(launch_file, launch_arguments, condition=None):
    return IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare('bender_bringup'), 'launch', 'robot', launch_file
            ])
        ),
        launch_arguments=launch_arguments.items(),
        condition=condition
    )


def generate_launch_description():
    use_arms = LaunchConfiguration('use_arms')
    use_base = LaunchConfiguration('use_base')
    use_joy = LaunchConfiguration('use_joy')
    use_lidar = LaunchConfiguration('use_lidar')
    use_rviz = LaunchConfiguration('use_rviz')
    slam = LaunchConfiguration('slam')
    use_sim = LaunchConfiguration('use_sim')

    declare_use_arms = DeclareLaunchArgument(
        'use_arms', default_value='true',
        description='Start shoulders, arms, grippers and head, and MoveIt'
    )
    declare_use_base = DeclareLaunchArgument(
        'use_base', default_value='true',
        description='Start the Pioneer base, localization and Nav2'
    )
    declare_use_joy = DeclareLaunchArgument(
        'use_joy', default_value='true',
        description='Start the joystick teleop (only if use_base is true)'
    )
    declare_use_lidar = DeclareLaunchArgument(
        'use_lidar', default_value='true',
        description='Start the RPLidar C1 and its scan filter (publishes /scan)'
    )
    declare_use_rviz = DeclareLaunchArgument(
        'use_rviz', default_value='true',
        description='Launch MoveIt RViz (only if use_arms is true)'
    )
    declare_slam = DeclareLaunchArgument(
        'slam', default_value='false',
        description='Build a map with slam_toolbox instead of localizing with AMCL'
    )
    declare_use_sim = DeclareLaunchArgument(
        'use_sim', default_value='false',
        description='Run the robot in Gazebo instead of starting the real hardware'
    )

    hardware = include_robot_launch(
        'bender_hardware.launch.py',
        {'use_arms': use_arms, 'use_base': use_base, 'use_joy': use_joy, 'use_lidar': use_lidar},
        condition=UnlessCondition(use_sim)
    )

    # Gazebo siempre simula el robot completo. El TF world -> odom solo se publica
    # sin navegación, porque con AMCL o SLAM odom ya cuelga de map.
    simulation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare('bender_bringup'), 'launch', 'sim', 'gazebo.launch.py'
            ])
        ),
        launch_arguments={'world_tf': NotSubstitution(use_base)}.items(),
        condition=IfCondition(use_sim)
    )

    navigation = include_robot_launch(
        'bender_navigation.launch.py',
        {'slam': slam, 'use_sim_time': use_sim},
        condition=IfCondition(use_base)
    )

    # En simulación la base siempre existe (odom -> base_link), aunque no se navegue.
    moveit = include_robot_launch(
        'bender_moveit.launch.py',
        {
            'use_rviz': use_rviz,
            'use_base': OrSubstitution(use_base, use_sim),
            'use_sim_time': use_sim,
        },
        condition=IfCondition(use_arms)
    )

    return LaunchDescription([
        declare_use_arms,
        declare_use_base,
        declare_use_joy,
        declare_use_lidar,
        declare_use_rviz,
        declare_slam,
        declare_use_sim,
        hardware,
        simulation,
        navigation,
        moveit,
    ])
