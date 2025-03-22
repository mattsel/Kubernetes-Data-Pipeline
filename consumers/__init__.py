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
        '--threads',
        type=int,
        help='Amount of threads to process topics',
        required=False
    )

    args = parser.parse_args()
   
    batch = args.batch if args.batch is not None else 5000
    threads = args.thread if args.thread is not None else 15
    
    main(args.brokers, batch, threads)
