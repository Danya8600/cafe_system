from datetime import datetime

from app.extensions import db
from app.models import Role, User


class UserRepository:
    @staticmethod
    def get_by_username(username):
        return User.query.filter_by(username=username).first()

    @staticmethod
    def get_by_id(user_id):
        return User.query.get(user_id)

    @staticmethod
    def get_role(user):
        if user is None:
            return None

        return Role.query.get(user.role_id)

    @staticmethod
    def get_role_by_name(name):
        return Role.query.filter_by(name=name).first()

    @staticmethod
    def create_client(username, password_hash):
        client_role = UserRepository.get_role_by_name("client")

        if client_role is None:
            raise ValueError("В базе данных не найдена роль 'client'.")

        user = User(
            role_id=client_role.id,
            username=username,
            password_hash=password_hash,
            created_at=datetime.now()
        )

        db.session.add(user)
        db.session.commit()

        return user

    @staticmethod
    def get_demo_client():
        return User.query.filter_by(username="client1").first()