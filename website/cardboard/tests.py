from django.test import TestCase

# Create your tests here.
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from website.cardboard.models import Board, Card, Column


class BoardTests(APITestCase):
    
    def setUp(self):
        owner = User.objects.create_user(
            username="owner", password="owner", is_staff= True
        )
        self.users = []
        for i in range(3):
            self.users.append(User.objects.create_user(
                username=f"user{i}", password="user", is_staff= False
            ))


        # fill the DB
        Board.objects.create(
            name= "b1",
            owner= owner,
        )
        Board.objects.create(
            name= "b2",
            owner= owner,
        )
        Board.objects.get(name="b2").members.add(self.users[0].pk)
        Board.objects.get(name="b1").members.add(self.users[1].pk)
    
    def test_list_boards(self):
        self.user = self.users[0]
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/boards/")
        board_name_list = [b["name"] for b in response.data]
        self.assertEqual(board_name_list, ["b2"])

    def test_create_boards(self):
        self.user = User.objects.get(username="owner")
        self.client.force_authenticate(user=self.user)
        response = self.client.post("/api/boards/",{"name": "b3", "owner": self.user.id, "members":[self.users[2].pk]}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_normal_user_create_boards(self):
        self.user = self.users[1]
        self.client.force_authenticate(user=self.user)
        response = self.client.post("/api/boards/",{"name": "b2", "owner": self.user.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ColumnsTest(APITestCase):
    
    def setUp(self):
        self.owners = [User.objects.create_user(
            username="owner1", password="owner", is_staff= True
        ),User.objects.create_user(
            username="owner2", password="owner", is_staff= True
        )]

        self.users = []
        for i in range(3):
            self.users.append(User.objects.create_user(
                username=f"user{i}", password="user", is_staff= False
            ))


        # fill the DB
        self.boards = []
        self.boards.append(Board.objects.create(
            name= "b1",
            owner= self.owners[0],
        ))
        self.boards.append(Board.objects.create(
            name= "b2",
            owner= self.owners[1],
        ))
        self.boards[0].members.add(self.users[0].pk)
        self.boards[1].members.add(self.users[1].pk)

        for i in range(3):
            Column.objects.create(
                name=f"C1{i}",
                board=self.boards[0],
                order=i
            )
            Column.objects.create(
                name=f"C2{i}",
                board=self.boards[1],
                order=i
            )

    def test_list_column(self):
        self.user = self.owners[0]
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/columns/")
        print(response.data)
        board_name_list = [b["name"] for b in response.data]
        self.assertEqual(len(board_name_list),3)
        self.assertIn( "C10",board_name_list)
        self.assertIn( "C11",board_name_list)
        self.assertIn( "C12",board_name_list)
        
    def test_create_lists(self):
        self.user = self.owners[0]
        self.client.force_authenticate(user=self.user)
        response = self.client.post("/api/columns/",
                {
                    "name": "C14",
                    "owner": self.user.id,
                    "members":[self.users[0].pk],
                    "board": self.boards[0].pk
                },
                format='json'
            )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post("/api/columns/",
                {
                    "name": "C15",
                    "owner": self.user.id,
                    "members":[self.users[1].pk]},
                    "board": self.boards[0].pk
                format='json'
            )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        response = self.client.post("/api/columns/",
                {
                    "name": "C16",
                    "owner": self.user.id,
                    "members":[self.users[0].pk],
                    "board": self.boards[1].pk
                },
                format='json'
            )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)