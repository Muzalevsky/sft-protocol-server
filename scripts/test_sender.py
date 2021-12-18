import argparse
import sys
import requests

def parse_args():
    parser = argparse.ArgumentParser(description='sft-protocol-server description:')
    parser.add_argument('address', type=str,
                help='IP adress of server')
    parser.add_argument('port', type=int,
                help='Port of server')
    parser.add_argument('file', type=str,
                help='Protocol file')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    try:
        args = parse_args()
    except Exception as exp:
        print("Arguments parsing error")
        sys.exit(1)

    with open(args.file) as f:
        read_data = f.read()

    requests.post(f"http://{args.address}:{args.port}", read_data, headers={"protocolId":"1"})
