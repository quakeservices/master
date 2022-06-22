import logging
from typing import Union


class LoggingMixin:
    # TODO: Different log levels
    def log(self, message: Union[str, bytes]):
        calling_class = self.__class__.__name__
        if isinstance(message, bytes):
            logging.debug(
                "{calling_class} - {message!r}".format(
                    calling_class=calling_class, message=message
                )
            )
        else:
            logging.debug(
                "{calling_class} - {message}".format(
                    calling_class=calling_class, message=message
                )
            )
