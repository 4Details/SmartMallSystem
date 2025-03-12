from datetime import datetime, timedelta
from ..models import db
from ..models.points_transaction import PointsTransaction
from ..models.user import User
from ..services.user_service import UserService
from ..utils.exceptions import InsufficientPointsError

class PointsService:
    @staticmethod
    def update_system_points_stats():
        """更新系统积分统计"""
        total_points = PointsService.get_total_points_in_system()
        active_points = PointsService.get_total_active_points()
        expired_points = PointsService.get_total_expired_points()

        # 这里可以添加将统计数据保存到缓存或数据库的逻辑
        # 例如：
        # cache.set('total_points', total_points)
        # cache.set('active_points', active_points)
        # cache.set('expired_points', expired_points)

        return {
            'total_points': total_points,
            'active_points': active_points,
            'expired_points': expired_points
        }
    @staticmethod
    def get_user_points_history(user_id, page=1, per_page=20):
        """获取用户积分历史记录"""
        UserService.get_user_by_id(user_id)  # 验证用户存在
        return PointsTransaction.query.filter_by(user_id=user_id).order_by(
            PointsTransaction.created_at.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def get_total_points_in_system():
        """获取系统中的总积分数"""
        return db.session.query(db.func.sum(PointsTransaction.points)).scalar() or 0

    @staticmethod
    def get_total_active_points():
        """获取系统中的有效积分总数"""
        return db.session.query(db.func.sum(PointsTransaction.points)).filter(
            PointsTransaction.is_expired == False
        ).scalar() or 0

    @staticmethod
    def get_total_expired_points():
        """获取系统中已过期的积分总数"""
        return db.session.query(db.func.sum(PointsTransaction.points)).filter(
            PointsTransaction.is_expired == True
        ).scalar() or 0

    @staticmethod
    def get_points_rules():
        """获取积分规则"""
        # 这里需要根据你的实际存储方式来实现
        # 例如，如果你将规则存储在数据库中：
        # return PointsRule.query.all()
        # 或者如果你将规则存储在配置文件中：
        # return current_app.config.get('POINTS_RULES')
        pass

    @staticmethod
    def update_points_rules(new_rules):
        """更新积分规则"""
        # 这里需要根据你的实际存储方式来实现
        # 例如，如果你将规则存储在数据库中：
        # for rule in new_rules:
        #     db_rule = PointsRule.query.get(rule['id'])
        #     if db_rule:
        #         for key, value in rule.items():
        #             setattr(db_rule, key, value)
        # db.session.commit()
        # return PointsRule.query.all()
        pass
    @staticmethod
    def add_points(user_id, points, transaction_type, description=None,
                   expires_in_days=None, related_entity_id=None, related_entity_type=None):
        """为用户添加积分"""
        if points <= 0:
            raise ValueError("Points to add must be positive")

        # 验证用户存在
        user = UserService.get_user_by_id(user_id)

        # 设置过期时间
        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)

        # 创建积分交易记录
        transaction = PointsTransaction.create_transaction(
            user_id=user_id,
            points=points,
            transaction_type=transaction_type,
            description=description,
            expires_at=expires_at,
            related_entity_id=related_entity_id,
            related_entity_type=related_entity_type
        )

        # 更新用户会员等级
        UserService.update_membership_level(user_id)

        return transaction

    @staticmethod
    def deduct_points(user_id, points, transaction_type, description=None,
                      related_entity_id=None, related_entity_type=None):
        """从用户扣除积分"""
        import logging

        logging.info(f"Attempting to deduct {points} points from user {user_id}")

        if points <= 0:
            logging.error(f"Invalid points value: {points}")
            raise ValueError("Points to deduct must be positive")

        try:
            # 验证用户存在
            user = UserService.get_user_by_id(user_id)
            logging.info(f"User {user_id} found")

            # 检查用户是否有足够积分
            current_balance = user.get_points_balance()
            logging.info(f"User {user_id} current balance: {current_balance}")

            if current_balance < points:
                logging.warning(f"Insufficient points for user {user_id}. Required: {points}, Available: {current_balance}")
                raise InsufficientPointsError(f"Insufficient points. Required: {points}, Available: {current_balance}")

            # 创建积分交易记录（使用负数表示扣除）
            transaction = PointsTransaction.create_transaction(
                user_id=user_id,
                points=-points,  # 负数表示扣除
                transaction_type=transaction_type,
                description=description,
                related_entity_id=related_entity_id,
                related_entity_type=related_entity_type
            )
            logging.info(f"Points transaction created: {transaction.id}")

            return transaction
        except Exception as e:
            logging.error(f"Error in deduct_points: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def get_user_points_balance(user_id):
        """获取用户当前积分余额"""
        user = UserService.get_user_by_id(user_id)
        return user.get_points_balance()

    @staticmethod
    def get_user_points_summary(user_id):
        """获取用户积分汇总信息"""
        UserService.get_user_by_id(user_id)  # 验证用户存在
        return PointsTransaction.get_user_points_summary(user_id)

    @staticmethod
    def get_user_transactions(user_id, page=1, per_page=20, transaction_type=None):
        """获取用户的积分交易历史"""
        UserService.get_user_by_id(user_id)  # 验证用户存在
        return PointsTransaction.get_user_transactions(
            user_id, page, per_page, transaction_type
        )

    @staticmethod
    def expire_points():
        """过期已到期的积分"""
        now = datetime.utcnow()
        expired_transactions = PointsTransaction.query.filter(
            PointsTransaction.expires_at <= now,
            PointsTransaction.is_expired == False,
            PointsTransaction.points > 0  # 只过期正数积分（获得的积分）
        ).all()

        expired_count = 0
        for transaction in expired_transactions:
            transaction.is_expired = True
            # 创建一个新的过期交易记录
            PointsTransaction.create_transaction(
                user_id=transaction.user_id,
                points=-transaction.points,
                transaction_type="EXPIRATION",
                description="Points expired",
                related_entity_id=transaction.id,
                related_entity_type="TRANSACTION"
            )
            expired_count += 1

        db.session.commit()
        return expired_count

    @staticmethod
    def transfer_points(from_user_id, to_user_id, points, description=None):
        """用户之间转移积分"""
        if points <= 0:
            raise ValueError("Points to transfer must be positive")

        # 验证两个用户都存在
        from_user = UserService.get_user_by_id(from_user_id)
        to_user = UserService.get_user_by_id(to_user_id)

        # 检查发送方是否有足够积分
        current_balance = from_user.get_points_balance()
        if current_balance < points:
            raise InsufficientPointsError(f"Insufficient points. Required: {points}, Available: {current_balance}")

        # 开始事务
        try:
            # 从发送方扣除积分
            deduct_transaction = PointsTransaction.create_transaction(
                user_id=from_user_id,
                points=-points,
                transaction_type="TRANSFER_OUT",
                description=description or f"Transfer to {to_user.username}",
                related_entity_id=to_user_id,
                related_entity_type="USER"
            )

            # 给接收方添加积分
            add_transaction = PointsTransaction.create_transaction(
                user_id=to_user_id,
                points=points,
                transaction_type="TRANSFER_IN",
                description=description or f"Transfer from {from_user.username}",
                related_entity_id=from_user_id,
                related_entity_type="USER"
            )

            # 更新会员等级
            UserService.update_membership_level(from_user_id)
            UserService.update_membership_level(to_user_id)

            return {
                'deduct_transaction': deduct_transaction,
                'add_transaction': add_transaction
            }
        except Exception as e:
            db.session.rollback()
            raise e