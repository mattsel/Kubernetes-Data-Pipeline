import argparse
from app import main

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="List of brokers")
    parser.add_argument(
        '--brokers',
        type=str,
        nargs='+',
        help='A list of brokers to connect to',
        required=True
    )
    parser.add_argument(
        '--batch',
        type=int,
        help='Batch size to send to ELK',
        required=False
    )
    parser.add_argument(
        '--topic',
        type=str,
        help='Name of the topic to parse',
        required=False
    )

    args = parser.parse_args()
   
    batch = args.batch if args.batch is not None else 1000
    topic = args.topic if args.topic is not None else "service-logs"
    
    main(args.brokers, batch, topic)
