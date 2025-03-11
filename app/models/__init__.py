from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# 导入模型以便在其他地方可以通过 app.models 访问
from .user import User, Role, MembershipLevel
from .product import Product, Promotion
from .points_transaction import PointsTransaction