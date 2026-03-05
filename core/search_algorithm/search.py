import re
from typing import List
from core.thought import Thought
from core.promts.generate_thought import SUMMARY_PROMT
from core.promts.evaluator_thought import EVALUATOR_PROMT

class Search:
    def _evaluate(self, problem: str, thought: Thought):
        history = "\n".join(thought.parent.get_path()) if thought.parent else "Начало"
        prompt = EVALUATOR_PROMT.format(
            problem=problem, 
            history=history, 
            current_thought=thought.state
        )
        
        response = self.client.generate(prompt)
        
        score = 0.0
        feedback = ""
        
        score_match = re.search(r"SCORE:\s*([\d.]+)", response)
        feedback_match = re.search(r"FEEDBACK:\s*(.*)", response, re.DOTALL)
        
        if score_match:
            score = float(score_match.group(1))
        if feedback_match:
            feedback = feedback_match.group(1).strip()
        
        return score, feedback


    def _parse_thoughts(self, text: str) -> List[str]:
        thoughts = re.findall(r"Thought\s*\d+:\s*(.*?)(?=(?:Thought\s*\d+:)|$)", text, re.DOTALL)
        return [t.strip() for t in thoughts if t.strip()]


    def _get_final_answer(self, problem: str, best_thought: Thought) -> str:
        history = "\n".join(best_thought.get_path())
        prompt = SUMMARY_PROMT.format(problem=problem, history=history)
        return self.client.generate(prompt)
    
    
    