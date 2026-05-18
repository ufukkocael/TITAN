import requests
import time

def test_gateway():
    print("🔍 Testing API Gateway at http://127.0.0.1:9000")
    try:
        r = requests.get("http://127.0.0.1:9000/", timeout=5)
        print(f"✅ Gateway is ALIVE. Status: {r.status_code}")
        print(f"📄 Response: {r.json()}")
    except Exception as e:
        print(f"❌ Gateway is UNREACHABLE: {e}")

    print("\n🔍 Testing Auth Login...")
    try:
        r = requests.post("http://127.0.0.1:9000/auth/login", 
                          data={"username": "admin", "password": "titan2026"}, 
                          timeout=5)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            print("✅ Login SUCCESS")
            print(f"🔑 Token: {r.json().get('access_token')[:20]}...")
        else:
            print(f"❌ Login FAILED: {r.text}")
    except Exception as e:
        print(f"❌ Auth Test ERROR: {e}")

if __name__ == "__main__":
    test_gateway()
