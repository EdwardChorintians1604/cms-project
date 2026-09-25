# Import all the models so that Base has them registered before Alembic imports
from app.core.database import Base
from app.models.user import User
from app.models.item import Item
