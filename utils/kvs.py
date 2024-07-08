import time
import threading

from pymemcache.client.base import Client
from pymemcache.client.base import PooledClient
import redis


class Memcached:
    def __init__(self, connect_host):
        self.host = connect_host

    def get_client(self):
        return PooledClient(self.host)

    def set(key, value):
        cli = self.get_client()
        cli.set(key, value)

    def get(key):
        cli = self.get_client()
        return cli.get(key)


class Redis:
    def __init__(self, conn_host, conn_port=6379):
        self.redis_pool = redis.ConnectionPool(
                host=conn_host,
                port=conn_port,
                db=0,  )

    def get_connection(self):
        return redis.StrictRedis(connection_pool = self.redis_pool )

    def broadcast(self, msg, channel_name):
        conn = self.get_connection()
        # pubsub = conn.pubsub()

        return conn.publish(channel_name, msg)

    def add_subscriber(self, channel_name):
        return add_subscriber_list( [channel_name])

    def add_subscriber_list(self, channel_list):
        conn = self.get_connection()
        pubsub = conn.pubsub(ignore_subscribe_messages=True)
        # pubsub = conn.pubsub()
        pubsub.subscribe(*channel_list)

        return pubsub


    def remove_subscriber(self, channel_name):
        conn = self.get_connection(conn_host, conn_port)
        # pubsub = conn.pubsub(ignore_subscribe_messages=True)
        pubsub = conn.pubsub()
        pubsub.unsubscribe(channel_name )

        return pubsub

    def set(key, value):
        pass

    def get(key):
        pass


