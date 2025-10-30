import requests
import json


def test_admin_login():
    print("=== Testing Admin Login ===")

    url = "http://localhost:8000/api/login"
    data = {
        "email": "admin@admin.com",
        "password": "admin123"
    }

    try:
        print(f"Sending request to: {url}")
        print(f"Data: {json.dumps(data, indent=2)}")

        response = requests.post(url, json=data)

        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Text: {response.text}")

        if response.status_code == 200:
            print("✅ Admin login successful")
            token_data = response.json()
            print(f"Token: {token_data.get('access_token', 'NOT FOUND')}")

            # Тестируем получение информации о пользователе
            me_url = "http://localhost:8000/api/me"
            headers = {
                "Authorization": f"Bearer {token_data['access_token']}"
            }
            me_response = requests.get(me_url, headers=headers)
            print(f"User info status: {me_response.status_code}")
            print(f"User info: {me_response.text}")

        else:
            print("❌ Admin login failed")
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
    test_admin_login()