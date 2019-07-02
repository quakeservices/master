import asyncio
import signal
import functools


class Transport(object):
  def __init__(self, master):
    self.bind = ('0.0.0.0', 27900)
    self.master = master
    self.loop = asyncio.get_event_loop()
    self.signal()
    self.listener()
    self.run_until()

  def signal(self):
    signals = ('SIGINT', 'SIGTERM')
    for signame in signals:
      self.loop.add_signal_handler(getattr(signal, signame),
                                   functools.partial(self.shutdown, signame))

  def listener(self):
    self.listen = self.loop.create_datagram_endpoint(self.master,
                                                     local_addr=self.bind)

  def run_until(self):
    self.transport, self.protocol = self.loop.run_until_complete(self.listen)

  def shutdown(self):
    self.transport.close()
    self.loop.stop()

  def __del__(self):
    self.shutdown()
