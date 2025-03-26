import threading
from typing import List
from kafka.errors import KafkaError
from Consumer import Consumer
from Elk import Elk
from env import logger

def consume_partition(brokers: List[str], topic: str, batch: int, partition: int) -> None:
    # Instantiates an Elk object to post logs to Elasticsearch
    elk = Elk()
    consumer = Consumer(topic, brokers, batch)
    consumer.assign_topic_partition(partition)
    try:
        while True:
            # Timeout to avoid blocking
            messages = consumer.client.poll(timeout_ms=100)
            
            if messages is None:
                continue
            
            # Check for errors in the message
            for message in messages:
                if message.error():
                    # Continues polling if no messages are left
                    if message.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    else:
                        # Since this is not an EOF, we want to log the error
                        raise KafkaError(message.error())

            batch_logs = []
            for message in messages:
                logger.info(message.value().decode('utf-8'))
                log = elk.to_dict(message.value().decode('utf-8'))
                if log is None:
                    continue
                batch_logs.append(log)
                if len(batch_logs) != consumer.batch:
                    elk.post_to_elk(index="service-logs", document=batch_logs)
                    batch_logs = []
            
            # Posts remaining logs & commit offset to avoid reprocessing
            if batch_logs:
                elk.post_to_elk(index="service-logs", document=batch_logs)
            consumer.client.commit()
    except Exception as e:
        logger.error(f"Error consuming messages: {e}")
    except KeyboardInterrupt:
        logger.warning("Consumer interrupted by user")
    finally:
        consumer.close()

def main(brokers: List[str], batch: int, topic: str) -> None:
    try:
        # Creates consumer client and gets the topic's partitions
        consumer = Consumer(topic, brokers, batch)
        partitions = consumer.get_topic_partitions()
    except Exception as e:
        logger.error(f"Error getting topic partitions: {e}")
        return

    try:
        # Generates a thread for each partition
        threads = []
        for partition in partitions:
            thread = threading.Thread(target=consume_partition, args=(brokers, topic, batch, partition,))
            thread.start()
            threads.append(thread)

        # Gracefully waits for all threads to finish
        for thread in threads:
            thread.join()
    except Exception as e:
        logger.error(f"Error while assigning threads: {e}")
        return