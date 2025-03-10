from app import create_app
from app.models import db
from app.models.user import Role, MembershipLevel
import uuid
import json

def init_db():
    app = create_app()
    with app.app_context():
        # 创建所有表
        db.create_all()

        # 创建默认角色
        roles = [
            ('admin', 'System administrator with full access'),
            ('user', 'Regular user with basic access'),
            ('staff', 'Staff member with elevated access')
        ]

        for role_name, description in roles:
            if not Role.query.filter_by(name=role_name).first():
                role = Role(id=str(uuid.uuid4()), name=role_name, description=description)
                db.session.add(role)

        # 创建默认会员等级
        levels = [
            ('Bronze', 'Basic membership level', 0, {'discount_rate': 1.0}, '#CD7F32'),
            ('Silver', 'Intermediate membership level', 1000, {'discount_rate': 0.95}, '#C0C0C0'),
            ('Gold', 'Advanced membership level', 5000, {'discount_rate': 0.9}, '#FFD700'),
            ('Platinum', 'Premium membership level', 10000, {'discount_rate': 0.85}, '#E5E4E2')
        ]

        for name, desc, points, benefits, color in levels:
            if not MembershipLevel.query.filter_by(name=name).first():
                level = MembershipLevel(
                    id=str(uuid.uuid4()),
                    name=name,
                    description=desc,
                    required_points=points,
                    benefits=json.dumps(benefits),
                    color_code=color
                )
                db.session.add(level)

        db.session.commit()

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully!")