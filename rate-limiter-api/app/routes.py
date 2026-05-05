from flask import Blueprint, jsonify

bp = Blueprint("main", __name__)


@bp.route("/ping")
def ping():
    return jsonify({"status": "ok"})


@bp.route("/limited")
def limited():
    return jsonify({"message": "You got through the rate limiter!"})


@bp.route("/unlimited")
def unlimited():
    return jsonify({"message": "This route is never blocked."})
