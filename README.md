![License](https://img.shields.io/github/license/shakti-garg/prometheus_kafka_metrics)
![Open Issues](https://img.shields.io/github/issues-raw/shakti-garg/prometheus_kafka_metrics)
![Contributors](https://img.shields.io/github/contributors/shakti-garg/prometheus_kafka_metrics)

![Build Status](https://img.shields.io/circleci/build/github/shakti-garg/prometheus_kafka_metrics/master)
![Version](https://img.shields.io/pypi/v/prometheus-kafka-metrics)
![Downloads](https://img.shields.io/pypi/dm/prometheus-kafka-metrics)

# prometheus_kafka_metrics
Prometheus instrumentation library for confluent-kafka-python applications. 

Plain and simple, it implements a metrics mapper which translate confluent-kafka's native metrics to prometheus format.

## Releases
This python package is released at PyPi: https://pypi.org/project/prometheus-kafka-metrics/.

Release is automated using git-webhook which triggers build and deployment at CircleCI pipeline(https://app.circleci.com/pipelines/github/shakti-garg/prometheus_kafka_metrics)

## Usage

1. Instantiate the relevant metrics manager and pass its send function as parameter to the kafka-client's callback `stats_cb`.


For confluent-kafka producer:

```pycon
from confluent_kafka import Producer
from prometheus_kafka_producer.metrics_manager import ProducerMetricsManager

metric_manager = ProducerMetricsManager()
conf = {'bootstrap.servers': brokers,
        'stats_cb': metric_manager.send
        }
Producer(conf)

```

Similary, for confluent-kafka consumer:

```pycon
from confluent_kafka import Consumer
from prometheus_kafka_consumer.metrics_manager import ConsumerMetricsManager

metric_manager = ConsumerMetricsManager()
conf = {'bootstrap.servers': brokers,
        'group.id': consumer_group_id,
        'stats_cb': metric_manager.send
        }
Consumer(conf)

```


2. Publish the generated prometheus metrics at a http port. In case you are not using any relevant framework, it can be done naively like below:

```pycon
from prometheus_client import start_http_server

if __name__ == '__main__':
    start_http_server(8000)
```


## References:
1) https://github.com/edenhill/librdkafka/blob/master/STATISTICS.md
2) https://www.datadoghq.com/blog/monitoring-kafka-performance-metrics/
