from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker 
import os 
from dotenv import load_dotenv

load_dotenv()
# get the database url from the environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

# create the database engine
engine = create_engine(DATABASE_URL)
session_local = sessionmaker(autocommit = False , autoflush = False , bind = engine ) 


# Base class for the models which will be used to create the tables
Base = declarative_base()



