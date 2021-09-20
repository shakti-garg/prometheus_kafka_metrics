# prometheus_kafka_metrics
Prometheus instrumentation library for confluent-kafka-python applications. 

Plain and simple, it implements a metrics mapper which translate confluent-kafka's native metrics to prometheus format.

## Releases
This python package is released at PyPi: https://pypi.org/project/prometheus-kafka-metrics/.

Release is automated using git-webhook which triggers build and deployment at CircleCI pipeline(https://app.circleci.com/pipelines/github/shakti-garg/prometheus_kafka_metrics)

## Usage
Instantiate the relevant metrics manager and pass its send function as parameter to the kafka-client's callback `stats_cb`.


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


## References:
1) https://github.com/edenhill/librdkafka/blob/master/STATISTICS.md
2) https://www.datadoghq.com/blog/monitoring-kafka-performance-metrics/
