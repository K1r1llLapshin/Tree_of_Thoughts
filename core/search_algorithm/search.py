import re
import uuid
import json
import time
from typing import List
from core.thought import Thought
from core.prompts.generate_thought import SUMMARY_PROMPT
from core.prompts.evaluator_thought import EVALUATOR_PROMPT
from core.visualizer import visualize_thoughts_tree

class Search:
    def __init__(self):
        '''
        all_thoughts: список всех мыслей
        total_tokens: общее количество токенов
        start_time: время начала поиска
        '''
        self.all_thoughts = []
        self.total_tokens = 0
        self.start_time = time.time()
        
    def _evaluate(self, problem: str, thought: Thought) -> float:
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
        
        # Добавляем время и стоимость оценки к самой мысли
        
        score = 0.0
        
        score_match = re.search(r"SCORE:\s*([\d.]+)", text)
        
        if score_match:
            score = float(score_match.group(1))
    
        return score


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
        raw_thoughts = ans["text"]
        
        child = Thought(state=raw_thoughts, role="final_answer", parent=best_thought)
        
        score = self._evaluate(problem, child)
        child.set_score(score)
        best_thought.add_child(child)
        self.all_thoughts.append(child) # Сохраняем в общий лог
        return raw_thoughts.strip()
    
    def save_logs(self, name_search: str, count_thoughts: int, breadth_limit_or_threshold: int, max_depth: int, problem: str, answer: str) -> str:
        """Сохраняет собранную информацию в JSON файл"""
        filename_json = f"D:/Tree_of_Thoughts/logs/json/search_logs_{uuid.uuid4()}.json"
        total_time = time.time() - self.start_time
        
        if (name_search == "BFS"):
            name_breadth_limit_or_threshold = "breadth_limit"
        else:
            name_breadth_limit_or_threshold = "threshold"
            
        log_data = {
            "parameters": [
                {
                    "name_search": name_search,
                    "count_thoughts": count_thoughts,
                    name_breadth_limit_or_threshold: breadth_limit_or_threshold,
                    "max_depth": max_depth
                }
            ],
            "general_information": [
                {
                    "count_thoughts": len(self.all_thoughts),
                    "total_tokens": self.total_tokens,
                    "total_time": round(total_time, 2)
                }
            ],
            "brief_summary": [
                {
                    "question": problem,
                    "answer": answer
                }   
            ],
            "thoughts": [thought.to_dict() for thought in self.all_thoughts]
        }
        
        with open(filename_json, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, ensure_ascii=False, indent=4)
        
        filename_png = visualize_thoughts_tree(filename_json)
        return filename_json, filename_png
        
        
    
    
    