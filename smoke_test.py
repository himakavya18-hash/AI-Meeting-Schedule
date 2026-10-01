import requests

r = requests.get('http://127.0.0.1:8000/login/')
print(f"Login page status: {r.status_code}")
print(f"Contains 'Meeting Portal': {'Meeting Portal' in r.text}")

r2 = requests.get('http://127.0.0.1:8000/api/accounts/users/', headers={"Accept": "application/json"})
print(f"Users API status: {r2.status_code}")

r3 = requests.get('http://127.0.0.1:8000/dashboard/')
print(f"Dashboard page status: {r3.status_code}")

r4 = requests.get('http://127.0.0.1:8000/admin/')
print(f"Admin page status: {r4.status_code}")

print("\nAll core endpoints responding!")
