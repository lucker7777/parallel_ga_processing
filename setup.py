from setuptools import setup

setup(
    name='parallel_ga_processing',
    version='1.0.1',
    packages=['examples', 'algorithmRunners', 'geneticAlgorithms'],
    url='https://github.com/lucker7777/parallelGA',
    license='',
    install_requires=[
          'scoop', 'pip', 'numpy'
      ],
    author='Martin Tuleja',
    author_email='holanga4321@gmail.com',
    description='This package provides tools for processing hard problems with parallel genetic '
                'algorithm.',
    include_package_data=True
)
