import google.generativeai as genai

# Өзіңіз алған API кілтті мына жерге қойыңыз
GEMINI_API_KEY = "AIzaSyCl4YeZ_V3ojAmKJPPSCjMg6j-DlRSM9jI"

genai.configure(api_key=GEMINI_API_KEY)

def generate_study_plan(topic, days):
    """
    Пайдаланушы енгізген тақырып пен күндер санына байланысты
    AI арқылы оқу жоспарын мәтін түрінде генерациялайтын функция.
    """
    try:
        # Ең тұрақты әрі жылдам модельді таңдаймыз
       model = genai.GenerativeModel('gemini-1.5-flash')
        
        # AI-ға нақты тапсырма (Prompt) дайындаймыз
       prompt = f"""
        Сен кәсіби академиялық кеңесшісің. 
        Маған "{topic}" тақырыбын {days} күн ішінде меңгеруге арналған нақты оқу жоспарын құрып бер.
        Жоспар таза қазақ тілінде, түсінікті әрі құрылымды (әр күнге бөлінген тапсырмалармен) болуы керек.
        """
        
       response = model.generate_content(prompt)
       return response.text
    except Exception as e:
        return f"AI-мен байланыс орнату кезінде қате шықты: {str(e)}"
    
    import json

import json
import re

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
        
        # Регулярлық өрнек арқылы тек [...] арасындағы JSON-ды суырып аламыз (Қателіктен сақтау)
        match = re.search(r'\[.*\]', text, re.DOTALL)
        if match:
            clean_text = match.group(0)
        else:
            clean_text = text.replace("```json", "").replace("```", "").strip()
            
        return json.loads(clean_text)
    except Exception as e:
        print("Quiz Generation Error:", e)
        # Егер AI қате формат берсе, бағдарлама құламауы үшін дайын 3 тест сұрағын қайтарамыз
        return [
            {"question": f"{topic} негіздерін түсіндіңіз бе?", "A": "Иә, бәрі түсінікті", "B": "Жартылай", "C": "Жоқ, қайталау керек", "correct": "A"},
            {"question": f"{topic} бойынша тапсырмаларды орындадыңыз ба?", "A": "Иә", "B": "Енді бастаймын", "C": "Жоқ", "correct": "A"},
            {"question": f"{topic} қиын болды ма?", "A": "Жоқ, оңай", "B": "Орташа", "C": "Өте қиын", "correct": "B"}
        ]