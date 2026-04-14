import click
from flask.cli import with_appcontext

from app.extensions import db
from app.models import AdminUser
from app.services.auth import hash_password


@click.command('create-admin')
@click.option('--email', prompt=True)
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=False)
@with_appcontext
def create_admin(email, password):
    """Create an admin user."""
    existing = AdminUser.query.filter_by(email=email).first()
    if existing:
        raise click.ClickException(f'Admin with email {email} already exists')
    user = AdminUser(email=email, password_hash=hash_password(password))
    db.session.add(user)
    db.session.commit()
    click.echo(f'Admin {email} created (id={user.id})')


def register_cli(app):
    app.cli.add_command(create_admin)
