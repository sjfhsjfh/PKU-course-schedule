from setuptools import setup, find_packages

version = '0.1.0'

setup(
    name='PKUCourse',
    version=version,
    description='PKU Course python module',
    author='sjfhsjfh',
    author_email='sjfhsjfh@qq.com',
    url='https://github.com/sjfhsjfh/PKU-course-schedule',
    install_requires=[
        'git+https://github.com/sjfhsjfh/PKU-login-python.git',
    ],
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
)
