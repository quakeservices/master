#!/usr/bin/env python3
import logging
import sys

from headers import Headers
from storage import Storage
from transport import Transport
from masterserver import MasterServer

from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all


#xray_recorder.configure(aws_xray_tracing_name='master')
#plugins = ('ECSPlugin')
#xray_recorder.configure(plugins=plugins)
#patch_all()

def setup_logging(level='INFO'):
  log_level = getattr(logging, level.upper())

  logging.basicConfig(stream=sys.stdout,
                      level=log_level,
                      format='%(asctime)s %(levelname)s %(message)s',
                      datefmt='%Y-%m-%d %H:%M:%S')


def main():
  headers = Headers()
  storage = Storage()
  transport = Transport(storage, headers)

  try:
    transport.loop.run_forever()
  except:
    pass

if __name__ == '__main__':
  setup_logging('DEBUG')

  main()
