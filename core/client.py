import os
import time
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
        start_time = time.time()
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
            )
            end_time = time.time()
            
            # Получаем токены из ответа API
            prompt_tokens = response.usage.prompt_tokens
            completion_tokens = response.usage.completion_tokens
            total_tokens = response.usage.total_tokens
            
            # Примерный расчет стоимости 
            price = (prompt_tokens * 53.76 / 1_000_000) + (completion_tokens * 80.64 / 1_000_000) # 53.76 руб. за 1M токенов ввода, 80.64 руб. за 1M вывода (06.03.2026)

            return {
                "text": response.choices[0].message.content,
                "tokens": total_tokens,
                "price": price,
                "time": end_time - start_time
            }
        except Exception as e:
            return {
                "text": f"ОШИБКА: {str(e)}", 
                "tokens": 0, 
                "price": 0.0, 
                "time": time.time() - start_time
            }


