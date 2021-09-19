# prometheus_kafka_metrics
 Prometheus metrics mapper for confluent-kafka-python applications

# Usage
instantiate the relevant metrics manager and provide the send function as parameter to `metrics_cb` :

```pycon
from confluent_kafka import Producer
from prometheus_kafka_producer.metrics_manager import ProducerMetricsManager

metrics = ProducerMetricsManager()
conf = {'bootstrap.servers': brokers,
        'stats_cb': metrics.send
        }
Producer(conf)

```

# References:
1) https://github.com/edenhill/librdkafka/blob/master/STATISTICS.md
2) https://www.datadoghq.com/blog/monitoring-kafka-performance-metrics/
