import os

from setuptools import setup, find_packages

work_dir = os.path.dirname(os.path.realpath(__file__))

setup(name='prometheus-kafka-metrics',
      version='0.4.2',
      description='Prometheus instrumentation library for confluent-kafka-python applications',
      url='https://github.com/shakti-garg/prometheus_kafka_metrics.git',
      author='Shakti Garg',
      author_email='shakti.garg@gmail.com',
      license='Apache License Version 2.0',
      packages=find_packages(exclude=("tests", "tests.*")),
      install_requires=['prometheus-client'],
      zip_safe=False)
