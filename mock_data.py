from datetime import date, timedelta
import random

# Demo credentials
USERS = {
    "demo@savi.com": {
        "password": "password123",
        "name": "Alex Johnson",
        "member_since": "2019",
    }
}

# Accounts
ACCOUNTS = [
    {
        "id": "chk001",
        "type": "Checking",
        "number": "****4821",
        "balance": 5_284.37,
        "available": 5_284.37,
        "color": "#012169",
    },
    {
        "id": "sav001",
        "type": "Savings",
        "number": "****3309",
        "balance": 18_750.00,
        "available": 18_750.00,
        "color": "#E31837",
    },
    {
        "id": "cc001",
        "type": "Credit Card",
        "number": "****7742",
        "balance": -1_234.56,
        "available": 8_765.44,
        "color": "#1a6b3c",
    },
]

_categories = ["Food & Dining", "Shopping", "Utilities", "Travel", "Entertainment", "Healthcare", "Transfer", "Deposit"]

def _make_transactions():
    items = [
        # date offset, description, amount, category, account_id
        (0,  "Whole Foods Market",        -87.43,   "Food & Dining",   "chk001"),
        (1,  "Amazon Purchase",           -124.99,  "Shopping",        "chk001"),
        (2,  "Netflix",                   -15.49,   "Entertainment",   "chk001"),
        (3,  "Direct Deposit - Payroll",  3_250.00, "Deposit",         "chk001"),
        (4,  "Uber Eats",                 -32.11,   "Food & Dining",   "chk001"),
        (5,  "AT&T Wireless",             -89.00,   "Utilities",       "chk001"),
        (6,  "Delta Airlines",            -412.80,  "Travel",          "chk001"),
        (7,  "Walgreens",                 -18.75,   "Healthcare",      "chk001"),
        (8,  "Target",                    -63.20,   "Shopping",        "chk001"),
        (9,  "Starbucks",                 -6.45,    "Food & Dining",   "chk001"),
        (10, "Spotify",                   -9.99,    "Entertainment",   "chk001"),
        (11, "Electric Bill - PG&E",      -142.33,  "Utilities",       "chk001"),
        (12, "CVS Pharmacy",              -24.50,   "Healthcare",      "chk001"),
        (13, "Chipotle",                  -14.75,   "Food & Dining",   "chk001"),
        (14, "Transfer to Savings",       -500.00,  "Transfer",        "chk001"),
        (14, "Transfer from Checking",     500.00,  "Transfer",        "sav001"),
        (15, "Savings Interest",            12.42,  "Deposit",         "sav001"),
        (16, "Best Buy",                  -299.99,  "Shopping",        "cc001"),
        (17, "Cheesecake Factory",         -78.60,  "Food & Dining",   "cc001"),
        (18, "Credit Card Payment",        400.00,  "Transfer",        "cc001"),
    ]

    today = date.today()
    txns = []
    for i, (offset, desc, amt, cat, acct) in enumerate(items):
        txns.append({
            "id": f"txn{i:03d}",
            "date": (today - timedelta(days=offset)).strftime("%Y-%m-%d"),
            "description": desc,
            "amount": amt,
            "category": cat,
            "account_id": acct,
        })
    return txns

# Mutable list so transfers can append to it at runtime
TRANSACTIONS = _make_transactions()

CATEGORIES = _categories
