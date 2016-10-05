import hashlib
import random
import itertools
import string
import logging
from datetime import datetime
from locust import Locust, events
from pymemcache.client.base import Client


LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
                '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)

class MemcachedLocust(Locust):
    """
    Represents a memcached client, in this situation defined as
    an agent that will be making verious memcached calls like
    an application that relies heavily on caching would.
    """

    client = None
    """
    Instance of pymemcache client
    """

    min_set_size = 1000
    """
    The minimum set size, in bytes. This is used to determine the
    size of values that are set randomly.
    """

    max_set_size = 1000
    """
    The maximum set size, in bytes. This is used to determine the
    maximum size of values that are set.
    """

    number_of_keys = 100
    """
    The number of keys to pool for setting/getting.
    """

    simulate_miss_ratio = 0.0
    """
    Ratio of gets to simulate misses
    """

    def __init__(self):
        super(MemcachedLocust, self).__init__()
        if self.host is None:
            raise LocustError("You must specify the base host. Either in the host attribute in the Locust class, or on the command line using the --host option.")
        self.client = LocustMemcachedClient(
                (self.host, 11211),
                number_of_keys=self.number_of_keys)
        self.client.max_set_size = self.max_set_size
        self.client.min_set_size = self.min_set_size


class LocustMemcachedClient(Client):
    """
    A wrapper for pymemcache.client.base.Client that provides some
    convenience methods
    """
    _computed_keys = []

    def __init__(self, conn, number_of_keys):
        super(LocustMemcachedClient, self).__init__(conn, no_delay=True)

        for key in xrange(number_of_keys):
            m = hashlib.md5()
            m.update("{}".format(key))
            self._computed_keys.append(m.hexdigest())
        self._computed_keys = itertools.cycle(self._computed_keys)


    def random_set(self):
        watch = StopWatch()
        length = random.randint(self.min_set_size, self.max_set_size)
        value = ''.join(random.choice(string.lowercase) for x in range(length))
        key = self._computed_keys.next()

        name = "small value"
        if length > 500000:
            name = "big value"
        try:
            watch.start()
            self.set(key, value)
            LOGGER.info('SET {}'.format(key))
        except Exception as e:
            events.request_failure.fire(
                request_type="set",
                name=name,
                response_time=watch.elapsed_time(),
                exception=e
            )
        else:
            events.request_success.fire(
                request_type="set",
                name=name,
                response_time=watch.elapsed_time(),
                response_length=length
            )
            
    def random_get(self):
        watch = StopWatch()
        key = self._computed_keys.next()

        watch.start()
        result = self.get(key)

        name = "small value"
        if not result:
            name = "no value"
        elif len(result) > 500000:
            name = "big value"

        if result:
            events.request_success.fire(
                request_type="get",
                name=name,
                response_time=watch.elapsed_time(),
                response_length=len(result)
            )
        else:
            events.request_failure.fire(
                request_type="get",
                name=name,
                response_time=watch.elapsed_time(),
                exception=Exception("Key {} not found".format(key)),
            )


class StopWatch(object):
    def start(self):
        self._start = datetime.now()

    def elapsed_time(self):
        timedelta = datetime.now() - self._start
        return timedelta.total_seconds() * 1000



