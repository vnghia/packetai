import json
import os
import re

import psycopg2
from flask import Flask, request
from werkzeug.exceptions import HTTPException, BadRequest
from werkzeug.middleware.dispatcher import DispatcherMiddleware

DATABASE_URL = os.environ.get("DATABASE_URL")
SCHEMA_NAME = os.environ.get("SCHEMA_NAME")
TABLE_NAME = os.environ.get("TABLE_NAME", "users")
conn = psycopg2.connect(DATABASE_URL, options=f"-c search_path={SCHEMA_NAME}")


check_email_regex = re.compile(
    r"""(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"""
)


def check_email(email):
    if not check_email_regex.match(email):
        raise BadRequest(f"{email} is not a valid email")


root = Flask(__name__)


@root.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, HTTPException):
        return e
    return str(e), 500


@root.route("/")
def entry():
    return "OK"


@root.route("/createuser", methods=["POST"])
def create_user():
    with conn:
        with conn.cursor() as curs:
            user = request.get_json()
            check_email(user["email"])
            curs.execute(
                f"INSERT INTO {TABLE_NAME} (name, email) VALUES (%s, %s) RETURNING id",
                (user["name"], user["email"]),
            )
            user_id = curs.fetchone()[0]
            return f"Created new user with id: {user_id}"


@root.route("/listuser", methods=["GET"])
def list_user():
    with conn:
        with conn.cursor() as curs:
            curs.execute(f"SELECT * FROM {TABLE_NAME}")
            users = [
                {"id": user[0], "name": user[1], "email": user[2]}
                for user in curs.fetchall()
            ]
            return json.dumps(users)


@root.route("/updateuser/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    with conn:
        with conn.cursor() as curs:
            user = request.get_json()
            check_email(user["email"])
            curs.execute(
                f"UPDATE {TABLE_NAME} SET name = %s, email = %s WHERE id = %s",
                (user["name"], user["email"], user_id),
            )
            return f"Updated user with id: {user_id}"


@root.route("/deleteuser/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    with conn:
        with conn.cursor() as curs:
            curs.execute(f"DELETE FROM {TABLE_NAME} WHERE id = %s", (user_id,))
            return f"Deleted user with id: {user_id}"


app = DispatcherMiddleware(root)
