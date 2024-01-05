from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.config import settings
import redis
from contextlib import contextmanager

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, pool_pre_ping=True, pool_size=20, max_overflow=10
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
REDIS_CLUSTER_MODE = settings.REDIS_CLUSTER_MODE


def get_db():
    try:
        db = SessionLocal()
        yield db
    except Exception as e:
        raise e
    finally:
        db.close()


@contextmanager
def get_task_db():
    try:
        db = SessionLocal()
        yield db
    except Exception as e:
        raise e
    finally:
        db.close()


def get_cache():
    if REDIS_CLUSTER_MODE == "0":
        return redis.Redis(host=settings.REDIS_HOST, port=6379, db=0)
    return redis.RedisCluster(host=settings.REDIS_HOST, port=6379)
