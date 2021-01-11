from setuptools import setup

setup(
    name='tower',
    packages=['tower'],
    include_package_data=True,
    install_requires=[
        'flask',
        'requests',
        'pytest',
    ],
)
