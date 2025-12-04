import requests
import json

BASE_URL = "http://localhost:8000"

print("=== Testing Traffic Management API ===\n")

# Test 1: Root endpoint
print("1. Testing root endpoint...")
try:
    response = requests.get(f"{BASE_URL}/")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}\n")
except Exception as e:
    print(f"   Error: {e}\n")

# Test 2: Current traffic data
print("2. Testing current traffic endpoint...")
try:
    response = requests.get(f"{BASE_URL}/api/traffic/current")
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Found {len(data)} traffic records\n")
except Exception as e:
    print(f"   Error: {e}\n")

# Test 3: Active emergency overrides
print("3. Testing emergency overrides endpoint...")
try:
    response = requests.get(f"{BASE_URL}/api/traffic/emergency/active")
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Active overrides: {data.get('count', 0)}\n")
except Exception as e:
    print(f"   Error: {e}\n")

# Test 4: Detection statistics
print("4. Testing detection statistics endpoint...")
try:
    response = requests.get(f"{BASE_URL}/api/traffic/detection-statistics/junction_01")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Location: {data.get('location_id')}")
        print(f"   Total vehicles: {data.get('total_vehicles', 0)}\n")
    else:
        print(f"   Response: {response.json()}\n")
except Exception as e:
    print(f"   Error: {e}\n")

# Test 5: Signals list
print("5. Testing signals endpoint...")
try:
    response = requests.get(f"{BASE_URL}/api/signals/")
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Found {len(data)} signals\n")
except Exception as e:
    print(f"   Error: {e}\n")

print("=== API Tests Complete ===")
