import argparse
from app import main

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="List of brokers")
    
    parser.add_argument(
        '--list', 
        type=str, 
        nargs='+',
        help='A list of brokers to connect to ', 
        required=True
    )
    
    args = parser.parse_args()
    
    main(args.list)

