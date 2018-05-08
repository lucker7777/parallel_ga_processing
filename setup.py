from setuptools import setup

setup(
    name='parallel_ga_processing',
    version='2.0.9',
    packages=['parallel_ga_processing',
              'parallel_ga_processing.algorithmRunners',
              'parallel_ga_processing.geneticAlgorithms'],
    url='https://github.com/lucker7777/parallelGA',
    license='',
    install_requires=[
          'scoop', 'pika', 'numpy', 'jsonpickle'
      ],
    author='Martin Tuleja',
    author_email='holanga4321@gmail.com',
    description='This package provides tools for processing hard problems with parallel genetic '
                'algorithm.',
    include_package_data=True
)
