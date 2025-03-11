import pytest
from app.models.user import User, Role
from app.services.user_service import UserService
from app.utils.exceptions import DuplicateUserError, UserNotFoundError

class TestUserService:
    """用户服务测试类"""

    @pytest.fixture(autouse=True)
    def setup_method(self, session):
        """每个测试方法前的设置"""
        self.session = session

        # 创建管理员角色
        admin_role = Role(name='admin', description='Administrator')
        session.add(admin_role)
        session.commit()

    def test_create_user(self):
        """测试创建用户"""
        user = UserService.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )

        assert user is not None
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
        assert user.verify_password('password123')

    def test_create_duplicate_user(self):
        """测试创建重复用户"""
        UserService.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )

        with pytest.raises(DuplicateUserError):
            UserService.create_user(
                username='testuser',
                email='another@example.com',
                password='password123'
            )

        with pytest.raises(DuplicateUserError):
            UserService.create_user(
                username='anotheruser',
                email='test@example.com',
                password='password123'
            )

    def test_get_user_by_id(self):
        """测试通过ID获取用户"""
        user = UserService.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )

        found_user = UserService.get_user_by_id(user.id)
        assert found_user is not None
        assert found_user.id == user.id

        with pytest.raises(UserNotFoundError):
            UserService.get_user_by_id('nonexistent_id')

    def test_get_user_by_email(self):
        """测试通过邮箱获取用户"""
        user = UserService.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )

        found_user = UserService.get_user_by_email('test@example.com')
        assert found_user is not None
        assert found_user.id == user.id

        with pytest.raises(UserNotFoundError):
            UserService.get_user_by_email('nonexistent@example.com')

    def test_update_user(self):
        """测试更新用户信息"""
        user = UserService.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )

        updated_user = UserService.update_user(
            user.id,
            username='newusername',
            phone='1234567890'
        )

        assert updated_user.username == 'newusername'
        assert updated_user.phone == '1234567890'

    def test_assign_role(self):
        """测试分配角色"""
        user = UserService.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )

        UserService.assign_role(user.id, 'admin')

        user = UserService.get_user_by_id(user.id)
        assert 'admin' in [role.name for role in user.roles]