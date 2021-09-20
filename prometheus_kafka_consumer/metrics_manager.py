import json

from prometheus_client import Gauge

CONSUMER_METRIC_REPLY_QUEUE = Gauge('kafka_consumer_reply_queue',
                                    'Number of ops(callbacks, events, etc) waiting in queue to serve with poll',
                                    labelnames=['type', 'client_id'])
# equivalent to JMX's metric, records-consumed-rate
CONSUMER_METRIC_CONSUMED_RECORDS_RATE = Gauge('kafka_consumer_consumed_records_rate',
                                              'Average number of messages consumed (excluding ignored msgs) per second',
                                              labelnames=['type', 'client_id', 'topic', 'partition'])
# equivalent to JMX's metric, bytes-consumed-rate
CONSUMER_METRIC_CONSUMED_BYTES_RATE = Gauge('kafka_consumer_consumed_bytes_rate',
                                            'Average message bytes (including framing) consumed per second',
                                            labelnames=['type', 'client_id', 'topic', 'partition'])
# equivalent to JMX's metric, records-lag
CONSUMER_METRIC_RECORDS_LAG = Gauge('kafka_consumer_records_lag',
                                    'Number of messages consumer is behind producer on this partition',
                                    labelnames=['type', 'client_id', 'topic', 'partition'])


class ConsumerMetricsManager:
    def __init__(self):
        self.last_rxmsgs = {}
        self.last_rxbytes = {}

        self.last_ts = 0

    def send(self, stats_json_str):
        stats = json.loads(stats_json_str)

        type = stats['type']
        client_id = stats['client_id']

        ts_diff_sec = (stats['ts'] - self.last_ts)/1000000
        self.last_ts = stats['ts']

        for topic_name, topic_metrics in stats['topics'].items():
            if topic_name not in self.last_rxmsgs:
                self.last_rxmsgs[topic_name] = {}
            if topic_name not in self.last_rxbytes:
                self.last_rxbytes[topic_name] = {}

            for partition_name, partition_metrics in topic_metrics['partitions'].items():
                if partition_name not in self.last_rxmsgs[topic_name]:
                    self.last_rxmsgs[topic_name][partition_name] = 0
                if partition_name not in self.last_rxbytes[topic_name]:
                    self.last_rxbytes[topic_name][partition_name] = 0

                consumed_rate = (partition_metrics['rxmsgs'] - self.last_rxmsgs[topic_name][partition_name]
                                 ) / ts_diff_sec if ts_diff_sec > 0 else 0
                self.last_tx = stats['tx']
                self.last_rxmsgs[topic_name][partition_name] = partition_metrics['rxmsgs']

                consumed_bytes_rate = (partition_metrics['rxbytes'] - self.last_rxbytes[topic_name][partition_name]
                                       ) / ts_diff_sec if ts_diff_sec > 0 else 0
                self.last_rxbytes[topic_name][partition_name] = partition_metrics['rxbytes']

                CONSUMER_METRIC_CONSUMED_RECORDS_RATE.labels(type=type, client_id=client_id, topic=topic_name,
                                                             partition=partition_name).set(consumed_rate)
                CONSUMER_METRIC_CONSUMED_BYTES_RATE.labels(type=type, client_id=client_id, topic=topic_name,
                                                           partition=partition_name).set(consumed_bytes_rate)

                CONSUMER_METRIC_RECORDS_LAG.labels(type=type, client_id=client_id, topic=topic_name,
                                                   partition=partition_name).set(partition_metrics['consumer_lag'])

        CONSUMER_METRIC_REPLY_QUEUE.labels(type=type, client_id=client_id).set(stats['replyq'])