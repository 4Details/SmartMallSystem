import uuid
from datetime import datetime
from sqlalchemy.types import JSON
from . import db

class PointsTransaction(db.Model):
    __tablename__ = 'points_transactions'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    points = db.Column(db.Integer, nullable=False)  # 正数表示获得积分，负数表示消费积分
    transaction_type = db.Column(db.String(50), nullable=False)  # 例如：签到、购物、兑换等
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)  # 积分过期时间
    related_entity_id = db.Column(db.String(36))  # 关联实体ID（如订单ID）
    related_entity_type = db.Column(db.String(50))  # 关联实体类型（如order, product等）
    is_expired = db.Column(db.Boolean, default=False)

    def __init__(self, user_id, points, transaction_type, description=None,
                 expires_at=None, related_entity_id=None, related_entity_type=None):
        self.user_id = user_id
        self.points = points
        self.transaction_type = transaction_type
        self.description = description
        self.expires_at = expires_at
        self.related_entity_id = related_entity_id
        self.related_entity_type = related_entity_type

    @classmethod
    def create_transaction(cls, user_id, points, transaction_type, description=None,
                         expires_at=None, related_entity_id=None, related_entity_type=None):
        """创建新的积分交易记录"""
        transaction = cls(
            user_id=user_id,
            points=points,
            transaction_type=transaction_type,
            description=description,
            expires_at=expires_at,
            related_entity_id=related_entity_id,
            related_entity_type=related_entity_type
        )
        db.session.add(transaction)
        db.session.commit()
        return transaction

    def to_dict(self):
        """将交易记录转换为字典"""
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'points': self.points,
            'transaction_type': self.transaction_type,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'related_entity_id': str(self.related_entity_id) if self.related_entity_id else None,
            'related_entity_type': self.related_entity_type,
            'is_expired': self.is_expired
        }

    @classmethod
    def get_user_points_summary(cls, user_id):
        """获取用户积分汇总信息"""
        total_earned = db.session.query(db.func.sum(cls.points)).filter(
            cls.user_id == user_id,
            cls.points > 0,
            cls.is_expired == False
        ).scalar() or 0

        total_spent = abs(db.session.query(db.func.sum(cls.points)).filter(
            cls.user_id == user_id,
            cls.points < 0
        ).scalar() or 0)

        return {
            'total_earned': total_earned,
            'total_spent': total_spent,
            'current_balance': total_earned - total_spent
        }

    @classmethod
    def get_user_transactions(cls, user_id, page=1, per_page=20, transaction_type=None):
        """获取用户的积分交易历史"""
        query = cls.query.filter_by(user_id=user_id)

        if transaction_type:
            query = query.filter_by(transaction_type=transaction_type)

        return query.order_by(cls.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )