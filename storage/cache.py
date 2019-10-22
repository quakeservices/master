import logging
import pickle
import redis


class Cache():
    def __init__(self):
        logging.debug(f"{self.__class__.__name__ } - Initialising cache.")
        self.redis = redis.Redis(host='redis',
                                 port=6379,
                                 db=0,
                                 socket_timeout=3,
                                 socket_connect_timeout=5,
                                 socket_keepalive=True)

    def get(self, key):
        value = self.redis.get(key)
        if value:
            try:
                result = pickle.loads(value)
            except KeyError:
                logging.debug(f"{self.__class__.__name__ } - key error: possibly unpickled object?")
                result = value
            else:
                return result
        else:
            return False

    def set(self, key, value):
        logging.debug(f"{self.__class__.__name__ } - caching {value} as {key}.")
        value = pickle.dumps(value)
        try:
            self.redis.setex(key, timedelta(hours=1), value)
        except:
            return False
        else:
            return True

    def invalidate(self, key):
        logging.debug(f"{self.__class__.__name__ } - forcing {key} to expire.")
        self.redis.expire(key, 0)
