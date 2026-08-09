import redis
import json
from config import REDIS_URL

class RedisManager:
    def __init__(self):
        self.redis = redis.from_url(REDIS_URL, decode_responses=True)
    
    def set(self, key, value, expiry=None):
        self.redis.set(key, json.dumps(value), ex=expiry)
    
    def get(self, key):
        value = self.redis.get(key)
        return json.loads(value) if value else None
    
    def delete(self, key):
        self.redis.delete(key)
    
    def increment(self, key, amount=1):
        return self.redis.incrby(key, amount)
