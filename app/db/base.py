from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

from app.users.models import User  
from app.tasks.models import Task