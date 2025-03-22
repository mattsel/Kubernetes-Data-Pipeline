from typing import List
from KafkaClient import KafkaClient


def main(brokers: List[str]) -> None:
    kafka_client = KafkaClient(brokers)

