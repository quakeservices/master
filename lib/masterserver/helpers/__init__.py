import logging
from typing import Union


class LoggingMixin:
    def log(self, message: Union[str, bytes]):
        if isinstance(message, bytes):
            logging.debug(
                "{calling_class} - {message!r}".format(
                    calling_class=self.__class__.__name__, message=message
                )
            )
        else:
            logging.debug(
                "{calling_class} - {message}".format(
                    calling_class=self.__class__.__name__, message=message
                )
            )
