from .search import Search
from core.thought import Thought
from core.prompts.generate_thought import *

class DFS(Search):
    def __init__(self, client, count_thoughts: int, max_depth: int, threshold: float):
        """
        client: Экземпляр LLMClient
        count_thoughts: Количество генерируемых вариантов на каждом узле
        max_depth: Максимальная глубина поиска
        threshold: Минимальный порог оценки (если ниже — ветка отсекается)
        """
        super().__init__() # Инициализация метрик 
        self.client = client
        self.count_thoughts = count_thoughts
        self.max_depth = max_depth
        self.threshold = threshold
        

    def solve(self, problem: str) -> str:
        # Инициализация дерева
        root = Thought(state=problem, role="root") 
        self.all_thoughts.append(root) # Добавление кореня в логи
        
        # Запуск поиска
        target_thought = self._search(problem, root, 0)
        ans = self._get_final_answer(problem, target_thought)    
        self.save_logs() # Сохраняем логи перед выходом
        return ans

    def _search(self, problem: str, current_thought: Thought, depth: int) -> None:
         # Выбирается промт для каждого уровня 
        if depth >= self.max_depth:
            return

        if depth == 0:
            prompt = START_PROMPT.format(problem=problem, k=self.count_thoughts)
        else:
            history = "\n".join(current_thought.get_path())
            prompt = THOUGHT_PROMPT.format(problem=problem, history=history, k=self.count_thoughts)
        
        # Запрос генерации
        response = self.client.generate(prompt)
        
        # Обновление глобальных статистик
        self.total_tokens += response["tokens"]
        self.total_price += response["price"]
        
        raw_thoughts_text = response["text"]
        thoughts_texts = self._parse_thoughts(raw_thoughts_text)

        # Распределение времени/стоимости генерации поровну между новыми мыслями
        gen_price_per_thought = response["price"] / max(len(thoughts_texts), 1)
        gen_time_per_thought = response["time"] / max(len(thoughts_texts), 1)

        
        candidates = []
        # Создание мыслей и оценка 
        for text in thoughts_texts:
            child = Thought(state=text, role="thought", parent=current_thought)
        
            # Присваиваем долю ресурсов, затраченных на генерацию
            child.price += gen_price_per_thought
            child.time += gen_time_per_thought
            
            score, feedback = self._evaluate(problem, child)
            child.set_score(score, feedback)
            candidates.append(child)
                    
            self.all_thoughts.append(child) # Сохраняем в общий лог

        candidates.sort(key=lambda x: x.score, reverse=True)

        for candidate in candidates:
            if candidate.score >= 1.0:
                return candidate

            if candidate.score >= self.threshold:
                current_thought.add_child(candidate)
                result = self._search(problem, candidate, depth + 1)
                if result:
                    return result
           