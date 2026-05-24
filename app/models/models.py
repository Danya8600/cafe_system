from app.extensions import db


class Role(db.Model):
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    users = db.relationship("User", back_populates="role")

    def __repr__(self):
        return f"<Role {self.name}>"


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)

    role = db.relationship("Role", back_populates="users")

    customer_orders = db.relationship(
        "OrderRecord",
        foreign_keys="OrderRecord.customer_id",
        back_populates="customer"
    )

    accepted_orders = db.relationship(
        "OrderRecord",
        foreign_keys="OrderRecord.accepted_by_id",
        back_populates="accepted_by"
    )

    def __repr__(self):
        return f"<User {self.username}>"


class OrderType(db.Model):
    __tablename__ = "order_types"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    orders = db.relationship("OrderRecord", back_populates="order_type")

    def __repr__(self):
        return f"<OrderType {self.name}>"


class PaymentMethod(db.Model):
    __tablename__ = "payment_methods"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    orders = db.relationship("OrderRecord", back_populates="payment_method")

    def __repr__(self):
        return f"<PaymentMethod {self.name}>"


class OrderStatus(db.Model):
    __tablename__ = "order_statuses"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    orders = db.relationship("OrderRecord", back_populates="status")

    def __repr__(self):
        return f"<OrderStatus {self.name}>"


class MenuItem(db.Model):
    __tablename__ = "menu_items"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    is_available = db.Column(db.Boolean, nullable=False, default=True)

    order_items = db.relationship("OrderItemRecord", back_populates="menu_item")

    def __repr__(self):
        return f"<MenuItem {self.name}>"


class Extra(db.Model):
    __tablename__ = "extras"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    is_available = db.Column(db.Boolean, nullable=False, default=True)

    order_item_extras = db.relationship("OrderItemExtraRecord", back_populates="extra")

    def __repr__(self):
        return f"<Extra {self.name}>"


class OrderRecord(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)

    customer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    accepted_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    order_type_id = db.Column(db.Integer, db.ForeignKey("order_types.id"), nullable=False)
    payment_method_id = db.Column(db.Integer, db.ForeignKey("payment_methods.id"), nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey("order_statuses.id"), nullable=False)

    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    address = db.Column(db.String(255), nullable=False)

    created_at = db.Column(db.DateTime, nullable=False)
    accepted_at = db.Column(db.DateTime, nullable=True)

    customer = db.relationship(
        "User",
        foreign_keys=[customer_id],
        back_populates="customer_orders"
    )

    accepted_by = db.relationship(
        "User",
        foreign_keys=[accepted_by_id],
        back_populates="accepted_orders"
    )

    order_type = db.relationship("OrderType", back_populates="orders")
    payment_method = db.relationship("PaymentMethod", back_populates="orders")
    status = db.relationship("OrderStatus", back_populates="orders")

    items = db.relationship(
        "OrderItemRecord",
        back_populates="order",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<OrderRecord #{self.id}>"


class OrderItemRecord(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)

    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey("menu_items.id"), nullable=False)

    quantity = db.Column(db.Integer, nullable=False, default=1)
    base_price = db.Column(db.Numeric(10, 2), nullable=False)

    order = db.relationship("OrderRecord", back_populates="items")
    menu_item = db.relationship("MenuItem", back_populates="order_items")

    extras = db.relationship(
        "OrderItemExtraRecord",
        back_populates="order_item",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<OrderItemRecord #{self.id}>"


class OrderItemExtraRecord(db.Model):
    __tablename__ = "order_item_extras"

    id = db.Column(db.Integer, primary_key=True)

    order_item_id = db.Column(db.Integer, db.ForeignKey("order_items.id"), nullable=False)
    extra_id = db.Column(db.Integer, db.ForeignKey("extras.id"), nullable=False)

    extra_price = db.Column(db.Numeric(10, 2), nullable=False)

    order_item = db.relationship("OrderItemRecord", back_populates="extras")
    extra = db.relationship("Extra", back_populates="order_item_extras")

    def __repr__(self):
        return f"<OrderItemExtraRecord #{self.id}>"