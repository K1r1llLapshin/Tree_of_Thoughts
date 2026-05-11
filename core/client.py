import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class LLMClient:
    def __init__(self, model_name: str = "deepseek-chat", temperature: float = 0.7):
        self.model_name = model_name
        self.temperature = temperature
        
        # Получаем данные из .env
        self.api_key = os.getenv("AITUNNEL_API_KEY")
        self.api_base = os.getenv("AITUNNEL_BASE_URL")
        
        if not self.api_key:
            print("ОШИБКА: AITUNNEL_API_KEY не найден!")

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.api_base
        )
    
    def generate(self, prompt: str) -> dict:
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
            )
            
            # Получаем токены из ответа API
            total_tokens = response.usage.total_tokens
            
            return {
                "text": response.choices[0].message.content,
                "tokens": total_tokens
            }
        except Exception as e:
            return {
                "text": f"ОШИБКА: {str(e)}", 
                "tokens": 0
            }


