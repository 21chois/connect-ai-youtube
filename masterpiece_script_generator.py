import os
import sys
import re
from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Windows 콘솔 이모지 출력(cp949) 에러 방지용
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

if not api_key:
    print("❌ GEMINI_API_KEY 환경 변수가 없습니다.")
    sys.exit(1)

client = genai.Client(api_key=api_key)
MODEL_NAME = "gemini-2.5-pro" # 고퀄리티 추론을 위해 Pro 모델 사용

def generate_draft(topic):
    prompt = f"""
당신은 최고의 유튜브 쇼츠 기획자이자 대본 작가입니다.
주제: "{topic}"
위 주제로 시청자의 도파민을 분비시키고 끝까지 시청하게 만들 1분 이내의 유튜브 숏츠용 대본 초안을 작성해주세요.
내레이션과 간단한 시각적 연출(지문)을 포함해주세요.
"""
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )
    return response.text

def evaluate_script(script):
    prompt = f"""
당신은 냉혹하고 까다로운 유튜브 쇼츠 전문 PD입니다.
아래 대본을 읽고, 다음 4가지 기준에 따라 100점 만점으로 평가해주세요.
1. 후킹(Hooking): 처음 3초 안에 시청자의 시선을 사로잡는가?
2. 몰입도(Retention): 중간에 이탈하지 않고 끝까지 볼만한 긴장감이나 유머가 있는가?
3. 독창성(Originality): 뻔한 내용이 아닌, 예상을 깨는 전개인가?
4. 영상화 적합성: 시각적으로 표현하기 좋고 템포가 빠른가?

평가 결과는 반드시 아래 형식을 지켜주세요:
점수: [0~100 사이의 숫자]
피드백: [점수를 짜게 준 이유와 구체적인 수정 지시사항]

대본:
{script}
"""
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )
    
    text = response.text
    # 점수 파싱
    score_match = re.search(r"점수:\s*(\d+)", text)
    score = int(score_match.group(1)) if score_match else 0
    return score, text

def revise_script(topic, old_script, feedback):
    prompt = f"""
당신은 최고의 유튜브 쇼츠 작가입니다.
기존 대본이 PD에게 까다로운 피드백을 받았습니다.
피드백을 완벽하게 반영하여 대본을 완전히 뜯어고치고, 90점 이상의 '걸작'으로 업그레이드 해주세요.

주제: {topic}

[기존 대본]
{old_script}

[PD 피드백]
{feedback}

수정된 새로운 대본만 반환해주세요.
"""
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )
    return response.text

def run_masterpiece_generator(topic):
    print(f"🎬 [걸작 대본 생성기] 시작 - 주제: '{topic}'")
    
    script = generate_draft(topic)
    print("\n📝 [1회차 초안 생성 완료]")
    
    max_iterations = 3
    for i in range(1, max_iterations + 1):
        print(f"\n🔍 [PD 평가 진행 중... ({i}회차)]")
        score, feedback = evaluate_script(script)
        
        print(f"⭐ 현재 점수: {score}점")
        print(f"🗣️ PD 피드백:\n{feedback}\n")
        
        if score >= 90:
            print("🎉 [합격!] 90점 이상의 걸작 대본이 완성되었습니다!")
            break
        else:
            if i < max_iterations:
                print("🛠️ [수정 중] 피드백을 반영하여 대본을 다시 작성합니다...")
                script = revise_script(topic, script, feedback)
            else:
                print("⚠️ [종료] 최대 수정 횟수에 도달했습니다. 최종 대본을 반환합니다.")
                
    print("\n================ [최종 완성 대본] ================\n")
    print(script)
    print("\n==================================================\n")
    
    # 최종본 저장
    with open("masterpiece_script_final.txt", "w", encoding="utf-8") as f:
        f.write(script)
    print("💾 'masterpiece_script_final.txt' 파일로 저장되었습니다.")

if __name__ == "__main__":
    test_topic = "AI에게 나의 일정을 맡겼더니 생기는 일?"
    run_masterpiece_generator(test_topic)
