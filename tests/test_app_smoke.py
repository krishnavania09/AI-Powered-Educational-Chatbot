import os
from unittest.mock import patch
from app import create_app

def client():
    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()

def login(c, email="student@example.com", password="student"):
    return c.post("/signin", data={"email": email, "password": password}, follow_redirects=True)

def test_home():
    c = client()
    rv = c.get("/")
    assert rv.status_code == 200

def test_auth_and_chat_page():
    c = client()
    # guarded route redirects when not logged in
    assert c.get("/chat/").status_code in (302, 401, 403)
    # login works
    assert login(c).status_code == 200
    # now chat loads
    assert c.get("/chat/").status_code == 200

@patch("helper.send_gptnew", return_value="test-answer")
def test_chat_ask(mock_llm):
    c = client()
    login(c)
    rv = c.post("/chat/ask", json={"prompt": "hello"})
    assert rv.status_code == 200
    data = rv.get_json()
    assert data["ok"] is True
    assert data["answer"] == "test-answer"
    mock_llm.assert_called_once()
