import uuid
from datetime import datetime
from . import db

class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    total_points = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='PENDING')  # PENDING, COMPLETED, CANCELLED
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联
    user = db.relationship('User', backref='orders')
    items = db.relationship('OrderItem', backref='order', lazy='dynamic')

    def to_dict(self):
        """将订单信息转换为字典"""
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'total_points': self.total_points,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'items': [item.to_dict() for item in self.items]
        }

class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = db.Column(db.String(36), db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.String(36), db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    points_price = db.Column(db.Integer, nullable=False)  # 记录兑换时的积分价格
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 关联
    product = db.relationship('Product')

    def to_dict(self):
        """将订单项信息转换为字典"""
        return {
            'id': str(self.id),
            'order_id': str(self.order_id),
            'product_id': str(self.product_id),
            'product_name': self.product.name if self.product else None,
            'quantity': self.quantity,
            'points_price': self.points_price,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }