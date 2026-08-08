from setuptools import setup

package_name = 'camera'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='shahil',
    maintainer_email='shahil@todo.todo',
    description='Camera nodes for Raspberry Pi cameras',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'imx708_node = camera.imx708_publisher:main',
            'tof_node = camera.tof_publisher:main',
        ],
    },
)
