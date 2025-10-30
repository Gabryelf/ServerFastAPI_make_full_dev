import requests
import json


def test_user_registration():
    print("=== Testing User Registration ===")

    url = "http://localhost:8000/api/register"
    data = {
        "email": "testuser@example.com",
        "password": "testpassword123",
        "full_name": "Test User"
    }

    try:
        print(f"Sending request to: {url}")
        print(f"Data: {json.dumps(data, indent=2)}")

        response = requests.post(url, json=data)

        print(f"Status Code: {response.status_code}")
        print(f"Response Text: {response.text}")

        if response.status_code == 200:
            print("✅ User registration successful")
            user_data = response.json()
            print(f"User created: {user_data}")
        else:
            print("❌ User registration failed")
            try:
                error_data = response.json()
                print(f"Error details: {error_data}")
            except:
                print(f"Raw error: {response.text}")

    except Exception as e:
        print(f"❌ Connection error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_user_registration()