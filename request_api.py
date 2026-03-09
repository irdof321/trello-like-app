"""
Utilitaire de test API Django
Usage: python api_test.py
"""

import requests
import json

BASE_URL = "http://localhost:8000/api"
TOKEN = None

# ===== AUTH =====
def get_token(username="irdof", password="321321"):
    global TOKEN
    r = requests.post(f"{BASE_URL}/token/", json={"username": username, "password": password})
    if r.status_code == 200:
        TOKEN = r.json()["access"]
        print(f"✅ Token récupéré pour {username}")
    else:
        print(f"❌ Login failed → {r.status_code} {r.text}")
    return TOKEN

def headers():
    return {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

# ===== METHODES =====
def get(endpoint, params=None):
    """GET /api/<endpoint>/?param=value"""
    r = requests.get(f"{BASE_URL}/{endpoint}/", headers=headers(), params=params)
    print(f"\n→ GET /{endpoint}/ {params or ''}")
    print(f"  Status: {r.status_code}")
    print(f"  Response: {json.dumps(r.json(), indent=2)}")
    return r

def post(endpoint, data):
    """POST /api/<endpoint>/"""
    r = requests.post(f"{BASE_URL}/{endpoint}/", headers=headers(), json=data)
    print(f"\n→ POST /{endpoint}/")
    print(f"  Body: {json.dumps(data, indent=2)}")
    print(f"  Status: {r.status_code}")
    print(f"  Response: {json.dumps(r.json(), indent=2)}")
    return r

def put(endpoint, id, data):
    """PUT /api/<endpoint>/<id>/"""
    r = requests.put(f"{BASE_URL}/{endpoint}/{id}/", headers=headers(), json=data)
    print(f"\n→ PUT /{endpoint}/{id}/")
    print(f"  Body: {json.dumps(data, indent=2)}")
    print(f"  Status: {r.status_code}")
    print(f"  Response: {json.dumps(r.json(), indent=2)}")
    return r

def patch(endpoint, id, data):
    """PATCH /api/<endpoint>/<id>/"""
    r = requests.patch(f"{BASE_URL}/{endpoint}/{id}/", headers=headers(), json=data)
    print(f"\n→ PATCH /{endpoint}/{id}/")
    print(f"  Body: {json.dumps(data, indent=2)}")
    print(f"  Status: {r.status_code}")
    print(f"  Response: {json.dumps(r.json(), indent=2)}")
    return r

def delete(endpoint, id):
    """DELETE /api/<endpoint>/<id>/"""
    r = requests.delete(f"{BASE_URL}/{endpoint}/{id}/", headers=headers())
    print(f"\n→ DELETE /{endpoint}/{id}/")
    print(f"  Status: {r.status_code}")
    return r

# ===== TESTS =====
if __name__ == "__main__":
    # 1. Login
    get_token()

    # 2. Exemples — modifie comme tu veux

    # GET tous les boards
    get("boards")

    # GET colonnes d'un board spécifique
    get("columns", params={"board": 226})

    # GET cartes d'une colonne
    # get("cards", params={"column": 1})

    # POST créer une carte
    # post("cards", {
    #     "title": "Test carte",
    #     "content": "Contenu test",
    #     "status": "todo",
    #     "priority": "low",
    #     "column": 1,
    #     "order": 1,
    # })

    # PATCH modifier une carte
    # patch("cards", 1, {"status": "done"})

    # DELETE supprimer une carte
    # delete("cards", 1)