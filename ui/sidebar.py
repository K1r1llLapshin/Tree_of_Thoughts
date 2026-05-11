import streamlit as st
from history_storage import delete_history_item, clear_all_history

def render_sidebar():
    """Отображение боковой панели с историей запросов."""
    
    with st.sidebar:
        st.header("История запросов")

        # Если история пуста – выводим информационное сообщение
        if not st.session_state.history:
            st.info("Пока ничего нет")
        else:
            
            # Перебираем все элементы истории
            for item in st.session_state.history:
                col1, col2 = st.columns([4, 1])  # 4/5 под кнопку просмотра, 1/5 под удаление
                with col1:
                    # Кнопка для загрузки этого результата как текущего
                    if st.button(f"{item['query'][:20]}...", key=f"hist_{item['id']}"):
                        st.session_state.current_result = item
                        st.session_state.show_viz = False
                        st.rerun()
                with col2:
                    
                    # Кнопка удаления конкретного запроса
                    if st.button("🗑️", key=f"del_{item['id']}"):
                        
                        # Удаляем файлы JSON и PNG 
                        delete_history_item(item["id"])
                        
                        # Убираем запись из списка в session_state
                        st.session_state.history = [
                            h for h in st.session_state.history if h["id"] != item["id"]
                        ]
                        
                        # Если удаляем текущий отображаемый результат, сбрасываем его
                        if st.session_state.current_result and st.session_state.current_result["id"] == item["id"]:
                            st.session_state.current_result = None
                            st.session_state.show_viz = False
                        st.rerun()

            # Кнопка полной очистки истории
            if st.button("Очистить всю историю"):
                
                # Удаляем все файлы из папок результатов
                clear_all_history()
                
                # Очищаем session_state
                st.session_state.history = []
                st.session_state.current_result = None
                st.session_state.show_viz = False
                st.rerun()