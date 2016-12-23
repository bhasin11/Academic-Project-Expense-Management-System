from functools import wraps
from datetime import datetime, timedelta
from time import sleep
import redis




r_server = redis.Redis("127.0.0.1")
str = ''
portStatus = {}


class CircuitBreaker(object):
    def __init__(self, name=None, expected_exception=Exception, max_failure_to_open=1, reset_timeout=10):
        self._name = name
        self._expected_exception = expected_exception
        self._max_failure_to_open = max_failure_to_open
        self._reset_timeout = reset_timeout
        # Set the initial state
        self.close()
        self.i = -1

    def close(self):
        self._is_closed = True
        self._failure_count = 0

    def open(self):
        self._is_closed = False
        self._opened_since = datetime.utcnow()

    def __call__(self, func):
        if self._name is None:
            self._name = func.__name__

        @wraps(func)
        def with_circuitbreaker(*args, **kwargs):
            return self.call(func, *args, **kwargs)

        return with_circuitbreaker

    def call(self, func, *args, **kwargs):
        ins = Instanes()
        global str

        while (True):

            self.i += 1
            self.i %= ins.getLength()
            port = ins.getInstance(self.i)
            print 'current port is', port

            if port not in portStatus:

                portStatus[port] = self._max_failure_to_open - 1

            newList = list(args)
            newList[3] = port
            args = tuple(newList)

            if (len(portStatus) == 0):
                break

            try:
                result = func(*args, **kwargs)
                if (result == 'SUCCESS'):
                    break
                else:
                    t = portStatus[port]
                    portStatus[port] = t - 1
                    if (t == 0):
                        print '{} removed'.format(port)
                        r_server.lrem("FINAL", port, 0)

                        del portStatus[port]

                    if(len(portStatus) ==0 ):
                        break


            except Exception as ex:
                print ex
                break



class Instanes:

    def __init__(self):
        self.instances = r_server.lrange("FINAL", 0, r_server.llen("FINAL"))

    def getInstance(self,i):
        return self.instances[i]

    def getLength(self):
        return len(self.instances)