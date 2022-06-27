import logging
import threading
from typing import Union


class LoggingMixin:
    def _get_logger(self):
        return logging.getLogger(__name__)

    def log(self, message: Union[str, bytes]):
        logger = self._get_logger()
        calling_class: str = self.__class__.__name__
        current_thread: str = threading.current_thread().name
        if isinstance(message, bytes):
            logger.debug(
                "{calling_class} - {current_thread} - {message!r}".format(
                    calling_class=calling_class,
                    current_thread=current_thread,
                    message=message,
                )
            )
        else:
            logger.debug(
                "{calling_class} - {current_thread} - {message}".format(
                    calling_class=calling_class,
                    current_thread=current_thread,
                    message=message,
                )
            )
