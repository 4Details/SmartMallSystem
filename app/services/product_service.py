from datetime import datetime
from ..models import db
from ..models.product import Product, Promotion, Currency
from ..utils.exceptions import ProductNotFoundError, InsufficientStockError

class ProductService:
    @staticmethod
    def create_product(name, points_price, description=None, cash_price=None,
                       stock=0, category=None, image_url=None, currency_id=None, attributes=None):
        """创建新商品"""
        product = Product(
            name=name,
            points_price=points_price,
            description=description,
            cash_price=cash_price,
            stock=stock,
            category=category,
            image_url=image_url,
            currency_id=currency_id
        )

        if attributes:
            product.attributes = attributes

        db.session.add(product)
        db.session.commit()
        return product

    @staticmethod
    def get_product_by_id(product_id):
        """根据ID获取商品"""
        product = Product.query.get(product_id)
        if not product:
            raise ProductNotFoundError(f"Product with id {product_id} not found")
        return product

    @staticmethod
    def update_product(product_id, **kwargs):
        """更新商品信息"""
        product = ProductService.get_product_by_id(product_id)

        allowed_fields = {
            'name', 'description', 'points_price', 'cash_price',
            'image_url', 'category', 'is_active', 'attributes', 'currency_id'
        }

        for key, value in kwargs.items():
            if key in allowed_fields:
                setattr(product, key, value)

        product.updated_at = datetime.utcnow()
        db.session.commit()
        return product

    @staticmethod
    def update_stock(product_id, quantity_change):
        """更新商品库存"""
        product = ProductService.get_product_by_id(product_id)

        new_stock = product.stock + quantity_change
        if new_stock < 0:
            raise InsufficientStockError(f"Cannot reduce stock below zero. Current stock: {product.stock}")

        product.stock = new_stock
        db.session.commit()
        return product

    @staticmethod
    def deactivate_product(product_id):
        """停用商品"""
        product = ProductService.get_product_by_id(product_id)
        product.is_active = False
        db.session.commit()
        return product

    @staticmethod
    def activate_product(product_id):
        """激活商品"""
        product = ProductService.get_product_by_id(product_id)
        product.is_active = True
        db.session.commit()
        return product

    @staticmethod
    def search_products(keyword=None, category=None, min_points=None, max_points=None,
                        in_stock=None, page=1, per_page=20, sort_by='created_at', sort_order='desc'):
        """搜索商品"""
        query = Product.query

        # 应用过滤条件
        if keyword:
            query = query.filter(Product.name.ilike(f'%{keyword}%') |
                                Product.description.ilike(f'%{keyword}%'))

        if category:
            query = query.filter(Product.category == category)

        if min_points is not None:
            query = query.filter(Product.points_price >= min_points)

        if max_points is not None:
            query = query.filter(Product.points_price <= max_points)

        if in_stock is not None:
            if in_stock:
                query = query.filter(Product.stock > 0)
            else:
                query = query.filter(Product.stock == 0)

        # 应用排序
        sort_column = getattr(Product, sort_by, Product.created_at)
        if sort_order.lower() == 'asc':
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        # 分页
        return query.paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def get_categories():
        """获取所有商品分类"""
        return db.session.query(Product.category).distinct().all()

    @staticmethod
    def get_all_products(page=1, per_page=20, sort_by='created_at', sort_order='desc', filter_by=None):
        """获取所有商品（带分页和筛选）"""
        query = Product.query

        # 应用过滤条件
        if filter_by:
            if 'name' in filter_by and filter_by['name']:
                query = query.filter(Product.name.ilike(f"%{filter_by['name']}%"))
            if 'category' in filter_by and filter_by['category']:
                query = query.filter(Product.category == filter_by['category'])
            if 'is_active' in filter_by:
                query = query.filter(Product.is_active == filter_by['is_active'])

        # 应用排序
        sort_column = getattr(Product, sort_by, Product.created_at)
        if sort_order.lower() == 'asc':
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        # 分页
        return query.paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def add_promotion(product_id, promotion_id):
        """为商品添加促销活动"""
        product = ProductService.get_product_by_id(product_id)
        promotion = Promotion.query.get(promotion_id)

        if not promotion:
            raise ValueError(f"Promotion with id {promotion_id} not found")

        if promotion not in product.promotions:
            product.promotions.append(promotion)
            db.session.commit()
        return True

    @staticmethod
    def remove_promotion(product_id, promotion_id):
        """移除商品的促销活动"""
        product = ProductService.get_product_by_id(product_id)
        promotion = Promotion.query.get(promotion_id)

        if promotion and promotion in product.promotions:
            product.promotions.remove(promotion)
            db.session.commit()
        return True

    @staticmethod
    def get_product_final_price(product_id, quantity=1):
        """获取商品的最终价格（考虑促销活动）"""
        product = ProductService.get_product_by_id(product_id)
        return product.calculate_final_price(quantity)

    @staticmethod
    def get_all_products(page=1, per_page=20, sort_by='created_at', sort_order='desc', filter_by=None):
        """获取所有商品，支持分页、排序和过滤"""
        query = Product.query

        # 应用过滤条件
        if filter_by:
            if 'name' in filter_by:
                query = query.filter(Product.name.ilike(f"%{filter_by['name']}%"))
            if 'category' in filter_by:
                query = query.filter(Product.category == filter_by['category'])
            if 'is_active' in filter_by:
                query = query.filter(Product.is_active == filter_by['is_active'])

        # 应用排序
        sort_column = getattr(Product, sort_by, Product.created_at)
        if sort_order.lower() == 'asc':
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        # 分页
        return query.paginate(page=page, per_page=per_page, error_out=False)