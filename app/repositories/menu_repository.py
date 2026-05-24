from app.models import MenuItem, Extra


class MenuRepository:
    @staticmethod
    def get_available_menu():
        return (
            MenuItem.query
            .filter(MenuItem.is_available.is_(True))
            .order_by(MenuItem.id)
            .all()
        )

    @staticmethod
    def get_item_by_id(item_id):
        return MenuItem.query.get(item_id)

    @staticmethod
    def get_available_extras():
        return (
            Extra.query
            .filter(Extra.is_available.is_(True))
            .order_by(Extra.id)
            .all()
        )

    @staticmethod
    def get_extras_by_ids(extra_ids):
        if not extra_ids:
            return []

        return (
            Extra.query
            .filter(
                Extra.id.in_(extra_ids),
                Extra.is_available.is_(True)
            )
            .order_by(Extra.id)
            .all()
        )