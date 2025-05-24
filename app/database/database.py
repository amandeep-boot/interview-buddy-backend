from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker 
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os 

load_dotenv()
# get the database url from the environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

# create the database engine
engine = create_engine(DATABASE_URL ,pool_pre_ping=True )
session_local = sessionmaker(autocommit = False , autoflush = False , bind = engine ) 


# Base class for the models which will be used to create the tables
Base = declarative_base()



