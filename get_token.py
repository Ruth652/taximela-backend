import requests

resp = requests.post(
    "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword",
    params={"key": "AIzaSyDq-F0DEMOXC0TjXY3PfjgUgktJg4TPQDw"},
    json={
        "email": "ruthgashahun5@gmail.com",
        "password": "Ruth123",
        "returnSecureToken": True
    }
)

data = resp.json()

if "idToken" in data:
    print("\n✅ Token retrieved successfully!\n")
    print("Copy this token into Swagger Authorize:\n")
    print(data["idToken"])
else:
    print("\n❌ Failed to get token:")
    print(data)
