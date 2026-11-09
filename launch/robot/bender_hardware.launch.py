from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import (AndSubstitution, Command, LaunchConfiguration,
                                  NotSubstitution, PathJoinSubstitution)
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare

# launch in charge of running bender's hardware on raspi

CONTROLLER_MANAGER = '/bender/controller_manager'

SHOULDER_CONTROLLERS = [
    'left_shoulder_controller',
    'right_shoulder_controller',
]

# Cadena izquierda (/dev/dynamixel_left): brazo y gripper izquierdos y cabeza
DYNAMIXEL_LEFT_CONTROLLERS = [
    'left_arm_controller',
    'head_controller',
    'left_gripper_controller',
]

# Cadena derecha (/dev/dynamixel_right): brazo y gripper derechos
DYNAMIXEL_RIGHT_CONTROLLERS = [
    'right_arm_controller',
    'right_gripper_controller',
]

BASE_CONTROLLERS = [
    'pioneer_base_controller',
    'estop_broadcaster',
]


def spawner(controller, condition=None, extra_args=None):
    return Node(
        package='controller_manager',
        executable='spawner',
        arguments=[controller, '--controller-manager', CONTROLLER_MANAGER] + (extra_args or []),
        condition=condition,
    )


def generate_launch_description():
    description_pkg = FindPackageShare('bender_description')
    joy_pkg = FindPackageShare('bender_joy')
    sensors_pkg = FindPackageShare('bender_sensors')

    use_arms = LaunchConfiguration('use_arms')
    use_dynamixel = LaunchConfiguration('use_dynamixel')
    use_shoulders = LaunchConfiguration('use_shoulders')
    use_dxl_right = LaunchConfiguration('use_dxl_right')
    use_base = LaunchConfiguration('use_base')
    use_joy = LaunchConfiguration('use_joy')
    use_lidar = LaunchConfiguration('use_lidar')
    use_camera = LaunchConfiguration('use_camera')
    camera_device = LaunchConfiguration('camera_device')
    camera_frame = LaunchConfiguration('camera_frame')

    declare_use_arms = DeclareLaunchArgument(
        'use_arms', default_value='true',
        description='Start shoulders, arms, grippers and head (ODrive + Dynamixel)'
    )
    declare_use_dynamixel = DeclareLaunchArgument(
        'use_dynamixel', default_value='true',
        description='Start the Dynamixel chains (arms, grippers, head). '
                    'Only if use_arms is true; false keeps just the shoulders'
    )
    declare_use_shoulders = DeclareLaunchArgument(
        'use_shoulders', default_value='true',
        description='Start the shoulders (ODrive + encoder Pico, which also drives the chest LED). '
                    'Only if use_arms is true'
    )
    # Por defecto en false: el conversor USB-RS485 de la cadena derecha está dañado
    declare_use_dxl_right = DeclareLaunchArgument(
        'use_dxl_right', default_value='false',
        description='Start the right Dynamixel chain (right arm and gripper). '
                    'Only if use_dynamixel is true'
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
        'use_lidar', default_value='false',
        description='Start the RPLidar C1 and its scan filter (publishes /scan)'
    )
    declare_use_camera = DeclareLaunchArgument(
        'use_camera', default_value='true',
        description='Start the USB camera (publishes /usb_cam/image_raw)'
    )
    declare_camera_device = DeclareLaunchArgument(
        'camera_device', default_value='/dev/usb_cam',
        description='Video device of the USB camera'
    )
    declare_camera_frame = DeclareLaunchArgument(
        'camera_frame', default_value='usb_cam_link',
        description='frame_id of the published images'
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
            ' use_dynamixel:=', use_dynamixel,
            ' use_shoulders:=', use_shoulders,
            ' use_dxl_right:=', use_dxl_right,
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
        arguments=['--ros-args',
            '--log-level', 'bender.controller_manager.hardware_component.system.DynamixelChainLeft:=error',
            '--log-level', 'bender.controller_manager.hardware_component.system.DynamixelChainRight:=error',
            '--log-level', 'dynamixel_hardware_interface:=error'],
        output='screen'
    )

    joint_state_broadcaster_spawner = spawner('joint_state_broadcaster')
    shoulders_on = AndSubstitution(use_arms, use_shoulders)
    arm_spawners = [spawner(name, IfCondition(shoulders_on)) for name in SHOULDER_CONTROLLERS]
    dynamixel_on = AndSubstitution(use_arms, use_dynamixel)
    arm_spawners += [spawner(name, IfCondition(dynamixel_on))
                     for name in DYNAMIXEL_LEFT_CONTROLLERS]
    arm_spawners += [spawner(name, IfCondition(AndSubstitution(dynamixel_on, use_dxl_right)))
                     for name in DYNAMIXEL_RIGHT_CONTROLLERS]
    base_spawners = [spawner(name, IfCondition(use_base)) for name in BASE_CONTROLLERS]

    # Luz del pecho (Pico W en /dev/encoders). El hardware ShoulderJoint solo existe
    # con use_arms y use_shoulders, y la state interface estop/pressed solo existe con
    # use_base (la exporta el Pioneer), así que sin base se lanza con el e-stop deshabilitado.
    chest_led_spawners = [
        spawner('chest_led_controller',
                IfCondition(AndSubstitution(shoulders_on, use_base))),
        spawner('chest_led_controller',
                IfCondition(AndSubstitution(shoulders_on, NotSubstitution(use_base))),
                extra_args=['--controller-ros-args=-p estop_interface:=""']),
    ]

    joy_node = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([joy_pkg, 'launch', 'joystick.launch.py'])
        ),
        condition=IfCondition(AndSubstitution(use_base, use_joy))
    )

    lidar_node = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([sensors_pkg, 'launch', 'lidar', 'hokuyo.launch.py'])
        ),
        # El link del lidar en el URDF se llama laser_1
        launch_arguments={'frame_id': 'laser_1'}.items(),
        condition=IfCondition(use_lidar)
    )

    camera_node = Node(
        package='usb_cam',
        executable='usb_cam_node_exe',
        name='usb_cam',
        namespace='usb_cam',
        parameters=[
            PathJoinSubstitution([sensors_pkg, 'params', 'camera', 'usb_cam.yaml']),
            {'video_device': camera_device, 'frame_id': camera_frame},
        ],
        output='screen',
        condition=IfCondition(use_camera)
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
        declare_use_dynamixel,
        declare_use_shoulders,
        declare_use_dxl_right,
        declare_use_base,
        declare_use_joy,
        declare_use_lidar,
        declare_use_camera,
        declare_camera_device,
        declare_camera_frame,
        robot_state_publisher,
        ros2_control_node,
        joint_state_broadcaster_spawner,
        *arm_spawners,
        *base_spawners,
        *chest_led_spawners,
        joy_node,
        lidar_node,
        camera_node,
        twist_mux,
    ])
