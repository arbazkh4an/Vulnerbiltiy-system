import time
from jose import jwt
import httpx
from pathlib import Path

def get_config():
    env_path = Path("backend/.env")
    with open(env_path, "r") as f:
        env_content = f.read()
    
    config = {}
    for line in env_content.splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            config[k.strip()] = v.strip()
    return config

def generate_token(secret):
    payload = {
        "sub": "test_user_agent",
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600
    }
    return jwt.encode(payload, secret, algorithm="HS256")

def run_test(target_url):
    config = get_config()
    secret = config.get("JWT_SECRET")
    if not secret:
        print("JWT_SECRET not found")
        return

    token = generate_token(secret)
    headers = {"Authorization": f"Bearer {token}"}
    
    api_base = "http://localhost:5000/api"
    
    print(f"Starting scan for: {target_url}")
    with httpx.Client(timeout=30) as client:
        # 1. Start Scan
        try:
            resp = client.post(
                f"{api_base}/scan",
                json={"url": target_url, "consent": True},
                headers=headers
            )
            resp.raise_for_status()
            scan_id = resp.json()["scan_id"]
            print(f"Scan initiated! ID: {scan_id}")
        except Exception as e:
            print(f"Failed to start scan: {e}")
            if hasattr(e, 'response'):
                print(e.response.text)
            return

        # 2. Poll for results
        print("Polling for results (this may take a minute)...")
        for _ in range(60): # 5 minutes max
            time.sleep(5)
            try:
                resp = client.get(f"{api_base}/scan/{scan_id}", headers=headers)
                resp.raise_for_status()
                data = resp.json()
                status = data["status"]
                progress = data.get("progress", 0)
                print(f"Status: {status} ({progress}%)")
                
                if status == "complete":
                    print("\n--- SCAN COMPLETE ---")
                    print(f"Total Vulnerabilities: {data.get('total_vulnerabilities', 0)}")
                    print(f"Critical: {data.get('critical_count', 0)}")
                    print(f"High: {data.get('high_count', 0)}")
                    print(f"Medium: {data.get('medium_count', 0)}")
                    print(f"Low: {data.get('low_count', 0)}")
                    if data.get("ai_report"):
                        print("\nAI Summary:")
                        print(data["ai_report"].get("summary", "No summary provided"))
                    return
                elif status == "failed":
                    print(f"Scan failed: {data.get('error_message')}")
                    return
            except Exception as e:
                print(f"Error polling: {e}")
        
        print("Test timed out.")

if __name__ == "__main__":
    import sys
    url = sys.argv[1] if len(sys.argv) > 1 else "https://portfolio-fqnk.vercel.app/"
    run_test(url)
