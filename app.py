#!/usr/bin/env python3
import logging
import sys
import argparse

from protocols import Protocols
from storage import Storage
from transport import Transport
from masterserver import MasterServer

from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

xray_recorder.configure()
patch_all()

def gather_args():
  parser = argparse.ArgumentParser(description='Master Server for idTech servers.')
  parser.add_argument('--debug', dest='debug', action="store_true")
  return parser.parse_args()


def setup_logging(level='INFO'):
  log_level = getattr(logging, level.upper())

  logging.basicConfig(stream=sys.stdout,
                      level=log_level,
                      format='%(asctime)s %(levelname)s %(message)s',
                      datefmt='%Y-%m-%d %H:%M:%S')


def main():
  protocols = Protocols()
  storage = Storage()
  master = MasterServer(storage, protocols)
  transport = Transport(master)

  try:
    transport.loop.run_forever()
  except:
    pass

if __name__ == '__main__':
  args = gather_args()

  if args.debug:
    setup_logging('DEBUG')
  else:
    setup_logging()

  logging.info(f"Starting master server.")
  main()
  logging.info(f"Master server stopped.")
