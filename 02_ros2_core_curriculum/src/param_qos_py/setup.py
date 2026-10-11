from setuptools import setup

package_name = 'param_qos_py'

setup(
    name=package_name,
    version='1.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/config', ['config/default_params.yaml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ROS 2 Learning Portfolio',
    maintainer_email='portfolio@example.com',
    description=(
        'Concept-driven ROS 2 Parameters and QoS module demonstrating '
        'atomic validation, parameter events, and DDS QoS policies.'
    ),
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'dynamic_telemetry_publisher = param_qos_py.dynamic_telemetry_publisher:main',
            'qos_sensor_streamer = param_qos_py.qos_sensor_streamer:main',
            'qos_sensor_listener = param_qos_py.qos_sensor_listener:main',
            'qos_config_publisher = param_qos_py.qos_config_publisher:main',
            'qos_config_listener = param_qos_py.qos_config_listener:main',
        ],
    },
)
