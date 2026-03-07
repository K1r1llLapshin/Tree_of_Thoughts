from .search import Search
from core.thought import Thought
from core.prompts.generate_thought import *

class BFS(Search):
    def __init__(self, client, count_thoughts: int, breadth_limit: int, max_depth: int):
        """
        client: Экземпляр LLMClient
        count_thoughts: Количество генерируемых мыслей на каждом шаге
        breadth_limit: Количество лучших мыслей оставляем для следующего уровня
        max_depth: Максимальная глубина дерева
        """
        super().__init__() # Инициализация метрик 
        self.client = client
        self.count_thoughts = count_thoughts
        self.breadth_limit = breadth_limit
        self.max_depth = max_depth
            
    def solve(self, problem: str) -> str:
        # Инициализация дерева
        root = Thought(state=problem, role="root")
        current_level_thoughts = [root]
        
        self.all_thoughts.append(root) # Добавление кореня в логи
        
        for depth in range(self.max_depth):
            
            if current_level_thoughts[0].score >= 1.0:
                break
            
            new_candidates = []
            
            for parent_thought in current_level_thoughts:
                # Выбирается промт для каждого уровня 
                if depth == 0:
                    prompt = START_PROMPT.format(problem=problem, k=self.count_thoughts)
                else:
                    history = "\n".join(parent_thought.get_path())
                    prompt = THOUGHT_PROMPT.format(problem=problem, history=history, k=self.count_thoughts)

                # Запрос генерации
                response_data = self.client.generate(prompt)
                
                # Обновление глобальных статистк
                self.total_tokens += response_data["tokens"]
                
                raw_thoughts = response_data["text"]
                thoughts_texts = self._parse_thoughts(raw_thoughts)

                # Распределение времени генерации поровну между новыми мыслями
                gen_time_per_thought = response_data["time"] / max(len(thoughts_texts), 1)

                # Создание мыслей и оценка 
                for text in thoughts_texts:
                    child = Thought(state=text, role="thought", parent=parent_thought)
                    
                    # Присваиваем долю ресурсов, затраченных на генерацию
                    child.time += gen_time_per_thought
                    
                    score, feedback = self._evaluate(problem, child)
                    child.set_score(score, feedback)
                    parent_thought.add_child(child)
                    new_candidates.append(child)
                    
                    self.all_thoughts.append(child) # Сохраняем в общий лог

            # Сортировка и выбор лучших мыслей по оценке
            new_candidates.sort(key=lambda x: x.score, reverse=True)
            current_level_thoughts = new_candidates[:self.breadth_limit]
       
        ans = self._get_final_answer(problem, current_level_thoughts[0])    
        self.save_logs()
        return ans
 


    