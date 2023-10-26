import time
import backoff

from elasticsearch import Elasticsearch

@backoff.on_exception(backoff.constant, Exception, interval=1, max_tries=10, raise_on_giveup=False)
def es_try_connect(host):
    es_client = Elasticsearch(hosts=host, validate_cert=False, use_ssl=False)
    
    if es_client.ping():
        return True

if __name__ == '__main__':
    es_try_connect('http://localhost:9200')