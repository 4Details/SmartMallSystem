from datetime import datetime, timedelta
from ..models import db
from ..models.points_transaction import PointsTransaction
from ..models.user import User
from ..services.user_service import UserService
from ..utils.exceptions import InsufficientPointsError

class PointsService:
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
        if points <= 0:
            raise ValueError("Points to deduct must be positive")

        # 验证用户存在
        user = UserService.get_user_by_id(user_id)

        # 检查用户是否有足够积分
        current_balance = user.get_points_balance()
        if current_balance < points:
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

        return transaction

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

        for transaction in expired_transactions:
            transaction.is_expired = True

        db.session.commit()
        return len(expired_transactions)

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