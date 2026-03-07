import uuid
from typing import List, Optional

class Thought:
    def __init__(self, state: str, role: str, parent: Optional['Thought'] = None):
        self.id = str(uuid.uuid4()) # Уникальный ID мысли
        self.role = role       # Текст мысли
        self.state = state          # Текст мысли
        self.parent = parent        # Ссылка на узел выше
        self.children: List[Thought] = []
        self.score = 0.0            # Оценка 
        self.feedback = ""          # Текстовое обоснование оценки от ИИ
        self.time = 0.0

    def set_score(self, score: float, feedback: str):
        """Устанавливает оценку"""
        self.score = score
        self.feedback = feedback
    
    def set_parent(self, parent: 'Thought'):
        """Устанавливает родительский узел"""
        self.parent = parent    
        
    def add_child(self, child: 'Thought'):
        """Добавляет дочерний узел"""
        child.set_parent(self)
        self.children.append(child)

    def get_path(self) -> List[str]:
        """Восстанавливает всю цепочку мыслей от корня до этого узла"""
        path = []
        current = self
        while current:
            path.append(current.state)
            current = current.parent
        return path[::-1]
    
    def to_dict(self) -> dict:
        """Подготовка данных узла для JSON лога"""
        return {
            "id": self.id,
            "role": self.role,
            "state": self.state,
            "score": self.score,
            "feedback": self.feedback,
            "time": round(self.time, 2),
            "parent": self.parent.id if self.parent else None
        }