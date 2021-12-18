import argparse
import os
import sys
import shutil
import logging

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)
sys.path.append(ROOT_DIR)


from src.server import Server
from src.utils import get_log_path


# NOTE: instead of func -> class ServerArgParser
def parse_args():
    parser = argparse.ArgumentParser(description='sft-protocol-server description:')
    parser.add_argument('address', type=str,
                help='a required string positional argument, ip-adress of server')
    parser.add_argument('port', type=int,
                help='a required integer positional argument, port of server')
    args = parser.parse_args()
    return args


def get_log_fpath():
    # log folder (re)creating
    log_path = get_log_path()
    if log_path is None:
        print("Could not find SFT_ROOT environment variable")
        sys.exit(1)

    try:
        shutil.rmtree(log_path)
    except FileNotFoundError:
        pass
    except Exception as exc:
        print("Could not get an access to log folder", log_path, exc)
        sys.exit(1)

    try:
        os.makedirs(log_path)
    except Exception as exc:
        print("Could not create log folder", log_path, exc)
        sys.exit(1)

    log_path = os.path.join(log_path, "server.log")

    return log_path


if __name__ == '__main__':
    try:
        args = parse_args()
    except Exception as exp:
        print("Arguments parsing error")
        sys.exit(1)

    log_path = get_log_fpath()

    logging.basicConfig(
            format='%(asctime)s %(levelname)-8s %(message)s',
#            filename=log_path,
            level=logging.DEBUG)

    try:
        new_server = Server(args.address, args.port)
        new_server.start()
    except KeyboardInterrupt:
        print('Server is closed')
        sys.exit(0)
