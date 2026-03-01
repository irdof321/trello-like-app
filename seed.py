import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'website.settings')
django.setup()

from django.contrib.auth import get_user_model
from website.cardboard.models import Board, Column, Card

User = get_user_model()

# ===== CLEAN =====
print("Cleaning database...")
Card.objects.all().delete()
Column.objects.all().delete()
Board.objects.all().delete()
User.objects.all().delete()

# ===== USERS =====
print("Creating users...")

admin = User.objects.create_user(
    username='admin',
    password='admin123',
    email='admin@cardboard.com',
    is_staff=True
)

owner1 = User.objects.create_user(
    username='owner1',
    password='owner123',
    email='owner1@cardboard.com',
    is_staff=True
)

owner2 = User.objects.create_user(
    username='owner2',
    password='owner123',
    email='owner2@cardboard.com',
    is_staff=True
)

normal_users = []
for i in range(1, 6):
    u = User.objects.create_user(
        username=f'user{i}',
        password='user123',
        email=f'user{i}@cardboard.com',
        is_staff=False
    )
    normal_users.append(u)

user1, user2, user3, user4, user5 = normal_users
print(f"  → 1 superadmin + 2 owners + 5 normal users created")

# ===== BOARDS =====
print("Creating boards...")

board1 = Board.objects.create(name='Frontend', owner=owner1)
board1.members.set([user1, user2, user3])

board2 = Board.objects.create(name='Backend', owner=owner1)
board2.members.set([user2, user4])

board3 = Board.objects.create(name='DevOps', owner=owner2)
board3.members.set([user3, user5])

board4 = Board.objects.create(name='Design', owner=owner2)
board4.members.set([user1, user4, user5])

boards = [board1, board2, board3, board4]
print(f"  → {len(boards)} boards created")

# ===== COLUMNS =====
print("Creating columns...")

column_names = ['Backlog', 'In Progress', 'Review', 'Done']
all_columns = []

for board in boards:
    for order, name in enumerate(column_names, start=1):
        col = Column.objects.create(name=name, board=board, order=order)
        all_columns.append(col)

print(f"  → {len(all_columns)} columns created")

# ===== CARDS =====
print("Creating cards...")

cards_data = [
    ("Fix login bug", "high", "todo"),
    ("Setup CI/CD", "medium", "in_progress"),
    ("Write unit tests", "low", "todo"),
    ("Update README", "low", "done"),
    ("Refactor auth", "high", "in_progress"),
    ("Add dark mode", "medium", "todo"),
    ("Optimize queries", "high", "done"),
    ("Deploy to staging", "medium", "in_progress"),
    ("Code review", "low", "todo"),
    ("Update dependencies", "medium", "done"),
    ("Add pagination", "low", "todo"),
    ("Fix typo in docs", "low", "done"),
    ("Setup monitoring", "high", "todo"),
    ("Write API docs", "medium", "in_progress"),
    ("Add rate limiting", "high", "todo"),
    ("Setup Redis cache", "medium", "todo"),
]

for i, (title, priority, status) in enumerate(cards_data):
    col = random.choice(all_columns)
    assigned = random.choice(normal_users + [None, None])
    Card.objects.create(
        title=title,
        content=f'Description for: {title}',
        status=status,
        priority=priority,
        column=col,
        order=i + 1,
        assigned_to=assigned,
    )

# Card specifically assigned to user1 for permission tests
test_col = all_columns[0]
Card.objects.create(
    title='Card assigned to user1',
    content='This card is specifically assigned to user1 for testing',
    status='todo',
    priority='medium',
    column=test_col,
    order=99,
    assigned_to=user1,
)

print(f"  → {Card.objects.count()} cards created")

# ===== SUMMARY =====
print("\n✅ Seed complete!")
print(f"{'='*50}")
print(f"  Superadmin → admin    / admin123")
print(f"  Owner 1    → owner1   / owner123  (boards: Frontend, Backend)")
print(f"  Owner 2    → owner2   / owner123  (boards: DevOps, Design)")
print(f"  User 1     → user1    / user123   (member: Frontend, Design)")
print(f"  User 2     → user2    / user123   (member: Frontend, Backend)")
print(f"  User 3     → user3    / user123   (member: Frontend, DevOps)")
print(f"  User 4     → user4    / user123   (member: Backend, Design)")
print(f"  User 5     → user5    / user123   (member: DevOps, Design)")
print(f"{'='*50}")
print(f"  Boards  → {Board.objects.count()}")
print(f"  Columns → {Column.objects.count()}")
print(f"  Cards   → {Card.objects.count()}")
print(f"{'='*50}")
print(f"  ⚠️  user1 has a card: 'Card assigned to user1' (for permission tests)")
