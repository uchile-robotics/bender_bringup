from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import AndSubstitution, Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare

# launch in charge of running bender's hardware on raspi

CONTROLLER_MANAGER = '/bender/controller_manager'

ARM_CONTROLLERS = [
    'left_shoulder_controller',
    'right_shoulder_controller',
    'left_arm_controller',
    'right_arm_controller',
    'head_controller',
    'left_gripper_controller',
    'right_gripper_controller',
]

BASE_CONTROLLERS = [
    'pioneer_base_controller',
    'estop_broadcaster',
]


def spawner(controller, condition=None):
    return Node(
        package='controller_manager',
        executable='spawner',
        arguments=[controller, '--controller-manager', CONTROLLER_MANAGER],
        condition=condition,
    )


def generate_launch_description():
    description_pkg = FindPackageShare('bender_description')
    joy_pkg = FindPackageShare('bender_joy')
    sensors_pkg = FindPackageShare('bender_sensors')

    use_arms = LaunchConfiguration('use_arms')
    use_base = LaunchConfiguration('use_base')
    use_joy = LaunchConfiguration('use_joy')
    use_lidar = LaunchConfiguration('use_lidar')

    declare_use_arms = DeclareLaunchArgument(
        'use_arms', default_value='true',
        description='Start shoulders, arms, grippers and head (ODrive + Dynamixel)'
    )
    declare_use_base = DeclareLaunchArgument(
        'use_base', default_value='true',
        description='Start the Pioneer base, the e-stop broadcaster and twist_mux'
    )
    declare_use_joy = DeclareLaunchArgument(
        'use_joy', default_value='true',
        description='Start the joystick teleop (only if use_base is true)'
    )
    declare_use_lidar = DeclareLaunchArgument(
        'use_lidar', default_value='true',
        description='Start the RPLidar C1 and its scan filter (publishes /scan)'
    )

    urdf_path = PathJoinSubstitution([description_pkg, 'urdf', 'bender.xacro'])
    controllers_yaml_path = PathJoinSubstitution([
        description_pkg, 'config', 'controllers', 'controllers.yaml'
    ])
    twist_mux_params = PathJoinSubstitution([joy_pkg, 'params', 'twist_mux.yaml'])

    robot_description_content = ParameterValue(
        Command([
            'xacro ', urdf_path,
            ' hardware:=real',
            ' use_arms:=', use_arms,
            ' use_base:=', use_base,
        ]),
        value_type=str
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description_content}],
        # ros2_control corre en el namespace /bender
        remappings=[('joint_states', '/bender/joint_states')],
    )

    ros2_control_node = Node(
        package='controller_manager',
        executable='ros2_control_node',
        namespace='bender',
        remappings=[('robot_description', '/robot_description')],
        parameters=[controllers_yaml_path],
        output='screen'
    )

    joint_state_broadcaster_spawner = spawner('joint_state_broadcaster')
    arm_spawners = [spawner(name, IfCondition(use_arms)) for name in ARM_CONTROLLERS]
    base_spawners = [spawner(name, IfCondition(use_base)) for name in BASE_CONTROLLERS]

    joy_node = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([joy_pkg, 'launch', 'joystick.launch.py'])
        ),
        condition=IfCondition(AndSubstitution(use_base, use_joy))
    )

    lidar_node = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([sensors_pkg, 'launch', 'lidar', 'rplidar_c1_launch.py'])
        ),
        # El link del lidar en el URDF se llama laser_1
        launch_arguments={'frame_id': 'laser_1'}.items(),
        condition=IfCondition(use_lidar)
    )

    # Va junto al hardware para que el joystick mantenga la prioridad sobre Nav2
    # aunque se caiga el computador de arriba o la red.
    twist_mux = Node(
        package='twist_mux',
        executable='twist_mux',
        parameters=[twist_mux_params],
        remappings=[('/cmd_vel_out', '/bender/pioneer_base_controller/cmd_vel')],
        condition=IfCondition(use_base)
    )

    return LaunchDescription([
        declare_use_arms,
        declare_use_base,
        declare_use_joy,
        declare_use_lidar,
        robot_state_publisher,
        ros2_control_node,
        joint_state_broadcaster_spawner,
        *arm_spawners,
        *base_spawners,
        joy_node,
        lidar_node,
        twist_mux,
    ])
