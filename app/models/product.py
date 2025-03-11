import uuid
import json
from datetime import datetime
from sqlalchemy.types import JSON
from . import db

# 商品活动关联表
product_promotions = db.Table('product_promotions',
    db.Column('product_id', db.String(36), db.ForeignKey('products.id'), primary_key=True),
    db.Column('promotion_id', db.String(36), db.ForeignKey('promotions.id'), primary_key=True)
)

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    points_price = db.Column(db.Integer, nullable=False)
    cash_price = db.Column(db.Numeric(10, 2))
    stock = db.Column(db.Integer, default=0)
    image_url = db.Column(db.String(255))
    category = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    attributes = db.Column(db.Text)  # 使用 Text 类型存储 JSON 字符串
    currency_id = db.Column(db.String(36), db.ForeignKey('currencies.id'))

    # 关系
    currency = db.relationship('Currency', backref='products')
    promotions = db.relationship('Promotion', secondary=product_promotions, lazy='subquery',
                               backref=db.backref('products', lazy=True))
    # 暂时注释掉未实现的关系
    # order_items = db.relationship('OrderItem', backref='product', lazy='dynamic')

    def __init__(self, name, points_price, description=None, cash_price=None,
                 stock=0, category=None, image_url=None, currency_id=None):
        self.name = name
        self.points_price = points_price
        self.description = description
        self.cash_price = cash_price
        self.stock = stock
        self.category = category
        self.image_url = image_url
        self.currency_id = currency_id
        self.attributes = json.dumps({})

    def update_stock(self, quantity):
        """更新商品库存"""
        if self.stock + quantity < 0:
            raise ValueError("Stock cannot be negative")
        self.stock += quantity
        db.session.commit()

    def check_availability(self, quantity):
        """检查商品是否有足够库存"""
        return self.is_active and self.stock >= quantity

    def get_active_promotions(self):
        """获取商品当前生效的促销活动"""
        now = datetime.utcnow()
        return [p for p in self.promotions if p.is_active and p.start_date <= now <= p.end_date]

    def calculate_final_price(self, quantity=1):
        """计算商品最终价格（考虑促销活动）"""
        base_points = self.points_price * quantity
        base_cash = float(self.cash_price or 0) * quantity

        # 获取当前有效的促销活动
        active_promotions = self.get_active_promotions()

        final_points = base_points
        final_cash = base_cash

        # 应用促销规则
        for promotion in active_promotions:
            rules = {}
            if promotion.rules:
                try:
                    rules = json.loads(promotion.rules)
                except:
                    rules = {}

            if promotion.promotion_type == 'DISCOUNT':
                discount = rules.get('discount', 1.0)
                final_points = int(final_points * discount)
                final_cash = float(final_cash * discount)
            elif promotion.promotion_type == 'FIXED_PRICE':
                final_points = rules.get('points_price', final_points)
                final_cash = float(rules.get('cash_price', final_cash))

        return {
            'original_points': base_points,
            'original_cash': base_cash,
            'final_points': final_points,
            'final_cash': final_cash,
            'quantity': quantity,
            'applied_promotions': [p.to_dict() for p in active_promotions]
        }

    def to_dict(self, include_promotions=False, include_admin_info=False):
        """将商品信息转换为字典"""
        # 基础信息，所有用户都可以看到
        result = {
            'id': str(self.id),
            'name': self.name,
            'description': self.description,
            'points_price': self.points_price,
            'cash_price': float(self.cash_price) if self.cash_price else None,
            'image_url': self.image_url,
            'category': self.category,
            'is_active': self.is_active,
            'stock': self.stock,  # 让所有用户都能看到库存信息
            'in_stock': self.stock > 0
        }

        # 管理员可以看到的额外信息
        if include_admin_info:
            result.update({
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'updated_at': self.updated_at.isoformat() if self.updated_at else None,
                'attributes': json.loads(self.attributes) if self.attributes else {},
                'currency': self.currency.code if self.currency else None
            })

        if include_promotions:
            result['active_promotions'] = [
                p.to_dict() for p in self.get_active_promotions()
            ]

        return result

class Currency(db.Model):
    __tablename__ = 'currencies'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code = db.Column(db.String(3), unique=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    symbol = db.Column(db.String(5))
    exchange_rate = db.Column(db.Numeric(10, 4), nullable=False, default=1.0)
    is_active = db.Column(db.Boolean, default=True)

class Promotion(db.Model):
    __tablename__ = 'promotions'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    promotion_type = db.Column(db.String(50), nullable=False)
    rules = db.Column(db.Text, nullable=False)  # 使用 Text 类型存储 JSON 字符串
    is_active = db.Column(db.Boolean, default=True)

    def to_dict(self):
        """将促销活动信息转换为字典"""
        rules = {}
        if self.rules:
            try:
                rules = json.loads(self.rules)
            except:
                rules = {}

        return {
            'id': str(self.id),
            'name': self.name,
            'description': self.description,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'promotion_type': self.promotion_type,
            'rules': rules,
            'is_active': self.is_active
        }