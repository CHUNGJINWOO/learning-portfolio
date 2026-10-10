from setuptools import find_packages, setup

package_name = 'my_package_rclcpy'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='cjinw',
    maintainer_email='cjinw@todo.todo',
    description='ROS 2 Humble Python learning examples: nodes, topics, and services.',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'my_first_node = my_package_rclcpy.my_first_node:main',
            'talker = my_package_rclcpy.talker:main',
            'listener = my_package_rclcpy.listener:main',
            'add_two_ints_server = my_package_rclcpy.add_two_ints_server:main',
            'add_two_ints_client = my_package_rclcpy.add_two_ints_client:main',
        ],
    },
)
