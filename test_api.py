"""
CardBoard API Test Script
Run: python test_api.py (server must be running)
IDs are fetched dynamically from the API
Created by Claude.ai
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

tokens = {}
credentials = {
    'irdof':  '321321',
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

r = requests.post(f"{BASE_URL}/token/", json={"username": "irdof", "password": "wrong"})
ok("Wrong password → 401") if r.status_code == 401 else fail(f"Expected 401, got {r.status_code}")

r = requests.get(f"{BASE_URL}/boards/")
ok("No token → 401") if r.status_code == 401 else fail(f"Expected 401, got {r.status_code}")

# ===== FETCH USER IDs DYNAMICALLY =====
section("FETCHING USER IDs")

r = requests.get(f"{BASE_URL}/users/", headers=h(tokens['irdof']))
if r.status_code == 200:
    users = {u['username']: u for u in r.json()}
    ok(f"Users fetched → {list(users.keys())}")
    info(f"IDs: { {k: v['id'] for k, v in users.items()} }")
else:
    fail(f"Cannot fetch users → {r.status_code}")
    users = {}

admin_id  = users.get('irdof',  {}).get('id')
owner1_id = users.get('owner1', {}).get('id')
owner2_id = users.get('owner2', {}).get('id')
user1_id  = users.get('user1',  {}).get('id')
user2_id  = users.get('user2',  {}).get('id')
user3_id  = users.get('user3',  {}).get('id')
user4_id  = users.get('user4',  {}).get('id')
user5_id  = users.get('user5',  {}).get('id')

# ===== FETCH BOARDS & BUILD MEMBERSHIP MAP =====
section("FETCHING BOARDS & MEMBERSHIP MAP")

r = requests.get(f"{BASE_URL}/boards/", headers=h(tokens['irdof']))
if r.status_code == 200:
    all_boards = r.json()
    # Dict: board_id -> {name, owner, members}
    boards_map = {b['id']: b for b in all_boards}
    ok(f"Boards fetched → {len(all_boards)} found")

    # Board membership per user
    user_boards = {}
    for username, u in users.items():
        uid = u['id']
        member_of = [b['id'] for b in all_boards if uid in b.get('members', [])]
        owner_of  = [b['id'] for b in all_boards if b['owner'] == uid]
        user_boards[username] = {'member_of': member_of, 'owner_of': owner_of}
        info(f"{username} → owner of {owner_of}, member of {member_of}")
else:
    fail(f"Cannot fetch boards → {r.status_code}")
    all_boards = []
    boards_map = {}
    user_boards = {}

# Helper: get a board where username is member but NOT owner
def board_where_member_not_owner(username):
    for bid in user_boards.get(username, {}).get('member_of', []):
        if bid not in user_boards.get(username, {}).get('owner_of', []):
            return boards_map.get(bid)
    return None

# Helper: get a board where username is NOT member and NOT owner
def board_where_not_member(username):
    all_ids = set(b['id'] for b in all_boards)
    user_ids = set(user_boards.get(username, {}).get('member_of', []) +
                   user_boards.get(username, {}).get('owner_of', []))
    for bid in all_ids - user_ids:
        return boards_map.get(bid)
    return None

# Helper: get a user who is NOT member of a given board
def user_not_member_of(board_id):
    board = boards_map.get(board_id, {})
    members = board.get('members', [])
    owner = board.get('owner')
    for username, u in users.items():
        if u['id'] != owner and u['id'] not in members:
            return username, u['id']
    return None, None

board_id       = all_boards[0]["id"] if all_boards else None
owner1_board   = next((b for b in all_boards if b['owner'] == owner1_id), None)
owner1_board_id = owner1_board["id"] if owner1_board else None
owner2_board   = next((b for b in all_boards if b['owner'] == owner2_id), None)
owner2_board_id = owner2_board["id"] if owner2_board else None

# ===== 2. BOARDS =====
section("2. BOARDS")

ok(f"Admin lists all boards → {len(all_boards)} found")
info(f"Boards: {[b['name'] for b in all_boards]}")

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
r = requests.post(f"{BASE_URL}/boards/", headers=h(tokens['irdof']), json={
    "name": "Test Board", "owner": admin_id, "members": [user1_id, user2_id]
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
    r = requests.delete(f"{BASE_URL}/boards/{new_board_id}/", headers=h(tokens['irdof']))
    ok("Admin deletes board → 204 cascade") if r.status_code == 204 else fail(f"Admin cannot delete → {r.status_code}")

# ===== 2b. BOARD VALIDATIONS =====
section("2b. BOARD VALIDATIONS")

r = requests.post(f"{BASE_URL}/boards/", headers=h(tokens['irdof']), json={
    "name": "Invalid Board", "owner": user1_id, "members": []
})
ok(f"Non-staff owner → 400") if r.status_code == 400 else fail(f"Expected 400, got {r.status_code} {r.text}")

# ===== 3. COLUMNS =====
section("3. COLUMNS")

r = requests.get(f"{BASE_URL}/columns/", headers=h(tokens['irdof']))
if r.status_code == 200:
    columns = r.json()
    ok(f"Admin lists columns → {len(columns)} found")
    column_id = columns[0]["id"] if columns else None
    owner1_column = next((c for c in columns if c['board'] == owner1_board_id), None)
    owner1_column_id = owner1_column["id"] if owner1_column else None
else:
    fail(f"Cannot list columns → {r.status_code}")
    column_id = owner1_column_id = None

if board_id:
    r = requests.post(f"{BASE_URL}/columns/", headers=h(tokens['irdof']), json={
        "name": "Test Column", "board": board_id, "order": 99
    })
    ok("Admin creates column") if r.status_code == 201 else fail(f"Admin cannot create column → {r.status_code} {r.text}")

if board_id:
    r = requests.post(f"{BASE_URL}/columns/", headers=h(tokens['user1']), json={
        "name": "Hacked Column", "board": board_id, "order": 1
    })
    ok(f"User1 cannot create column → {r.status_code}") if r.status_code in [401, 403] else fail(f"User1 should be blocked → {r.status_code}")

# ===== 3b. COLUMN VALIDATIONS =====
section("3b. COLUMN VALIDATIONS")

if owner1_board_id:
    r = requests.post(f"{BASE_URL}/columns/", headers=h(tokens['owner2']), json={
        "name": "Hacked Column", "board": owner1_board_id, "order": 1
    })
    ok(f"Owner2 cannot create column in Owner1's board → 400") if r.status_code == 400 else fail(f"Expected 400, got {r.status_code} {r.text}")

if owner1_column_id and owner2_board_id:
    r = requests.patch(f"{BASE_URL}/columns/{owner1_column_id}/", headers=h(tokens['owner1']), json={
        "board": owner2_board_id
    })
    ok(f"Cannot move column to another board → 400") if r.status_code == 400 else fail(f"Expected 400, got {r.status_code} {r.text}")

# ===== 4. CARDS =====
section("4. CARDS")

r = requests.get(f"{BASE_URL}/cards/", headers=h(tokens['irdof']))
if r.status_code == 200:
    cards = r.json()
    ok(f"Admin lists cards → {len(cards)} found")
    user1_card = next((c for c in cards if c.get("assigned_to") == user1_id), None)
    user1_card_id = user1_card["id"] if user1_card else None
    info(f"Card assigned to user1: id={user1_card_id}, title='{user1_card['title'] if user1_card else 'not found'}'")
else:
    fail(f"Cannot list cards → {r.status_code}")
    user1_card_id = None

# Find a column in owner1's board where user1 is member — for card creation
user1_member_board = board_where_member_not_owner('user1')
user1_column = next((c for c in columns if user1_member_board and c['board'] == user1_member_board['id']), None) if columns else None
user1_column_id = user1_column["id"] if user1_column else column_id

info(f"Using column {user1_column_id} in board {user1_member_board['name'] if user1_member_board else '?'} for user1 card creation")

if user1_column_id:
    r = requests.post(f"{BASE_URL}/cards/", headers=h(tokens['user1']), json={
        "title": "New card by user1",
        "content": "test content",
        "status": "todo",
        "priority": "low",
        "column": user1_column_id,
        "order": 1,
    })
    if r.status_code == 201:
        ok("User1 creates a card without assignment")
        new_card_id = r.json()["id"]
        new_card_board_id = user1_member_board['id'] if user1_member_board else None
        new_card_board_owner = user1_member_board['owner'] if user1_member_board else None
        # Find token of this board's owner
        new_card_board_owner_username = next((u for u, d in users.items() if d['id'] == new_card_board_owner), None)
        info(f"Card created in board owned by {new_card_board_owner_username}")
    else:
        fail(f"User1 cannot create card → {r.status_code} {r.text}")
        new_card_id = None
        new_card_board_owner_username = None

# Owner of that board assigns card to user1
if new_card_id and new_card_board_owner_username:
    r = requests.patch(f"{BASE_URL}/cards/{new_card_id}/", headers=h(tokens[new_card_board_owner_username]), json={
        "assigned_to": user1_id
    })
    ok(f"Owner ({new_card_board_owner_username}) assigns card to user1") if r.status_code == 200 else fail(f"Owner cannot assign → {r.status_code} {r.text}")

# User1 updates their assigned card status
if user1_card_id:
    r = requests.patch(f"{BASE_URL}/cards/{user1_card_id}/", headers=h(tokens['user1']), json={"status": "in_progress"})
    ok("User1 updates own card → status: in_progress") if r.status_code == 200 else fail(f"User1 cannot update own card → {r.status_code} {r.text}")

# User3 cannot update user1's card
if user1_card_id:
    r = requests.patch(f"{BASE_URL}/cards/{user1_card_id}/", headers=h(tokens['user3']), json={"status": "done"})
    ok(f"User3 cannot update user1's card → {r.status_code}") if r.status_code in [400, 401, 403, 404] else fail(f"User3 should be blocked → {r.status_code} {r.text}")

# User5 cannot update (not member of that board)
if user1_card_id:
    r = requests.patch(f"{BASE_URL}/cards/{user1_card_id}/", headers=h(tokens['user5']), json={"status": "done"})
    ok(f"User5 (not member) cannot update → {r.status_code}") if r.status_code in [400, 401, 403, 404] else fail(f"User5 should be blocked → {r.status_code}")

# ===== 4b. CARD VALIDATIONS =====
section("4b. CARD VALIDATIONS")
# Get other member dynamically
board = boards_map.get(new_card_board_id, {})
other_member = next((uid for uid in board.get('members', []) if uid != user1_id), None)
info(f"User1 tries to assign card {new_card_id} to user {other_member}")


# User1 cannot assign a card (only owner can)
r = requests.patch(f"{BASE_URL}/cards/{new_card_id}/", headers=h(tokens['user1']), json={
    "assigned_to": other_member
})
if r.status_code == 200 and r.json().get('assigned_to') != other_member:
    ok(f"User1 cannot assign → field ignored (read_only)")
elif r.status_code == 400:
    ok(f"User1 cannot assign → 400")
else:
    fail(f"Expected field to be ignored or 400, got {r.status_code} {r.text}")

# Owner cannot assign to a non-member
if new_card_id and new_card_board_owner_username:
    non_member_username, non_member_id = user_not_member_of(new_card_board_id)
    if non_member_id:
        info(f"Owner tries to assign to non-member {non_member_username} (id={non_member_id})")
        r = requests.patch(f"{BASE_URL}/cards/{new_card_id}/", headers=h(tokens[new_card_board_owner_username]), json={
            "assigned_to": non_member_id
        })
        ok(f"Cannot assign to non-member → 400") if r.status_code == 400 else fail(f"Expected 400, got {r.status_code} {r.text}")

# Cannot move card to a board user is not member of
if new_card_id:
    foreign_board = board_where_not_member('user1')
    if foreign_board:
        foreign_col = next((c for c in columns if c['board'] == foreign_board['id']), None)
        if foreign_col:
            info(f"User1 tries to move card to foreign board {foreign_board['name']}")
            r = requests.patch(f"{BASE_URL}/cards/{new_card_id}/", headers=h(tokens['user1']), json={
                "column": foreign_col["id"]
            })
            ok(f"Cannot move card to foreign board → 400") if r.status_code == 400 else fail(f"Expected 400, got {r.status_code} {r.text}")

# ===== 5. FILTERS =====
section("5. FILTERS")

r = requests.get(f"{BASE_URL}/cards/?status=todo", headers=h(tokens['irdof']))
ok(f"Filter status=todo → {len(r.json())} cards") if r.status_code == 200 else fail(f"Filter failed → {r.status_code}")

r = requests.get(f"{BASE_URL}/cards/?status=done", headers=h(tokens['irdof']))
ok(f"Filter status=done → {len(r.json())} cards") if r.status_code == 200 else fail(f"Filter failed → {r.status_code}")

r = requests.get(f"{BASE_URL}/cards/?priority=high", headers=h(tokens['irdof']))
ok(f"Filter priority=high → {len(r.json())} cards") if r.status_code == 200 else fail(f"Filter failed → {r.status_code}")

r = requests.get(f"{BASE_URL}/cards/?priority=low", headers=h(tokens['irdof']))
ok(f"Filter priority=low → {len(r.json())} cards") if r.status_code == 200 else fail(f"Filter failed → {r.status_code}")

if column_id:
    r = requests.get(f"{BASE_URL}/cards/?column={column_id}", headers=h(tokens['irdof']))
    ok(f"Filter column={column_id} → {len(r.json())} cards") if r.status_code == 200 else fail(f"Filter failed → {r.status_code}")

r = requests.get(f"{BASE_URL}/cards/?status=todo&priority=high", headers=h(tokens['irdof']))
ok(f"Combined filter todo+high → {len(r.json())} cards") if r.status_code == 200 else fail(f"Combined filter failed → {r.status_code}")

section("DONE ✅")