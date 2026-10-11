from setuptools import setup

package_name = 'service_action_py'

setup(
    name=package_name,
    version='1.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ROS 2 Learning Portfolio',
    maintainer_email='portfolio@example.com',
    description=(
        'Concept-driven ROS 2 Services and Actions module demonstrating '
        'request-response communication and goal-feedback-cancel lifecycle.'
    ),
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'add_two_ints_server = service_action_py.add_two_ints_server:main',
            'add_two_ints_client = service_action_py.add_two_ints_client:main',
            'fibonacci_action_server = service_action_py.fibonacci_action_server:main',
            'fibonacci_action_client = service_action_py.fibonacci_action_client:main',
        ],
    },
)
