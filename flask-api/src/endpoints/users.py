from flask import Blueprint, jsonify, request
from src import db
from src.models import User

users_bp = Blueprint("users", __name__)


@users_bp.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()
    return jsonify(
        [
            {"user_id": user.user_id, "username": user.username, "email": user.email}
            for user in users
        ]
    )


@users_bp.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(
        {"user_id": user.user_id, "username": user.username, "email": user.email}
    )


@users_bp.route("/users", methods=["POST"])
def create_user():
    data = request.json
    new_user = User(username=data["username"], email=data["email"])
    db.session.add(new_user)
    db.session.commit()
    return (
        jsonify(
            {
                "user_id": new_user.user_id,
                "username": new_user.username,
                "email": new_user.email,
            }
        ),
        201,
    )
