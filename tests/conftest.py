import pytest
from app import create_app
from app.models import db as _db

@pytest.fixture(scope='session')
def app(request):
    """创建并配置一个新的app实例"""
    _app = create_app('testing')

    # 建立应用上下文
    ctx = _app.app_context()
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)
    return _app

@pytest.fixture(scope='session')
def db(app, request):
    """会话范围的数据库"""

    def teardown():
        _db.drop_all()

    _db.app = app
    _db.create_all()

    request.addfinalizer(teardown)
    return _db

@pytest.fixture(scope='function')
def session(db, request):
    """每个测试函数创建一个新的数据库会话"""
    connection = db.engine.connect()
    transaction = connection.begin()
    options = dict(bind=connection, binds={})
    session = db.create_scoped_session(options=options)
    db.session = session

    def teardown():
        transaction.rollback()
        connection.close()
        session.remove()

    request.addfinalizer(teardown)
    return session