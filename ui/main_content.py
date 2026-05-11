import streamlit as st
import os
import json
from core.client import LLMClient
from core.search_algorithm.bfs import BFS
from core.search_algorithm.dfs import DFS


def render_input_form():
    '''Ввод параметров и запроса'''

    st.subheader("Параметры обхода")
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

    with col1:
        search_alg = st.radio("Тип обхода", ["BFS", "DFS"], horizontal=True, key="search_alg") # Панель для выбора проходов 
    
    # Параметры для проходов
    with col2:
        count_thoughts = st.number_input(
            "Кол-во мыслей за шаг (макс. 10)", 
            min_value=2, 
            max_value=10, 
            value=3, 
            key="cnt_th")  # Кол-во мысслей на 1 уровне
    
    with col3:
        if search_alg == "BFS":
            max_breadth = count_thoughts - 1   # минимум 1, т.к. count_thoughts ≥ 2
           
            if "brd_val" in st.session_state and st.session_state["brd_val"] > max_breadth:
                st.session_state["brd_val"] = max_breadth

            breadth_val = st.number_input(
                f"Breadth limit (макс. {max_breadth})",
                min_value=1,
                max_value=max_breadth,
                value=st.session_state.get("brd_val", 2),
                key="brd_val"
            )
        else:
            breadth_val = st.slider(
                "Порог оценки (макс. 0.80)",
                0.30, 0.80, 0.5, step=0.05,
                key="thr_val"
            )
    
    with col4:
        max_depth = st.number_input(
            "Глубина (макс. 10)", 
            min_value=1, 
            max_value=10, 
            value=3, 
            key="max_d") # Глубина дерева

    
    query = st.text_area("Вопрос", height=100, placeholder="Введите свой запрос", key="query_input") # Поле для ввода запроса

    if st.button("Отправить", type="primary", use_container_width=True): # Кнопка "Отправить"
        if query.strip():
            
            with st.spinner("Идёт обход дерева мыслей..."):
                
                client = LLMClient(model_name="deepseek-chat", temperature=0.7) # Инициализация клиента
                
                # Выбор обхода
                if search_alg == "BFS":
                    algorithm = BFS(client,
                                    count_thoughts=count_thoughts,
                                    breadth_limit=breadth_val,
                                    max_depth=max_depth)
                else:
                    algorithm = DFS(client,
                                    count_thoughts=count_thoughts,
                                    threshold=breadth_val,
                                    max_depth=max_depth)

                answer, json_filename, png_filename = algorithm.solve(query) # решение

                # Читение JSON
                try:
                    with open(json_filename, "r", encoding="utf-8") as f:
                        log_data = json.load(f)
                except Exception as e:
                    st.error(f"Ошибка чтения JSON: {e}")
                    log_data = {}

                # Если PNG не существует – выставим None
                png_path = png_filename if os.path.exists(png_filename) else None

                # Определяем id из имени файла 
                base = os.path.splitext(os.path.basename(json_filename))[0]
                item_id = base  
             
                # Создаём item
                history_item = {
                    "id": item_id,
                    "query": query,
                    "response": answer,
                    "parameters": {
                        "search_alg": search_alg,
                        "count_thoughts": count_thoughts,
                        "breadth_limit_or_threshold": breadth_val,
                        "max_depth": max_depth
                    },
                    "log_data": log_data,
                    "png_filename": png_path,   
                }

                # Вставляем в начало истории
                st.session_state.history.insert(0, history_item)
                st.session_state.current_result = history_item
                st.session_state.show_viz = False
                st.rerun()
        else:
            st.warning("Пожалуйста, введите запрос.")


def render_result():
    '''Визуализация результатов'''
    
    curr = st.session_state.current_result # Получаем текущий сохранённый результат из session_state
    left_col, right_col = st.columns([3, 1]) # Создаём две колонки: основная (3/4 ширины) и боковая с параметрами (1/4)

    # Левая колонка: вопрос, ответ, кнопки действий и визуализация
    with left_col:
        st.markdown("### Ваш запрос и ответ")
        st.markdown(f"**Запрос:** {curr['query']}")
        st.markdown(f"**Ответ:** {curr['response']}")

        # Кнопки «Визуализировать» и «Новый запрос» в ряд
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("Визуализировать", use_container_width=True):
                
                # Устанавливаем флаг показа визуализации и перезагружаем страницу
                st.session_state.show_viz = True
                st.rerun()
        with col_btn2:
            if st.button("Новый запрос", use_container_width=True):
                
                # Сбрасываем текущий результат и флаг визуализации
                st.session_state.current_result = None
                st.session_state.show_viz = False
                st.rerun()

        # Если флаг show_viz = True, показываем блок с изображением
        if st.session_state.show_viz:
            st.markdown("### Визуализация дерева мыслей")
            
            png_path = curr.get("png_filename")

            if png_path and os.path.exists(png_path):
                st.image(png_path, caption="Структура графа ToT", width='stretch')
            else:
                st.warning("Нет данных для визуализации. Файл графа не найден.")
                
                
    # Правая колонка: информация о параметрах обхода и метрики
    with right_col:
        st.subheader("Параметры текущего обхода")
        params = curr["parameters"]
        
        # Выводим основные параметры вызова
        st.markdown(f"""
        - **Тип обхода:** `{params['search_alg']}`  
        - **Мыслей за шаг:** `{params['count_thoughts']}`  
        - **Предел ширины / Порог:** `{params['breadth_limit_or_threshold']}`  
        - **Макс. глубина:** `{params['max_depth']}`  
        """)

        # Извлекаем общую информацию
        try:
            gen_info = curr["log_data"]["general_information"][0]
            st.metric("Всего мыслей", gen_info["count_thoughts"])
            st.metric("Всего токенов", gen_info["total_tokens"])
            st.metric("Время выполнения (с)", gen_info["total_time"])
        except (KeyError, IndexError, TypeError):
            st.warning("Нет данных общей информации.")