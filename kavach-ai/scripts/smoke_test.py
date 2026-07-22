import os
import requests
import time

SERVICES = {
    "API Gateway": "http://localhost:4000/health",
    "Core Intelligence": "http://localhost:4001/health",
    "Evidence Vault": "http://localhost:4002/health",
    "AI Orchestrator": "http://localhost:4003/health",
    "Fraud Network": "http://localhost:4004/health",
    "Geospatial Intelligence": "http://localhost:4005/health",
}

def check_service(name, url):
    try:
        res = requests.get(url, timeout=3)
        if res.status_code == 200:
            print(f"✅ {name}: UP")
            return True
        else:
            print(f"❌ {name}: DOWN (Status: {res.status_code})")
            return False
    except Exception as e:
        print(f"❌ {name}: UNREACHABLE ({e})")
        return False

def main():
    print("--- KAVACH AI: End-to-End Smoke Test ---")
    
    all_passed = True
    for name, url in SERVICES.items():
        if not check_service(name, url):
            all_passed = False

    print("\n----------------------------------------")
    if all_passed:
        print("🚀 ALL SYSTEMS NOMINAL. Platform is ready for demo.")
        exit(0)
    else:
        print("⚠️ SOME SYSTEMS FAILED. Check Docker logs.")
        exit(1)

if __name__ == "__main__":
    main()
