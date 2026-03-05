from search_algorithm.search import Search
from core.thought import Thought
from core.promts.generate_thought import *

class BFS(Search):
    def __init__(self, client, count_thoughts: int, breadth_limimt: int, max_depth: int):
            """
            client: Экземпляр LLMClient
            count_thoughts: Количество генерируемых мыслей на каждом шаге
            breadth_limimt: Количество лучших мыслей оставляем для следующего уровня
            max_depth: Максимальная глубина дерева
            """
            self.client = client
            self.count_thoughts = count_thoughts
            self.breadth_limimt = breadth_limimt
            self.max_depth = max_depth
            
    def solve(self, problem: str) -> str:
        # Инициализация дерева
        root = Thought(state=problem)
        current_level_thoughts = [root]

        for depth in range(self.max_depth):
            new_candidates = []

            for parent_thought in current_level_thoughts:
                if depth == 0:
                    prompt = START_PROMT.format(problem=problem, k=self.count_thoughts)
                else:
                    history = "\n".join(parent_thought.get_path())
                    prompt = THOUGHT_PROMT.format(problem=problem, history=history, k=self.count_thoughts)

                raw_thoughts = self.client.generate(prompt)
                thoughts_texts = self._parse_thoughts(raw_thoughts)

                # Создание мыслей и оценка 
                for text in thoughts_texts:
                    child = Thought(state=text, parent=parent_thought)
                    score, feedback = self._evaluate(problem, child)
                    child.set_score(score, feedback)
                    
                    parent_thought.add_child(child)
                    new_candidates.append(child)

                    if score >= 1.0:
                        return self._get_final_answer(problem, child)

            # Сортировка и выбор лучших мыслей по оценке
            new_candidates.sort(key=lambda x: x.score, reverse=True)
            current_level_thoughts = new_candidates[:self.breadth_limimt]

        # Финальный результат по лучшей цепочке из оставшихся
        best_final_thought = current_level_thoughts[0]
        return self._get_final_answer(problem, best_final_thought)
 


    