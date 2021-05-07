from flask import Flask
from werkzeug.middleware.dispatcher import DispatcherMiddleware

root = Flask(__name__)


@root.route("/")
def entry():
    return "OK"


@root.route("/createuser", methods=["POST"])
def create_user():
    return "OK"


@root.route("/listuser", methods=["GET"])
def list_user():
    return "OK"


@root.route("/updateuser/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    return "OK"


@root.route("/deleteuser/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    return "OK"


app = DispatcherMiddleware(root)
