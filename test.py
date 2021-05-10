import os
import re
from urllib.parse import urljoin

import pytest
import requests

API_ENDPOINT = os.environ.get("API_ENDPOINT")
CREATED_USER_RESPONSE = re.compile(r"Created new user with id: (\d+)")

TEST_USER_NAME = "Test User"
TEST_USER_EMAIL = "test.user@example.com"

TEST_USER_NEW_NAME = "Test User New"
TEST_USER_NEW_EMAIL = "test.user.new@example.com"


def compare_user(lhs):
    return lhs["id"]


@pytest.mark.skipif(not API_ENDPOINT, reason="API_ENDPOINT isn't set")
def test_api():
    res = requests.get(urljoin(API_ENDPOINT, "listuser"))
    assert res.status_code == 200
    initial_users = res.json()

    res = requests.post(
        urljoin(API_ENDPOINT, "createuser"),
        json={"name": TEST_USER_NAME, "email": TEST_USER_EMAIL},
    )
    assert res.status_code == 200
    user_id_match = CREATED_USER_RESPONSE.search(res.text)
    assert user_id_match is not None
    user_id = int(user_id_match.group(1))

    res = requests.get(urljoin(API_ENDPOINT, "listuser"))
    assert res.status_code == 200
    created_users = res.json()
    assert (
        sorted(
            initial_users
            + [{"id": user_id, "name": TEST_USER_NAME, "email": TEST_USER_EMAIL}],
            key=compare_user,
        )
        == sorted(created_users, key=compare_user)
    )

    res = requests.put(
        urljoin(API_ENDPOINT, f"updateuser/{user_id}"),
        json={"name": TEST_USER_NEW_NAME, "email": TEST_USER_NEW_EMAIL},
    )
    assert res.status_code == 200
    res = requests.get(urljoin(API_ENDPOINT, "listuser"))
    assert res.status_code == 200
    created_users = res.json()
    assert (
        sorted(
            initial_users
            + [
                {
                    "id": user_id,
                    "name": TEST_USER_NEW_NAME,
                    "email": TEST_USER_NEW_EMAIL,
                }
            ],
            key=compare_user,
        )
        == sorted(created_users, key=compare_user)
    )

    res = requests.delete(urljoin(API_ENDPOINT, f"deleteuser/{user_id}"))
    assert res.status_code == 200
    res = requests.get(urljoin(API_ENDPOINT, "listuser"))
    created_users = res.json()
    assert sorted(initial_users, key=compare_user) == sorted(
        created_users, key=compare_user
    )
