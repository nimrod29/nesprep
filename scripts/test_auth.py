#!/usr/bin/env python3
"""Test script for auth endpoints."""

import httpx

BASE_URL = "http://localhost:8000/api"


def test_auth_flow():
    """Test the complete auth flow: signup, signin, and /me."""
    print("=" * 60)
    print("Testing Auth Endpoints")
    print("=" * 60)

    # Test 1: Signup
    print("\n1. Testing signup...")
    signup_data = {
        "email": "test@example.com",
        "password": "securepassword123",
        "name": "Test Manager",
        "role": "מנהל בוטיק",
    }

    response = httpx.post(f"{BASE_URL}/auth/signup", json=signup_data)
    print(f"   Status: {response.status_code}")

    if response.status_code == 201:
        data = response.json()
        print(f"   Manager ID: {data['manager']['id']}")
        print(f"   Name: {data['manager']['name']}")
        print(f"   Role: {data['manager']['role']}")
        print(f"   Token: {data['access_token'][:50]}...")
        access_token = data["access_token"]
    else:
        print(f"   Error: {response.json()}")
        return False

    # Test 2: Duplicate signup should fail
    print("\n2. Testing duplicate signup (should fail)...")
    response = httpx.post(f"{BASE_URL}/auth/signup", json=signup_data)
    print(f"   Status: {response.status_code}")
    if response.status_code == 409:
        print("   Correctly rejected duplicate email")
    else:
        print(f"   Unexpected response: {response.json()}")

    # Test 3: Signin
    print("\n3. Testing signin...")
    signin_data = {
        "email": "test@example.com",
        "password": "securepassword123",
    }

    response = httpx.post(f"{BASE_URL}/auth/signin", json=signin_data)
    print(f"   Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"   Manager ID: {data['manager']['id']}")
        print(f"   Name: {data['manager']['name']}")
        print("   Signin successful!")
    else:
        print(f"   Error: {response.json()}")
        return False

    # Test 4: Wrong password
    print("\n4. Testing wrong password (should fail)...")
    wrong_signin = {
        "email": "test@example.com",
        "password": "wrongpassword",
    }

    response = httpx.post(f"{BASE_URL}/auth/signin", json=wrong_signin)
    print(f"   Status: {response.status_code}")
    if response.status_code == 401:
        print("   Correctly rejected wrong password")
    else:
        print(f"   Unexpected response: {response.json()}")

    # Test 5: Get /me with valid token
    print("\n5. Testing /me endpoint with valid token...")
    headers = {"Authorization": f"Bearer {access_token}"}
    response = httpx.get(f"{BASE_URL}/auth/me", headers=headers)
    print(f"   Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"   Manager ID: {data['id']}")
        print(f"   Email: {data['email']}")
        print(f"   Name: {data['name']}")
        print(f"   Role: {data['role']}")
    else:
        print(f"   Error: {response.json()}")
        return False

    # Test 6: Get /me without token
    print("\n6. Testing /me endpoint without token (should fail)...")
    response = httpx.get(f"{BASE_URL}/auth/me")
    print(f"   Status: {response.status_code}")
    if response.status_code in (401, 403):
        print("   Correctly rejected unauthenticated request")
    else:
        print(f"   Unexpected response: {response.json()}")

    # Test 7: Get /me with invalid token
    print("\n7. Testing /me endpoint with invalid token (should fail)...")
    headers = {"Authorization": "Bearer invalid_token_here"}
    response = httpx.get(f"{BASE_URL}/auth/me", headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 401:
        print("   Correctly rejected invalid token")
    else:
        print(f"   Unexpected response: {response.json()}")

    # Test 8: Signup with different roles
    print("\n8. Testing signup with different roles...")
    roles = ["מנהל אזור", "הנהלה בכירה"]
    for i, role in enumerate(roles, start=2):
        signup_data = {
            "email": f"manager{i}@example.com",
            "password": "password123",
            "name": f"Manager {i}",
            "role": role,
        }
        response = httpx.post(f"{BASE_URL}/auth/signup", json=signup_data)
        if response.status_code == 201:
            data = response.json()
            print(f"   Created manager with role '{role}': ID={data['manager']['id']}")
        else:
            print(f"   Failed to create manager with role '{role}': {response.json()}")

    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    test_auth_flow()
