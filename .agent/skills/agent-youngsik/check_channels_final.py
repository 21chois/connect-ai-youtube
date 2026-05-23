import os
import sys
import pickle
from googleapiclient.discovery import build

# [설정] 프로젝트 루트 확보
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", ".."))

def check():
    os.chdir(ROOT_DIR)
    for account in ["main", "sub"]:
        token_path = "token_upload.pickle" if account == "main" else f"token_{account}.pickle"
        print(f"Checking {account} ({token_path})...")
        if not os.path.exists(token_path):
            print(f"  ❌ File not found")
            continue
        try:
            with open(token_path, "rb") as f:
                creds = pickle.load(f)
            service = build("youtube", "v3", credentials=creds)
            res = service.channels().list(part="snippet", mine=True).execute()
            if "items" in res:
                title = res["items"][0]["snippet"]["title"]
                print(f"  ✅ Channel: [{title}]")
            else:
                print("  ❌ No channel found")
        except Exception as e:
            print(f"  ❌ Error: {e}")

if __name__ == "__main__":
    check()
