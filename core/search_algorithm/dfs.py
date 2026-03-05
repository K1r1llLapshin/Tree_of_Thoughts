from search_algorithm.search import Search
from core.thought import Thought
from core.promts.generate_thought import *

class DFS(Search):
    def __init__(self, client, count_thoughts: int, max_depth: int, threshold: float):
        """
        client: Экземпляр LLMClient
        count_thoughts: Количество генерируемых вариантов на каждом узле
        max_depth: Максимальная глубина поиска
        threshold: Минимальный порог оценки (если ниже — ветка отсекается)
        """
        self.client = client
        self.count_thoughts = count_thoughts
        self.max_depth = max_depth
        self.threshold = threshold
        

    def solve(self, problem: str) -> str:
        root = Thought(state=problem)
        self.best_thought = root 
        
        # Запускаем поиск
        target_thought = self._search(problem, root, 0)
        
        return self._get_final_answer(problem, target_thought)

    def _search(self, problem: str, current_thought: Thought, depth: int) -> None:
        if depth >= self.max_depth:
            return

        if depth == 0:
            prompt = START_PROMT.format(problem=problem, k=self.count_thoughts)
        else:
            history = "\n".join(current_thought.get_path())
            prompt = THOUGHT_PROMT.format(problem=problem, history=history, k=self.count_thoughts)

        raw_thoughts = self.client.generate(prompt)
        thoughts_texts = self._parse_thoughts(raw_thoughts)
        
        candidates = []
        for text in thoughts_texts:
            child = Thought(state=text, parent=current_thought)
            score, feedback = self._evaluate(problem, child)
            child.set_score(score, feedback)
            candidates.append(child)

        candidates.sort(key=lambda x: x.score, reverse=True)

        for candidate in candidates:
            
            if candidate.score >= 1.0:
                return candidate

            if candidate.score >= self.threshold:
                current_thought.add_child(candidate)
                self._search(problem, candidate, depth + 1)
           