# prometheus_kafka_metrics
Prometheus instrumentation library for confluent-kafka-python applications. 

Plain and simple, it implements a metrics mapper which translate confluent-kafka's native metrics to prometheus format.

## Releases
This python package is released at PyPi: https://pypi.org/project/prometheus-kafka-metrics/.

Release is automated using git-webhook which triggers build and deployment at CircleCI pipeline(https://app.circleci.com/pipelines/github/shakti-garg/prometheus_kafka_metrics)

## Usage
instantiate the relevant metrics manager and provide the send function as parameter to `stats_cb` :

```pycon
from confluent_kafka import Producer
from prometheus_kafka_producer.metrics_manager import ProducerMetricsManager

metric_manager = ProducerMetricsManager()
conf = {'bootstrap.servers': brokers,
        'stats_cb': metric_manager.send
        }
Producer(conf)

```

## References:
1) https://github.com/edenhill/librdkafka/blob/master/STATISTICS.md
2) https://www.datadoghq.com/blog/monitoring-kafka-performance-metrics/
