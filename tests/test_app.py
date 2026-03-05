import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
import mock_data as db
from app import app


@pytest.fixture(autouse=True)
def reset_mock_data():
    """Reset in-memory data before each test to avoid state bleed."""
    db.TRANSACTIONS[:] = db._make_transactions()
    db.ACCOUNTS[0]["balance"] = 5_284.37
    db.ACCOUNTS[0]["available"] = 5_284.37
    db.ACCOUNTS[1]["balance"] = 18_750.00
    db.ACCOUNTS[1]["available"] = 18_750.00
    yield


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test-secret"
    with app.test_client() as c:
        yield c


def login(client, email="demo@savi.com", password="password123"):
    return client.post("/login", data={"email": email, "password": password}, follow_redirects=True)


# ── Auth tests ────────────────────────────────────────────────────────────────

def test_login_valid_credentials(client):
    resp = login(client)
    assert resp.status_code == 200
    assert b"dashboard" in resp.data.lower() or b"alex" in resp.data.lower()


def test_login_invalid_credentials_shows_error(client):
    resp = client.post(
        "/login",
        data={"email": "demo@savi.com", "password": "wrongpassword"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert b"Invalid email or password" in resp.data


def test_login_unknown_email_shows_error(client):
    resp = client.post(
        "/login",
        data={"email": "nobody@example.com", "password": "password123"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert b"Invalid email or password" in resp.data


# ── Auth-guard tests ──────────────────────────────────────────────────────────

def test_dashboard_redirects_when_unauthenticated(client):
    resp = client.get("/dashboard")
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]


def test_transactions_redirects_when_unauthenticated(client):
    resp = client.get("/transactions")
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]


def test_transfer_redirects_when_unauthenticated(client):
    resp = client.get("/transfer")
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]


# ── Transfer tests ────────────────────────────────────────────────────────────

def test_transfer_deducts_from_account_balance(client):
    login(client)
    checking = next(a for a in db.ACCOUNTS if a["id"] == "chk001")
    original_balance = checking["balance"]

    resp = client.post(
        "/transfer",
        data={
            "from_account": "chk001",
            "to_payee": "Test Payee",
            "amount": "100.00",
            "transfer_date": "2026-03-04",
            "memo": "",
        },
        follow_redirects=True,
    )

    assert resp.status_code == 200
    assert checking["balance"] == round(original_balance - 100.00, 2)


def test_transfer_appends_transaction(client):
    login(client)
    original_count = len(db.TRANSACTIONS)

    client.post(
        "/transfer",
        data={
            "from_account": "chk001",
            "to_payee": "Test Payee",
            "amount": "50.00",
            "transfer_date": "2026-03-04",
            "memo": "",
        },
        follow_redirects=True,
    )

    assert len(db.TRANSACTIONS) == original_count + 1
    assert db.TRANSACTIONS[0]["amount"] == -50.00
    assert db.TRANSACTIONS[0]["account_id"] == "chk001"


def test_transfer_invalid_amount_shows_error(client):
    login(client)
    resp = client.post(
        "/transfer",
        data={
            "from_account": "chk001",
            "to_payee": "Test Payee",
            "amount": "-50",
            "transfer_date": "2026-03-04",
            "memo": "",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert b"valid amount" in resp.data


# ── Transactions filter tests ─────────────────────────────────────────────────

def test_transactions_filter_by_account(client):
    login(client)
    resp = client.get("/transactions?account=sav001")
    assert resp.status_code == 200
    html = resp.data.decode()
    # sav001 transactions should appear
    assert "Transfer from Checking" in html or "Savings Interest" in html
    # chk001-only transactions should not appear
    assert "Whole Foods Market" not in html


def test_transactions_filter_by_category(client):
    login(client)
    resp = client.get("/transactions?category=Food+%26+Dining")
    assert resp.status_code == 200
    html = resp.data.decode()
    assert "Whole Foods Market" in html
    assert "Uber Eats" in html
    # Non-food transactions should not appear
    assert "Netflix" not in html
    assert "AT&amp;T Wireless" not in html


def test_transactions_filter_combined(client):
    login(client)
    resp = client.get("/transactions?account=chk001&category=Entertainment")
    assert resp.status_code == 200
    html = resp.data.decode()
    assert "Netflix" in html
    assert "Spotify" in html
    # Food items shouldn't appear
    assert "Whole Foods Market" not in html


def test_transactions_no_filter_returns_all(client):
    login(client)
    resp = client.get("/transactions")
    assert resp.status_code == 200
    html = resp.data.decode()
    # Transactions from all accounts should be present
    assert "Whole Foods Market" in html        # chk001
    assert "Savings Interest" in html          # sav001
    assert "Best Buy" in html                  # cc001
