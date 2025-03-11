from app import create_app
from app.models import db
from app.services.user_service import UserService
import click

@click.command()
@click.option('--username', prompt='Admin username', help='Username for the admin account')
@click.option('--email', prompt='Admin email', help='Email for the admin account')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='Password for the admin account')
def create_admin(username, email, password):
    """Create an admin user with the specified credentials."""
    app = create_app()
    with app.app_context():
        try:
            # 创建用户
            user = UserService.create_user(
                username=username,
                email=email,
                password=password
            )

            # 分配管理员角色
            UserService.assign_role(user.id, 'admin')

            click.echo(f"Admin user '{username}' created successfully!")

        except Exception as e:
            click.echo(f"Error creating admin user: {str(e)}", err=True)

if __name__ == '__main__':
    create_admin()