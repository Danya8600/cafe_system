from app.models import User, Role


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
    def get_demo_client():
        return User.query.filter_by(username="client1").first()