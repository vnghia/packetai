import json
import os

import psycopg2
from flask import Flask, request
from werkzeug.middleware.dispatcher import DispatcherMiddleware

DATABASE_URL = os.environ.get("DATABASE_URL")
SCHEMA_NAME = os.environ.get("SCHEMA_NAME")
TABLE_NAME = os.environ.get("TABLE_NAME", "users")
conn = psycopg2.connect(DATABASE_URL, options=f"-c search_path={SCHEMA_NAME}")

root = Flask(__name__)


@root.route("/")
def entry():
    return "OK"


@root.route("/createuser", methods=["POST"])
def create_user():
    with conn:
        with conn.cursor() as curs:
            user = request.get_json()
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
