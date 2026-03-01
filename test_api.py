"""
CardBoard API Test Script
Run: python test_api.py (server must be running)
IDs are fetched dynamically from the API
"""

import requests

BASE_URL = "http://127.0.0.1:8000/api"

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"

def ok(msg):      print(f"  {GREEN}✅ {msg}{RESET}")
def fail(msg):    print(f"  {RED}❌ {msg}{RESET}")
def info(msg):    print(f"  {YELLOW}→ {msg}{RESET}")
def section(msg): print(f"\n{BOLD}{BLUE}{'='*50}\n  {msg}\n{'='*50}{RESET}")

def get_token(username, password):
    r = requests.post(f"{BASE_URL}/token/",
        headers={"Content-Type": "application/json"},
        json={"username": username, "password": password}
    )
    if r.status_code == 200:
        return r.json()["access"]
    return None

def h(token):
    return {"Authorization": f"Bearer {token}"}

# ===== 1. AUTH =====
section("1. AUTHENTICATION")

# Get tokens
tokens = {}
credentials = {
    'admin':  'admin123',
    'owner1': 'owner123',
    'owner2': 'owner123',
    'user1':  'user123',
    'user2':  'user123',
    'user3':  'user123',
    'user4':  'user123',
    'user5':  'user123',
}

for username, password in credentials.items():
    token = get_token(username, password)
    if token:
        tokens[username] = token
        ok(f"{username} login successful")
    else:
        fail(f"{username} login failed")

r = requests.post(f"{BASE_URL}/token/", json={"username": "admin", "password": "wrong"})
ok("Wrong password → 401") if r.status_code == 401 else fail(f"Expected 401, got {r.status_code}")

r = requests.get(f"{BASE_URL}/boards/")
ok("No token → 401") if r.status_code == 401 else fail(f"Expected 401, got {r.status_code}")

# ===== FETCH USER IDs DYNAMICALLY =====
section("FETCHING USER IDs")

r = requests.get(f"{BASE_URL}/users/", headers=h(tokens['admin']))
if r.status_code == 200:
    users = {u['username']: u for u in r.json()}
    ok(f"Users fetched → {list(users.keys())}")
    info(f"IDs: { {k: v['id'] for k, v in users.items()} }")
else:
    fail(f"Cannot fetch users → {r.status_code}")
    users = {}

# ===== 2. BOARDS =====
section("2. BOARDS")

r = requests.get(f"{BASE_URL}/boards/", headers=h(tokens['admin']))
if r.status_code == 200:
    boards = r.json()
    ok(f"Admin lists all boards → {len(boards)} found")
    info(f"Boards: {[b['name'] for b in boards]}")
    board_id = boards[0]["id"] if boards else None
else:
    fail(f"Admin cannot list boards → {r.status_code}")
    board_id = None

r = requests.get(f"{BASE_URL}/boards/", headers=h(tokens['owner1']))
if r.status_code == 200:
    ok(f"Owner1 lists his boards → {len(r.json())} found")
    info(f"Owner1 boards: {[b['name'] for b in r.json()]}")
else:
    fail(f"Owner1 cannot list boards → {r.status_code}")

r = requests.get(f"{BASE_URL}/boards/", headers=h(tokens['user1']))
if r.status_code == 200:
    ok(f"User1 lists member boards → {len(r.json())} found")
    info(f"User1 boards: {[b['name'] for b in r.json()]}")
else:
    fail(f"User1 cannot list boards → {r.status_code}")

# Admin creates a board
admin_id = users.get('admin', {}).get('id')
user1_id = users.get('user1', {}).get('id')
user2_id = users.get('user2', {}).get('id')

if admin_id:
    r = requests.post(f"{BASE_URL}/boards/", headers=h(tokens['admin']), json={
        "name": "Test Board",
        "owner": admin_id,
        "members": [user1_id, user2_id]
    })
    if r.status_code == 201:
        ok("Admin creates a board")
        new_board_id = r.json()["id"]
    else:
        fail(f"Admin cannot create board → {r.status_code} {r.text}")
        new_board_id = None

# User1 cannot create a board
r = requests.post(f"{BASE_URL}/boards/", headers=h(tokens['user1']), json={
    "name": "Hacked Board", "owner": user1_id, "members": []
})
ok(f"User1 cannot create board → {r.status_code}") if r.status_code in [401, 403] else fail(f"User1 should be blocked → {r.status_code}")

# User1 cannot delete a board
if board_id:
    r = requests.delete(f"{BASE_URL}/boards/{board_id}/", headers=h(tokens['user1']))
    ok(f"User1 cannot delete board → {r.status_code}") if r.status_code in [401, 403] else fail(f"User1 should be blocked → {r.status_code}")

# Admin deletes test board (cascade)
if new_board_id:
    r = requests.delete(f"{BASE_URL}/boards/{new_board_id}/", headers=h(tokens['admin']))
    ok("Admin deletes board → 204 cascade") if r.status_code == 204 else fail(f"Admin cannot delete → {r.status_code}")

# ===== 3. COLUMNS =====
section("3. COLUMNS")

r = requests.get(f"{BASE_URL}/columns/", headers=h(tokens['admin']))
if r.status_code == 200:
    columns = r.json()
    ok(f"Admin lists columns → {len(columns)} found")
    column_id = columns[0]["id"] if columns else None
else:
    fail(f"Cannot list columns → {r.status_code}")
    column_id = None

if board_id:
    r = requests.post(f"{BASE_URL}/columns/", headers=h(tokens['admin']), json={
        "name": "Test Column", "board": board_id, "order": 99
    })
    ok("Admin creates column") if r.status_code == 201 else fail(f"Admin cannot create column → {r.status_code} {r.text}")

if board_id:
    r = requests.post(f"{BASE_URL}/columns/", headers=h(tokens['user1']), json={
        "name": "Hacked Column", "board": board_id, "order": 1
    })
    ok(f"User1 cannot create column → {r.status_code}") if r.status_code in [401, 403] else fail(f"User1 should be blocked → {r.status_code}")

# ===== 4. CARDS =====
section("4. CARDS")

r = requests.get(f"{BASE_URL}/cards/", headers=h(tokens['admin']))
if r.status_code == 200:
    cards = r.json()
    ok(f"Admin lists cards → {len(cards)} found")
    user1_card = next((c for c in cards if c.get("assigned_to") == user1_id), None)
    user1_card_id = user1_card["id"] if user1_card else None
    info(f"Card assigned to user1: id={user1_card_id}, title='{user1_card['title'] if user1_card else 'not found'}'")
else:
    fail(f"Cannot list cards → {r.status_code}")
    user1_card_id = None

if column_id:
    r = requests.post(f"{BASE_URL}/cards/", headers=h(tokens['user1']), json={
        "title": "New card by user1",
        "content": "test content",
        "status": "todo",
        "priority": "low",
        "column": column_id,
        "order": 1,
        "assigned_to": user1_id
    })
    if r.status_code == 201:
        ok("User1 creates a card")
        new_card_id = r.json()["id"]
    else:
        fail(f"User1 cannot create card → {r.status_code} {r.text}")
        new_card_id = None

if user1_card_id:
    r = requests.patch(f"{BASE_URL}/cards/{user1_card_id}/", headers=h(tokens['user1']), json={"status": "in_progress"})
    ok("User1 updates own card → status: in_progress") if r.status_code == 200 else fail(f"User1 cannot update own card → {r.status_code} {r.text}")

if user1_card_id:
    r = requests.patch(f"{BASE_URL}/cards/{user1_card_id}/", headers=h(tokens['user2']), json={"status": "done"})
    ok(f"User2 cannot update user1's card → {r.status_code}") if r.status_code in [401, 403] else fail(f"User2 should be blocked → {r.status_code} {r.text}")

if user1_card_id:
    r = requests.patch(f"{BASE_URL}/cards/{user1_card_id}/", headers=h(tokens['user5']), json={"status": "done"})
    ok(f"User5 (not member) cannot update → {r.status_code}") if r.status_code in [401, 403,404] else fail(f"User5 should be blocked → {r.status_code}")

# ===== 5. FILTERS =====
section("5. FILTERS")

r = requests.get(f"{BASE_URL}/cards/?status=todo", headers=h(tokens['admin']))
ok(f"Filter status=todo → {len(r.json())} cards") if r.status_code == 200 else fail(f"Filter failed → {r.status_code}")

r = requests.get(f"{BASE_URL}/cards/?status=done", headers=h(tokens['admin']))
ok(f"Filter status=done → {len(r.json())} cards") if r.status_code == 200 else fail(f"Filter failed → {r.status_code}")

r = requests.get(f"{BASE_URL}/cards/?priority=high", headers=h(tokens['admin']))
ok(f"Filter priority=high → {len(r.json())} cards") if r.status_code == 200 else fail(f"Filter failed → {r.status_code}")

r = requests.get(f"{BASE_URL}/cards/?priority=low", headers=h(tokens['admin']))
ok(f"Filter priority=low → {len(r.json())} cards") if r.status_code == 200 else fail(f"Filter failed → {r.status_code}")

if column_id:
    r = requests.get(f"{BASE_URL}/cards/?column={column_id}", headers=h(tokens['admin']))
    ok(f"Filter column={column_id} → {len(r.json())} cards") if r.status_code == 200 else fail(f"Filter failed → {r.status_code}")

r = requests.get(f"{BASE_URL}/cards/?status=todo&priority=high", headers=h(tokens['admin']))
ok(f"Combined filter todo+high → {len(r.json())} cards") if r.status_code == 200 else fail(f"Combined filter failed → {r.status_code}")

section("DONE ✅")