import re
import uuid
import os
import json
import time
from typing import List
from core.thought import Thought
from core.prompts.generate_thought import SUMMARY_PROMPT
from core.prompts.evaluator_thought import EVALUATOR_PROMPT

class Search:
    def __init__(self):
        '''
        all_thoughts: список всех мыслей
        total_tokens: общее количество токенов
        total_price: общая стоимость генерации
        start_time: время начала поиска
        '''
        self.all_thoughts = []
        self.total_tokens = 0
        self.total_price = 0.0
        self.start_time = time.time()
        
    def _evaluate(self, problem: str, thought: Thought):
        '''Оценщик мысли'''
        history = "\n".join(thought.parent.get_path()) if thought.parent else "Начало"
        prompt = EVALUATOR_PROMPT.format(
            problem=problem, 
            history=history, 
            current_thought=thought.state
        )
        
       # Получаем словарь с данными
        response_data = self.client.generate(prompt)
        text = response_data["text"]
        
        # Обновляем глобальную статистику
        self.total_tokens += response_data["tokens"]
        self.total_price += response_data["price"]
        
        # Добавляем время и стоимость оценки к самой мысли
        thought.price += response_data["price"]
        thought.time += response_data["time"]
        
        score = 0.0
        feedback = ""
        
        score_match = re.search(r"SCORE:\s*([\d.]+)", text)
        feedback_match = re.search(r"FEEDBACK:\s*(.*)", text, re.DOTALL)
        
        if score_match:
            score = float(score_match.group(1))
        if feedback_match:
            feedback = feedback_match.group(1).strip()
        
        return score, feedback


    def _parse_thoughts(self, text: str) -> List[str]:
        '''Парсит мысли из текста'''
        thoughts = re.findall(r"Thought\s*\d+:\s*(.*?)(?=(?:Thought\s*\d+:)|$)", text, re.DOTALL)
        return [t.strip() for t in thoughts if t.strip()]


    def _get_final_answer(self, problem: str, best_thought: Thought) -> str:
        '''Возвращает ответ на вопрос'''
        history = "\n".join(best_thought.get_path())
        prompt = SUMMARY_PROMPT.format(problem=problem, history=history)
        ans = self.client.generate(prompt)
        
        # Обновление глобальных статистк
        self.total_tokens += ans["tokens"]
        self.total_price += ans["price"]
        raw_thoughts = ans["text"]
        
        child = Thought(state=raw_thoughts, role="final_answer", parent=best_thought)
        child.price = ans["price"]
        child.time = ans["time"]
        
        score, feedback = self._evaluate(problem, child)
        child.set_score(score, feedback)
        best_thought.add_child(child)
        self.all_thoughts.append(child) # Сохраняем в общий лог
        return raw_thoughts.strip()
    
    def save_logs(self):
        """Сохраняет собранную информацию в JSON файл"""
        filename = f"./logs/search_logs_{uuid.uuid4()}.json"
        total_time = time.time() - self.start_time
        
        log_data = {
            "general_information": [
                {
                    "count_thoughts": len(self.all_thoughts),
                    "total_price": round(self.total_price, 6),
                    "total_tokens": self.total_tokens,
                    "total_time": round(total_time, 2)
                }
            ],
            "thoughts": [thought.to_dict() for thought in self.all_thoughts]
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, ensure_ascii=False, indent=4)
    
    
    