import time

import redis
import backoff

@backoff.on_exception(backoff.constant, Exception, interval=1, max_tries=10, raise_on_giveup=False)
def redis_try_connect(host, port):
    redis_client = redis.Redis(host=host, port=port, decode_responses=True)
    
    if redis_client.ping():
        return True

if __name__ == '__main__':
    redis_try_connect(host='localhost', port=6379)