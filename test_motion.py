import os
import sys
from google import genai
from dotenv import load_dotenv

# 툴 경로 추가
sys.path.insert(0, os.path.abspath(".agent/tools"))
from image_shorts_maker import create_image_shorts

load_dotenv()

def test_motion():
    client = genai.Client()
    prompt = "A mystical white cat in a temple"
    subtitles = ["테스트 자막입니다. 시네마틱 무빙 엔진 작동 중!"]
    output_path = "test_motion.mp4"
    
    success = create_image_shorts(client, [prompt], output_path, subtitles)
    if success:
        print("Success!")
    else:
        print("Failed.")

if __name__ == "__main__":
    test_motion()
