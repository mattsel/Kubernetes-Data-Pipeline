import threading
from typing import List, Optional
from KafkaClient import KafkaClient
from consumers import Consumer
from Elk import Elk
from env import logger

def consume_partition(topic_name: str, brokers: List[str], partition: int, batch: int) -> None:
    # Generates consumer client to consume messages from a partition
    consumer = Consumer(topic_name, brokers, partition)
    consumer_client = consumer.get_consumer_client()
    # Instantiates an Elk object to post logs to Elasticsearch
    elk = Elk()
    try:
        while True:
            # Timeout to avoid blocking
            messages = consumer.poll(timeout=1.0)
            
            if messages is None:
                continue
            
            if messages.error():
                # Continues polling if not messages are left
                if messages.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    # Since this is not an EOF, we would like to know the issue
                    raise KafkaException(messages.error())
            
            batch_logs = []
            for message in messages:
                log = elk.to_dict(message.value().decode('utf-8'))
                if log is None:
                    continue
                batch_logs.append(log)
                if len(batch_logs) == batch:
                    elk.post_to_elk(index="service-logs", document=batch_logs)
                    batch_logs = []
            
            # Posts remaining logs & commit offset to avoid reprocessing
            elk.post_to_elk(index="service-logs", document=batch_logs)
            consumer.commit()
    except Exception as e:
        logger.error(f"Error consuming messages: {e}")
    except KeyboardInterrupt:
        logger.warning("Consumer interrupted by user")
    finally:
        consumer.close()

def main(brokers: List[str], batch: int, topic: str) -> None:
    try:
        # Connects to kafka client and gets topic partitions
        kafka_client = KafkaClient(brokers, topic)
        partitions = kafka_client.get_topic_partitions()
        if kafka_client.get_topic_partitions() == []:
            raise Exception()
        kafka_client.close()
    except Exception as e:
        logger.error(f"Error getting topic metadata: {e}")
    try:
        # Generates a thread for each partition
        threads = []
        for partition in partitions:
            thread = threading.Thread(target=consume_partitions, args=(topic, brokers, partition, batch))
            thread.start()
            threads.append(thread)

        # Gracefully waits for all threads to finish
        for thread in threads:
            thread.join()
    except Exception as e:
        logger.error(f"Error while assigning threads: {e}")
