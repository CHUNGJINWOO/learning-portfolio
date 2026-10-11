from setuptools import setup

package_name = 'core_pubsub_py'

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
        'Concept-driven minimal Publisher/Subscriber package '
        'demonstrating Python OOP and ROS 2 Node integration.'
    ),
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'minimal_publisher = core_pubsub_py.minimal_publisher:main',
            'minimal_subscriber = core_pubsub_py.minimal_subscriber:main',
        ],
    },
)
