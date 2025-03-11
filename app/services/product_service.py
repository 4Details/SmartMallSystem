import logging
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
        logging.info(f"Attempting to get product by ID: {product_id}")

        try:
            # 尝试直接通过ID获取
            product = Product.query.get(product_id)

            if not product:
                logging.warning(f"Product not found with ID: {product_id}")
                # 尝试使用filter方式查询（以防ID格式问题）
                product = Product.query.filter(Product.id.ilike(f"%{product_id}%")).first()

                if not product:
                    logging.error(f"Product not found with ID (after filter attempt): {product_id}")
                    raise ProductNotFoundError(f"Product with id {product_id} not found")
                else:
                    logging.info(f"Product found using filter: {product.id}")
            else:
                logging.info(f"Product found directly: {product.id}")

            return product

        except Exception as e:
            logging.error(f"Error getting product by ID {product_id}: {str(e)}")
            raise

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
                        in_stock=None, page=1, per_page=20, sort_by='created_at', sort_order='desc',
                        include_inactive=False):
        """搜索商品"""
        print(f"Searching products with params: keyword={keyword}, category={category}, "
              f"min_points={min_points}, max_points={max_points}, in_stock={in_stock}, "
              f"page={page}, per_page={per_page}, sort_by={sort_by}, sort_order={sort_order}, "
              f"include_inactive={include_inactive}")

        try:
            # 创建基础查询
            query = Product.query

            # 默认只显示激活的商品，除非明确要求包含未激活的商品
            if not include_inactive:
                query = query.filter(Product.is_active == True)
                print("Filtering only active products")

            # 应用过滤条件
            if keyword:
                query = query.filter(Product.name.ilike(f'%{keyword}%') |
                                    Product.description.ilike(f'%{keyword}%'))
                print(f"Applied keyword filter: {keyword}")

            if category:
                query = query.filter(Product.category == category)
                print(f"Applied category filter: {category}")

            if min_points is not None:
                query = query.filter(Product.points_price >= min_points)
                print(f"Applied min_points filter: {min_points}")

            if max_points is not None:
                query = query.filter(Product.points_price <= max_points)
                print(f"Applied max_points filter: {max_points}")

            if in_stock is not None:
                if in_stock:
                    query = query.filter(Product.stock > 0)
                    print("Filtering products in stock")
                else:
                    query = query.filter(Product.stock == 0)
                    print("Filtering products out of stock")

            # 应用排序
            sort_column = getattr(Product, sort_by, Product.created_at)
            if sort_order.lower() == 'asc':
                query = query.order_by(sort_column.asc())
                print(f"Sorting by {sort_by} in ascending order")
            else:
                query = query.order_by(sort_column.desc())
                print(f"Sorting by {sort_by} in descending order")

            # 获取总数
            total_count = query.count()
            print(f"Total products found: {total_count}")

            # 分页
            pagination = query.paginate(page=page, per_page=per_page, error_out=False)
            print(f"Pagination results: total={pagination.total}, pages={pagination.pages}, "
                  f"items={len(pagination.items)}")

            return pagination

        except Exception as e:
            print(f"Error in search_products: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def get_categories():
        """获取所有商品分类"""
        # 获取所有非空的分类
        categories = db.session.query(Product.category)\
            .filter(Product.category.isnot(None))\
            .filter(Product.category != '')\
            .distinct()\
            .all()

        # 如果没有分类，返回默认分类列表
        if not categories:
            return [
                ("电子产品",),
                ("家居用品",),
                ("服装配饰",),
                ("美妆护肤",),
                ("食品饮料",),
                ("图书音像",),
                ("其他",)
            ]

        return categories

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
    def exchange_product(user_id, product_id, quantity=1):
        """兑换商品"""
        from ..services.points_service import PointsService
        from ..models.order import Order

        product = ProductService.get_product_by_id(product_id)
        if not product.is_active:
            raise ValueError("商品已下架")

        if product.stock < quantity:
            raise ValueError("商品库存不足")

        price_info = product.calculate_final_price(quantity)
        total_points = price_info['final_points']

        # 检查用户积分是否足够
        user_points = PointsService.get_user_points_balance(user_id)
        if user_points < total_points:
            raise ValueError("积分不足")

        # 创建订单
        order = Order(user_id=user_id, total_points=total_points)
        db.session.add(order)

        # 扣除积分
        PointsService.deduct_points(
            user_id=user_id,
            points=total_points,
            transaction_type="EXCHANGE",
            description=f"兑换商品: {product.name}",
            related_entity_id=str(order.id),
            related_entity_type="Order"
        )

        # 更新库存
        product.stock -= quantity
        db.session.commit()

        return {
            "order_id": str(order.id),
            "points_deducted": total_points,
            "quantity": quantity
        }
