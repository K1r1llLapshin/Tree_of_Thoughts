import os
import json
from typing import List, Dict, Any

# Папка с JSON-файлами результатов
JSON_RESULTS_DIR = "D:\Tree_of_Thoughts\logs\json"

# Папка с PNG-изображениями (может быть подпапкой results/png)
PNG_RESULTS_DIR = "D:\Tree_of_Thoughts\logs\img"

def _ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def load_history() -> List[Dict[str, Any]]:
    """Загружает историю из JSON-файлов. PNG ищется в отдельной папке."""
    
    _ensure_dir(JSON_RESULTS_DIR)
    _ensure_dir(PNG_RESULTS_DIR)
    items = []

    # Получаем все JSON-файлы и сортируем по времени изменения 
    json_files = [f for f in os.listdir(JSON_RESULTS_DIR) if f.endswith(".json")]
    json_files.sort(key=lambda f: os.path.getmtime(os.path.join(JSON_RESULTS_DIR, f)), reverse=True)

    for filename in json_files:
        json_path = os.path.join(JSON_RESULTS_DIR, filename)
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                log_data = json.load(f)
        except Exception:
            continue

        # Идентификатор = имя файла без расширения
        item_id = filename[12:-5] 
        
        # PNG
        png_path = os.path.join(PNG_RESULTS_DIR, f"thoughts_tree_{item_id}.png")
        if not os.path.exists(png_path):
            png_path = None

        # Извлекаем вопрос и ответ из brief_summary
        try:
            summary = log_data["brief_summary"][0]
            query = summary["question"]
            answer = summary["answer"]
        except (KeyError, IndexError):
            query = ""
            answer = ""

        # Параметры обхода
        try:
            params = log_data["parameters"][0]
            search_alg = params.get("name_search", "")
            count_thoughts = params.get("count_thoughts", 0)
            breadth = params.get("breadth_limit") or params.get("threshold") or params.get("breadth_limit_or_threshold", 0)
            max_depth = params.get("max_depth", 0)
        except (KeyError, IndexError):
            search_alg = ""
            count_thoughts = 0
            breadth = 0
            max_depth = 0

        items.append({
            "id": item_id,
            "query": query,
            "response": answer,
            "parameters": {
                "search_alg": search_alg,
                "count_thoughts": count_thoughts,
                "breadth_limit_or_threshold": breadth,
                "max_depth": max_depth
            },
            "log_data": log_data,
            "png_filename": png_path,   
        })

    return items

def delete_history_item(item_id: str):
    """Удаляет JSON и PNG для указанного id."""
    
    json_path = os.path.join(JSON_RESULTS_DIR, f"{item_id}.json")
    png_path = os.path.join(PNG_RESULTS_DIR, f"{item_id}.png")
    for p in (json_path, png_path):
        if os.path.exists(p):
            os.remove(p)

def clear_all_history():
    """Удаляет всё содержимое из JSON- и PNG-папок."""
    
    for directory in (JSON_RESULTS_DIR, PNG_RESULTS_DIR):
        if os.path.exists(directory):
            for fname in os.listdir(directory):
                file_path = os.path.join(directory, fname)
                if os.path.isfile(file_path):
                    os.remove(file_path)