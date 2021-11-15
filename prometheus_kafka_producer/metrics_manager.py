import json

from prometheus_client import Gauge

PRODUCER_METRIC_REPLY_QUEUE = Gauge('kafka_producer_reply_queue',
                                    'Number of ops(callbacks, events, etc) waiting in queue to serve with poll',
                                    labelnames=['type', 'client_id'])
PRODUCER_METRIC_QUEUE_MSG_CNT = Gauge('kafka_producer_queue_msg_cnt',
                                      'Current number of messages in prometheus_kafka_producer queues',
                                      labelnames=['type', 'client_id'])
PRODUCER_METRIC_QUEUE_MSG_SIZE = Gauge('kafka_producer_queue_msg_size',
                                       'Current total size of messages in prometheus_kafka_producer queues',
                                       labelnames=['type', 'client_id'])
PRODUCER_METRIC_INFLIGHT_MSG_CNT = Gauge('kafka_producer_inflight_msg_cnt',
                                         'Number of messages in-flight to broker awaiting response',
                                         labelnames=['type', 'client_id'])
# sum of queue and broker latency is equivalent to JMX's metric, request-latency-avg
PRODUCER_METRIC_QUEUE_LATENCY_AVG = Gauge('kafka_producer_queue_latency_avg',
                                          'Average Producer queue latency in milliseconds',
                                          labelnames=['type', 'client_id'])
PRODUCER_METRIC_BROKER_LATENCY_AVG = Gauge('kafka_producer_broker_latency_avg',
                                           'Broker latency / round-trip time in milliseconds',
                                           labelnames=['type', 'client_id'])
# equivalent to JMX's metric, batch-size-avg
PRODUCER_METRIC_BATCH_SIZE_BYTES_AVG = Gauge('kafka_producer_batch_size_bytes_avg',
                                             'Average Batch sizes in bytes',
                                             labelnames=['type', 'client_id'])
PRODUCER_METRIC_BATCH_SIZE_AVG = Gauge('kafka_producer_batch_size_avg',
                                       'Average Batch message counts',
                                       labelnames=['type', 'client_id'])
# equivalent to JMX's metric, request-rate
PRODUCER_METRIC_REQUEST_RATE = Gauge('kafka_producer_request_rate',
                                     'Average number of requests sent per second',
                                     labelnames=['type', 'client_id'])
# equivalent to JMX's metric, outgoing-byte-rate
PRODUCER_METRIC_REQUEST_BYTES_RATE = Gauge('kafka_producer_request_bytes_rate',
                                           'Average number of requests bytes sent per second',
                                           labelnames=['type', 'client_id'])
# equivalent to JMX's metric, response-rate
PRODUCER_METRIC_RESPONSE_RATE = Gauge('kafka_producer_response_rate',
                                      'Average number of responses received per second',
                                      labelnames=['type', 'client_id'])
PRODUCER_METRIC_RESPONSE_BYTES_RATE = Gauge('kafka_producer_response_bytes_rate',
                                            'Average number of response bytes received per second',
                                            labelnames=['type', 'client_id'])


class ProducerMetricsManager:
    def __init__(self):
        self.last_tx = 0
        self.last_tx_bytes = 0

        self.last_rx = 0
        self.last_rx_bytes = 0

        self.last_ts = 0

    def send(self, stats_json_str):
        stats = json.loads(stats_json_str)

        type = stats['type']
        client_id = stats['client_id']

        queue_msg_cnt = stats['msg_cnt']
        queue_msg_size = stats['msg_size']

        ts_diff_sec = (stats['ts'] - self.last_ts)/1000000
        self.last_ts = stats['ts']

        request_rate = (stats['tx'] - (self.last_tx)/ts_diff_sec) if ts_diff_sec > 0 else 0
        self.last_tx = stats['tx']
        request_bytes_rate = (stats['tx_bytes'] - self.last_tx_bytes) / ts_diff_sec if ts_diff_sec > 0 else 0
        self.last_tx_bytes = stats['tx_bytes']

        response_rate = (stats['rx'] - self.last_rx) / ts_diff_sec if ts_diff_sec != 0 else 0
        self.last_rx_bytes = stats['rx_bytes']
        self.last_rx = stats['rx']
        response_bytes_rate = (stats['rx_bytes'] - self.last_rx_bytes) / ts_diff_sec if ts_diff_sec != 0 else 0
        self.last_rx_bytes = stats['rx_bytes']

        inflight_msg_cnt = 0
        int_latency_sum = 0
        int_latency_cnt = 0
        outbuf_latency_sum = 0
        outbuf_latency_cnt = 0
        rtt_sum = 0
        rtt_cnt = 0
        for broker_id, broker_metrics in stats['brokers'].items():
            queue_msg_cnt += broker_metrics['outbuf_msg_cnt']

            inflight_msg_cnt += broker_metrics['waitresp_msg_cnt']

            int_latency_sum += broker_metrics['int_latency']['sum']
            int_latency_cnt += broker_metrics['int_latency']['cnt']
            outbuf_latency_sum += broker_metrics['outbuf_latency']['sum']
            outbuf_latency_cnt += broker_metrics['outbuf_latency']['cnt']

            rtt_sum += broker_metrics['rtt']['sum']
            rtt_cnt += broker_metrics['rtt']['cnt']

        queue_avg_latency = (int_latency_sum / int_latency_cnt if (int_latency_cnt > 0) else 0) + \
                            (outbuf_latency_sum / outbuf_latency_cnt if (outbuf_latency_cnt > 0) else 0)

        batchsize_sum = 0
        batchsize_cnt = 0
        batchcnt_sum = 0
        batchcnt_cnt = 0
        for topic_name, topic_metrics in stats['topics'].items():
            batchsize_sum += topic_metrics['batchsize']['sum']
            batchsize_cnt += topic_metrics['batchsize']['cnt']

            batchcnt_sum += topic_metrics['batchcnt']['sum']
            batchcnt_cnt += topic_metrics['batchcnt']['cnt']

        PRODUCER_METRIC_REPLY_QUEUE.labels(type=type, client_id=client_id).set(stats['replyq'])

        PRODUCER_METRIC_QUEUE_MSG_CNT.labels(type=type, client_id=client_id).set(queue_msg_cnt)
        PRODUCER_METRIC_QUEUE_MSG_SIZE.labels(type=type, client_id=client_id).set(queue_msg_size)

        PRODUCER_METRIC_INFLIGHT_MSG_CNT.labels(type=type, client_id=client_id).set(inflight_msg_cnt)

        PRODUCER_METRIC_QUEUE_LATENCY_AVG.labels(type=type, client_id=client_id).set(queue_avg_latency/1000)
        PRODUCER_METRIC_BROKER_LATENCY_AVG.labels(type=type, client_id=client_id)\
            .set((rtt_sum / (1000*rtt_cnt)) if rtt_cnt > 0 else 0)

        PRODUCER_METRIC_BATCH_SIZE_BYTES_AVG.labels(type=type, client_id=client_id)\
            .set((batchsize_sum / batchsize_cnt) if batchsize_cnt > 0 else 0)
        PRODUCER_METRIC_BATCH_SIZE_AVG.labels(type=type, client_id=client_id)\
            .set((batchcnt_sum / batchcnt_cnt) if batchcnt_cnt > 0 else 0)

        PRODUCER_METRIC_REQUEST_RATE.labels(type=type, client_id=client_id).set(request_rate)
        PRODUCER_METRIC_REQUEST_BYTES_RATE.labels(type=type, client_id=client_id).set(request_bytes_rate)

        PRODUCER_METRIC_RESPONSE_RATE.labels(type=type, client_id=client_id).set(response_rate)
        PRODUCER_METRIC_RESPONSE_BYTES_RATE.labels(type=type, client_id=client_id).set(response_bytes_rate)