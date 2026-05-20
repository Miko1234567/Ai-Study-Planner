import google.generativeai as genai
import os
import json
import re

# API Кілтіңді осы жерге нақты жаз (Қос тырнақшаның ішіне)
API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyCl4YeZ_V3ojAmKJPPSCjMg6j-DlRSM9jI")
genai.configure(api_key=API_KEY)

def generate_study_plan(topic, days):
    try:
        # Ең тұрақты жұмыс істейтін модельді таңдадық
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        Сен кәсіби академиялық кеңесшісің. 
        Маған "{topic}" тақырыбын {days} күн ішінде меңгеруге арналған нақты оқу жоспарын құрып бер.
        Жоспар таза қазақ тілінде, түсінікті әрі құрылымды жазылсын.
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print("Gemini Plan Error:", e)
        return f"Жоспар құру сәтсіз аяқталды. Тақырып: {topic}, Күндер саны: {days}."

def generate_quiz_data(topic):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        Сен ұстазсың. "{topic}" тақырыбы бойынша студентті тексеру үшін 3 тест сұрағын құрастыр.
        Жауапты ТЕК мынадай қатаң JSON форматында қайтар (ешқандай артық мәтінсіз, тек массив):
        [
          {{
            "question": "Сұрақтың мәтіні?",
            "A": "А нұсқасы",
            "B": "Б нұсқасы",
            "C": "В нұсқасы",
            "correct": "A"
          }}
        ]
        Таза қазақ тілінде жаз.
        """
        
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        match = re.search(r'\[.*\]', text, re.DOTALL)
        if match:
            clean_text = match.group(0)
        else:
            clean_text = text.replace("```json", "").replace("```", "").strip()
            
        return json.loads(clean_text)
    except Exception as e:
        print("Gemini Quiz Error:", e)
        return [
            {"question": f"{topic} негіздерін түсіндіңіз бе?", "A": "Иә", "B": "Жартылай", "C": "Жоқ", "correct": "A"},
            {"question": f"{topic} бойынша тапсырма дайын ба?", "A": "Иә", "B": "Жоқ", "C": "Енді бастаймын", "correct": "A"},
            {"question": f"{topic} оңай ма?", "A": "Иә", "B": "Орташа", "C": "Жоқ", "correct": "B"}
        ]