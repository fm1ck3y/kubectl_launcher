import re

from setuptools import setup, find_packages
from os import path

HERE = path.abspath(path.dirname(__file__))


def readfile(*parts):
    with open(path.join(HERE, *parts), 'r') as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = readfile(*file_paths)
    version_match = re.search(
        r"^__version__ = ['\"]([^'\"]*)['\"]",
        version_file,
        re.M,
    )
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string')


setup(
    name='kubectl-launcher',
    version=find_version('src', 'kubectl_launcher', '__init__.py'),
    description='Kubectl start deployments,services and pvc.',
    url='https://github.com/fm1ck3y/kubectl_launcher',
    author='Artem Vdovin',
    author_email='arte.vdovin@gmail.com',
    license='Proprietary License',
    classifiers=[
        'Development Status :: 1 - Alpha',
        'License :: Other/Proprietary License',
        'Programming Language :: Python :: 3.8',
        'Operating System :: POSIX :: Linux'
    ],
    packages=find_packages(where='src', include=('kubectl_launcher*',)),
    package_dir={'kubectl_launcher': 'src/kubectl_launcher'},
    python_requires='>=3.7',
    install_requires=[
        'pyyaml>=5.3.1,<6',
        'kubernetes>=12.0.0',
        'requests>=2.25.1,<3',
        'jinja2>=2.11.3<3',
    ],
    package_data={
        'kubectl_launcher': ['templates/*']
    },
    entry_points={
        'console_scripts': [
            'kubectl-launcher = kubectl_launcher.main:main'
        ]
    }
)
