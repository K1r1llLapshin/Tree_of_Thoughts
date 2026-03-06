import threading
import time
from core.client import LLMClient
from core.search_algorithm.bfs import BFS
from core.search_algorithm.dfs import DFS

def _run_timer(stop_event: threading.Event):
    start = time.time()
    while not stop_event.is_set():
        elapsed = time.time() - start
        # \r возвращает каретку в начало строки – будем перезаписывать
        print(f"Время: {elapsed:.1f} с", end="\r")
        time.sleep(0.5)
    # напоследок напечатать итог
    elapsed = time.time() - start
    print(f"\nИтого прошло {elapsed:.2f} с")
    
def main():
    # 1. Инициализация клиента
    client = LLMClient(model_name="deepseek-chat", temperature=0.7)

    # 2. Настройка  
    dfs_solver = DFS(client, count_thoughts=3, max_depth=3, threshold=6.0) 
    
    # 3. Формулировка задачи
    problem = """
    У нас есть два пустых кувшина: один вмещает ровно 5 литров, а другой — ровно 3 литра. У нас также есть неограниченный источник воды. 
    Как отмерить ровно 4 литра воды? Опиши действия по шагам.
    """

    print("=== Запуск системы 'Дерево мыслей' (DFS) ===")
    print(f"Задача: {problem.strip()}")
    
    stop_event = threading.Event()
    timer_thread = threading.Thread(target=_run_timer, args=(stop_event,))
    timer_thread.start()

    # 4. Поиск решения
    try:
        final_answer = dfs_solver.solve(problem)
        
        print("\n" + "="*30)
        print("ИТОГОВЫЙ ОТВЕТ:")
        print(final_answer)
        print("="*30)
        
    except Exception as e:
        print(f"\nПроизошла ошибка при выполнении: {e}")
        
    finally:
        stop_event.set()
        timer_thread.join()
if __name__ == "__main__":
    main()