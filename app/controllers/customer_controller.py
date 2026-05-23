from flask import Blueprint, render_template

customer_bp = Blueprint("customer", __name__)


@customer_bp.route("/")
def index():
    return render_template("index.html")