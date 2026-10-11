import os
from glob import glob
from setuptools import setup

package_name = 'tf2_transforms_py'

setup(
    name=package_name,
    version='1.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ROS 2 Learning Portfolio',
    maintainer_email='portfolio@example.com',
    description='ROS 2 Humble TF2 spatial coordinate transformations learning module.',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'static_frame_broadcaster = tf2_transforms_py.static_frame_broadcaster:main',
            'dynamic_frame_broadcaster = tf2_transforms_py.dynamic_frame_broadcaster:main',
            'point_transformer_listener = tf2_transforms_py.point_transformer_listener:main',
            'tf_lookup_diagnostics = tf2_transforms_py.tf_lookup_diagnostics:main',
        ],
    },
)
