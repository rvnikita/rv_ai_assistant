from sqlalchemy import create_engine, BigInteger, Boolean, Column, DateTime, Identity, Integer, JSON, PrimaryKeyConstraint, String, Text, UniqueConstraint, text, ForeignKey, Index, Time
from sqlalchemy.orm import Session, DeclarativeBase, declared_attr, relationship, backref
from sqlalchemy.sql.sqltypes import NullType
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func

import psycopg2
import psycopg2.extras
import os
import inspect #we need this to get current file name path
import traceback
import uuid
import threading
from contextlib import contextmanager

import src.helpers.logging_helper as logging_helper
import src.helpers.config_helper as config_helper

config = config_helper.get_config()
logger = logging_helper.get_logger()

def connect():
    conn = None
    try:
        conn = psycopg2.connect(user=config['DB']['DB_USER'],
                                password=config['DB']['DB_PASSWORD'],
                                host=config['DB']['DB_HOST'],
                                port=config['DB']['DB_PORT'],
                                database=config['DB']['DB_DATABASE'], cursor_factory=psycopg2.extras.RealDictCursor)
        return conn
    except (Exception, psycopg2.DatabaseError) as error:
        #write admin log mentioning file name and error
        logger.error(f"Error: {traceback.format_exc()}")

        return None


class Base(DeclarativeBase):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

#we will use thos for an example
# class User(Base):
#     __table_args__ = (
#         PrimaryKeyConstraint('id', name='user_pkey'),
#     )

#     id = Column(BigInteger, primary_key=True)
#     created_at = Column(DateTime(True), server_default=text('now()'))
#     first_name = Column(String)
#     last_name = Column(String)
#     username = Column(String)
#     is_bot = Column(Boolean)
#     is_anonymous = Column(Boolean)

#     user_statuses = relationship('User_Status', back_populates='user')


db_engine = create_engine(f"postgresql://{config['DB']['DB_USER']}:{config['DB']['DB_PASSWORD']}@{config['DB']['DB_HOST']}:{config['DB']['DB_PORT']}/{config['DB']['DB_DATABASE']}",
                          pool_size = 10,
                          max_overflow = 20)
Session = sessionmaker(bind=db_engine)

# Global counter for open sessions
open_session_count = 0
session_count_lock = threading.Lock() # not sure if we need this


@contextmanager
def session_scope():
    # global open_session_count

    # session_id = uuid.uuid4()  # Generate a unique session identifier for logging purposes
    # with session_count_lock:
    #     open_session_count += 1
    # logger.info(f"Starting a new database session {session_id}. Open sessions: {open_session_count}")

    session = Session()

    try:
        yield session
        session.commit()
        # logger.info(f"Session {session_id} committed successfully.")
    except Exception as error:
        session.rollback()
        # logger.error(f"Session {session_id} rollback due to error: {error}", exc_info=True)
        raise
    finally:
        session.close()
        # with session_count_lock:
            # open_session_count -= 1
        # logger.info(f"Database session {session_id} closed. Open sessions: {open_session_count}")