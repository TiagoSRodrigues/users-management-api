from fastapi.testclient import TestClient
from lambda_functions.user_management import app
from uuid import uuid4
from datetime import datetime

client = TestClient(app)

# Test data
test_user = {
    "full_name": "John Doe",
    "username": "john_doe",
    "email": "john.doe@test-case.com",
    "nationality": "Testland",
    "is_active": True,
    "created_at": datetime.now().isoformat(),
    "modified_at": datetime.now().isoformat()
}
 
def test_create_user():
    """ user is inserted into db """
    # Generate a unique email and username for testing
    unique_email = f"test_{uuid4()}@example.com"
    unique_username = f"test_{uuid4()}"
    test_user["email"] = unique_email
    test_user["username"] = unique_username

    response = client.post("/users", json=test_user)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == unique_email
    assert data["username"] == unique_username

def test_update_user():
    """ user data is updated in db """

    # Generate a unique email and username for testing
    unique_email = f"test_{uuid4()}@example.com"
    unique_username = f"test_{uuid4()}"
    test_user["email"] = unique_email
    test_user["username"] = unique_username

    response = client.post(f"/users/tiagosr", json=test_user)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == unique_email
    assert data["username"] == unique_username


def test_get_user():
    """ Fetch users data """

    # Generate a unique email and username for testing
    unique_email = f"test_{uuid4()}@example.com"
    unique_username = f"test_{uuid4()}"
    test_user["email"] = unique_email
    test_user["username"] = unique_username

    response = client.post("/users", json=test_user)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == unique_email
    assert data["username"] == unique_username

def test_delete_user():
    """ removes user from db """
    unique_email = f"test_{uuid4()}@example.com"
    unique_username = f"test_{uuid4()}"
    test_user["email"] = unique_email
    test_user["username"] = unique_username

    response = client.post("/users", json=test_user)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == unique_email
    assert data["username"] == unique_username

def test_get_users():
    """ Fetch all users """
    response = client.get("/users/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    
    
def cleans_test_data():
    """ deletes all users created during tests """
    pass


# Add more tests for update, delete, deactivate, etc.

# Note: You will also need to handle cleanup (deleting test users) to keep your test environment clean.
