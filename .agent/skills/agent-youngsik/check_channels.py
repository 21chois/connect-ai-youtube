import os
import pickle
from googleapiclient.discovery import build

def check():
    for account in ["main", "sub"]:
        token_path = f"../../../token_{account}.pickle" if account != "main" else "../../../token_upload.pickle"
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
                print(f"  ✅ Channel: {title}")
            else:
                print("  ❌ No channel found for this token")
        except Exception as e:
            print(f"  ❌ Error: {e}")

if __name__ == "__main__":
    check()
