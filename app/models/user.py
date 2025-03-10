import uuid
import json
from datetime import datetime
from passlib.hash import pbkdf2_sha256
from sqlalchemy.types import JSON
from . import db

# 用户角色关联表
user_roles = db.Table('user_roles',
    db.Column('user_id', db.String(36), db.ForeignKey('users.id'), primary_key=True),
    db.Column('role_id', db.String(36), db.ForeignKey('roles.id'), primary_key=True)
)

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    salt = db.Column(db.String(32), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    avatar_url = db.Column(db.String(255))
    address = db.Column(db.String(255))
    preferences = db.Column(db.Text)  # 使用 Text 类型存储 JSON 字符串
    membership_level_id = db.Column(db.String(36), db.ForeignKey('membership_levels.id'))

    # 关系
    points_transactions = db.relationship('PointsTransaction', backref='user', lazy='dynamic')
    # 暂时注释掉未实现的关系
    # orders = db.relationship('Order', backref='user', lazy='dynamic')
    # behaviors = db.relationship('UserBehavior', backref='user', lazy='dynamic')
    # notifications = db.relationship('Notification', backref='user', lazy='dynamic')
    roles = db.relationship('Role', secondary=user_roles, lazy='subquery',
                            backref=db.backref('users', lazy=True))

    membership_level = db.relationship('MembershipLevel', backref='users')

    def __init__(self, username, email, password, phone=None, address=None):
        self.username = username
        self.email = email
        self.phone = phone
        self.address = address
        self.salt = uuid.uuid4().hex
        self.password_hash = self._hash_password(password)
        self.preferences = json.dumps({})

    def _hash_password(self, password):
        return pbkdf2_sha256.hash(password + self.salt)

    def verify_password(self, password):
        return pbkdf2_sha256.verify(password + self.salt, self.password_hash)

    def update_password(self, new_password):
        self.salt = uuid.uuid4().hex
        self.password_hash = self._hash_password(new_password)

    def get_points_balance(self):
        """获取用户当前积分余额"""
        from .points_transaction import PointsTransaction
        total_points = db.session.query(db.func.sum(PointsTransaction.points)).filter(
            PointsTransaction.user_id == self.id,
            PointsTransaction.is_expired == False
        ).scalar() or 0
        return total_points

    def to_dict(self, include_private=False):
        """将用户对象转换为字典"""
        result = {
            'id': str(self.id),
            'username': self.username,
            'email': self.email if include_private else None,
            'phone': self.phone if include_private else None,
            'is_active': self.is_active,
            'avatar_url': self.avatar_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'membership_level': self.membership_level.name if self.membership_level else None,
            'points_balance': self.get_points_balance()
        }

        if include_private:
            preferences = {}
            if self.preferences:
                try:
                    preferences = json.loads(self.preferences)
                except:
                    preferences = {}

            result.update({
                'address': self.address,
                'preferences': preferences,
                'roles': [role.name for role in self.roles]
            })

        return result

class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系通过user_roles和role_permissions表定义

class MembershipLevel(db.Model):
    __tablename__ = 'membership_levels'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255))
    required_points = db.Column(db.Integer, nullable=False)
    benefits = db.Column(db.Text)  # 使用 Text 类型存储 JSON 字符串
    color_code = db.Column(db.String(10))

    # 关系
    benefits_list = db.relationship('Benefit', backref='membership_level', lazy='dynamic')

class Benefit(db.Model):
    __tablename__ = 'benefits'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    membership_level_id = db.Column(db.String(36), db.ForeignKey('membership_levels.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    benefit_type = db.Column(db.String(50), nullable=False)
    value = db.Column(JSON)