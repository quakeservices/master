import asyncio
import signal
import functools
import logging

from masterserver import MasterServer


class Transport(object):
  def __init__(self, storage, headers):
    logging.debug(f"{__class__.__name__ } - Initialising transport.")
    self.bind = ('0.0.0.0', 27900)
    self.storage = storage
    self.headers = headers
    self.loop = asyncio.get_event_loop()
    self.signal()
    self.listener()

  def signal(self):
    logging.debug(f"{__class__.__name__ } - Setting up signals")
    signals = ('SIGINT', 'SIGTERM')
    for signame in signals:
      self.loop.add_signal_handler(getattr(signal, signame),
                                   functools.partial(self.shutdown, signame))

  def listener(self):
    logging.debug(f"{__class__.__name__ } - Setting up listener")
    self.listen = self.loop.create_datagram_endpoint(lambda: MasterServer(self.storage, self.headers),
                                                     local_addr=self.bind)

    self.transport, self.protocol = self.loop.run_until_complete(self.listen)

  def shutdown(self, signal):
    logging.debug(f"{__class__.__name__ } - Caught {signal}")
    self.transport.close()
    self.loop.stop()
