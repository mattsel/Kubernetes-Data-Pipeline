import threading
from typing import List, Optional
from KafkaClient import KafkaClient
from consumers import Consumer
from Elk import Elk
from env import logger
def consume_partition(topic_name: str, brokers: List[str], partition: int, batch: int) -> None:
    consumer = Consumer(topic_name, brokers, partition)
    consumer_client = consumer.get_consumer_client()
    elk = Elk()
    try:
        while True:
            messages = consumer.poll(timeout=1.0)

            if messages is None:
                continue

            if messages.error():
                if messages.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    raise KafkaException(messages.error())

            count = 0
            for message in messages:
                log = elk.to_dict(message.value().decode('utf-8'))
                if log is None:
                    continue
                count += 1
                if count == batch:
                    elk.post_to_elk(index="service-logs", document=log)
                    count = 0
                elk.post_to_elk(index="service-logs", document=log)
                count = 0

    except KeyboardInterrupt:
        logger.warning("Consumer interrupted by user")
    finally:
        consumer.close()

def main(brokers: List[str], batch: int, topic: str) -> None:
    try:
        kafka_client = KafkaClient(brokers, topic)
        partitions = kafka_client.get_topic_partitions()
        if kafka_client.get_topic_partitions() == []:
            raise Exception()
        kafka_client.close()
    except Exception as e:
        logger.error(f"Error getting topic metadata: {e}")
    try:
        threads = []
        for partition in partitions:
            thread = threading.Thread(target=consome_partitions, args=(topic, brokers, partition, batch,))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()
    except Exception as e:
        logger.error(f"Error while assigning threads: {e}")
