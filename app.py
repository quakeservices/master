#!/usr/bin/env python3

from headers import Headers
from storage import Storage
from transport import Transport
from masterserver import MasterServer

from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all


xray_recorder.configure(aws_xray_tracing_name='master')
plugins = ('ECSPlugin')
xray_recorder.configure(plugins=plugins)
patch_all()


def main():
  storage = Storage()
  master = MasterServer(Headers())
  transport = Transport(master)

  try:
    transport.loop.run_forever()
  finally:
    transport.loop.close()
    storage.close()

if __name__ == '__main__':
  main()
