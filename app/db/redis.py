import logging

import redis

from app.config import REDIS_DB, REDIS_PORT, REDIS_HOST


def create_redis():
    try:
        rd = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
        logging.info("[create_redis()] start!")
    except:
        logging.error("redis connection failure")

    return rd


redis_db = create_redis()
