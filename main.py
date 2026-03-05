import os
from core.client import LLMClient
from core.search_algorithm.bfs import BFS

def main():
    # 1. Инициализация клиента
    # Убедитесь, что в вашем .env файле прописаны AITUNNEL_API_KEY и AITUNNEL_BASE_URL
    client = LLMClient(model_name="deepseek-chat", temperature=0.7)

    # 2. Настройка BFS
    # k=3 (генерируем 3 варианта на шаг)
    # b=2 (оставляем 2 лучших для продолжения)
    # max_depth=3 (максимум 3 шага рассуждений)
    bfs_solver = BFS(client, k=3, b=2, max_depth=3)

    # 3. Формулировка задачи
    # ToT отлично работает на задачах, где нужно рассмотреть несколько вариантов (планирование, математика, креатив)
    problem = """
    У меня есть 4 числа: 4, 8, 9, 5. 
    Используя каждое число ровно один раз и базовые арифметические операции (+, -, *, /), 
    получи число 24. Покажи пошаговый процесс рассуждений.
    """

    print("=== Запуск системы 'Дерево мыслей' (BFS) ===")
    print(f"Задача: {problem.strip()}")
    
    # 4. Поиск решения
    try:
        final_answer = bfs_solver.solve(problem)
        
        print("\n" + "="*30)
        print("ИТОГОВЫЙ ОТВЕТ:")
        print(final_answer)
        print("="*30)
        
    except Exception as e:
        print(f"\nПроизошла ошибка при выполнении: {e}")

if __name__ == "__main__":
    main()