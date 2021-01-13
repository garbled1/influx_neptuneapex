from setuptools import setup

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="influx_neptuneapex",
    version="1.1",
    description="Feed data from a neptune apex into an InfluxDB",
    license='GPL',
    packages=['influx_neptuneapex'],
    author='Tim Rightnour',
    author_email='thegarbledone@gmail.com',
    url='https://github.com/garbled1/influx_neptuneapex',
    project_urls={
        'Gitub Repo': 'https://github.com/garbled1/influx_neptuneapex',
    },
    install_requires=[
        'influxdb',
        'requests'
    ],
    python_requires='>3.5',
    long_description=long_description,
    long_description_content_type='text/markdown',
    entry_points={
        'console_scripts': [
            'influx_neptuneapex=influx_neptuneapex.__main__:main'
        ]
    }
)
