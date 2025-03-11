import pytest
from app.models.user import User, Role
from app.services.user_service import UserService

class TestBase:
    """基础测试类"""

    @pytest.fixture(autouse=True)
    def setup_method(self, session):
        """每个测试方法前的设置"""
        self.session = session

    def test_app_exists(self, app):
        """测试应用实例存在"""
        assert app is not None

    def test_app_is_testing(self, app):
        """测试应用处于测试模式"""
        assert app.config['TESTING']