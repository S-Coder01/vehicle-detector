import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
import requests
import json
from frontend.api_client import APIClient
from frontend.utils import draw_bboxes_on_image, CLASS_NAMES_RU, CLASS_COLORS

def show_history_page(api_client: APIClient):
    st.title("История запросов")

    if st.button("🔄 Обновить историю"):
        st.session_state["history_updated"] = True
        st.rerun()

    try:
        entries = api_client.get_history()
        if not entries:
            st.info("История пуста.")
            return

        if "view_entry_id" in st.session_state and st.session_state["view_entry_id"] is not None:
            entry_id = st.session_state["view_entry_id"]
            entry = next((e for e in entries if e["id"] == entry_id), None)
            if entry:
                st.subheader("Детали выбранной записи")
                # Метаданные записи: модель и дата
                st.write(f"**Модель:** {entry['model_used']}")
                st.write(f"**Дата:** {entry['created_at'][:19].replace('T', ' ')}")
                st.markdown("---")

                try:
                    user_id = st.session_state.get("user_id")
                    if user_id:
                        filename = Path(entry['image_path']).name
                        image_bytes = api_client.get_uploaded_image(user_id, filename)

                        results = json.loads(entry['results_json'])
                        detections = results.get("detections", [])

                        # Настройки отображения
                        st.subheader("Настройки отображения")
                        col1, col2 = st.columns(2)
                        with col1:
                            show_labels = st.checkbox("Показывать названия классов", value=True, key="hist_show_labels")
                            show_class_ids = st.checkbox("Показывать номера классов", value=False, key="hist_show_ids")
                        with col2:
                            class_filter = st.multiselect(
                                "Фильтр классов (оставьте пустым для всех)",
                                options=list(CLASS_NAMES_RU.keys()),
                                format_func=lambda x: f"{x}: {CLASS_NAMES_RU[x]}",
                                key="hist_class_filter"
                            )

                        if st.checkbox("Показать легенду", value=True, key="hist_show_legend"):
                            st.markdown("**Легенда классов:**")
                            cols = st.columns(len(CLASS_NAMES_RU))
                            for i, (cls_id, name) in enumerate(CLASS_NAMES_RU.items()):
                                color = CLASS_COLORS[cls_id]
                                with cols[i]:
                                    st.markdown(
                                        f"<span style='display:inline-block; width:12px; height:12px; background-color:rgb{color}; border-radius:2px;'></span> "
                                        f"{cls_id}: {name}",
                                        unsafe_allow_html=True
                                    )

                        show_original = st.checkbox("Показать исходное изображение (без боксов)", value=False, key="hist_show_original")
                        if show_original:
                            st.image(image_bytes, caption="Исходное изображение", width='stretch')
                        else:
                            if detections:
                                filter_classes = class_filter if class_filter else None
                                result_image_bytes = draw_bboxes_on_image(
                                    image_bytes,
                                    detections,
                                    show_labels=show_labels,
                                    show_class_ids=show_class_ids,
                                    filter_classes=filter_classes
                                )
                                st.image(result_image_bytes, caption="Результат детекции", width='stretch')
                            else:
                                st.info("Объекты не обнаружены.")
                                st.image(image_bytes, caption="Загруженное изображение", width='stretch')
                    else:
                        st.warning("ID пользователя не найден. Загрузить изображение нельзя.")
                except Exception as e:
                    st.error(f"Не удалось загрузить изображение: {e}")

                if st.button("Закрыть просмотр"):
                    st.session_state["view_entry_id"] = None
                    st.rerun()
                st.markdown("---")

        # Таблица записей
        for entry in entries:
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 1, 1])
                col1.write(f"**{entry['image_path']}**")
                col2.write(f"Модель: {entry['model_used']}")
                col3.write(f"Дата: {entry['created_at'][:19].replace('T', ' ')}")
                if col4.button("🗑️ Удалить", key=f"del_{entry['id']}"):
                    try:
                        api_client.delete_history_entry(entry['id'])
                        st.success("Запись удалена")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Ошибка: {str(e)}")
                if col5.button("👁️ Просмотр", key=f"view_{entry['id']}"):
                    st.session_state["view_entry_id"] = entry['id']
                    st.rerun()

        # Очистка всей истории
        confirm = st.checkbox("Подтвердите удаление всей истории", key="clear_confirm")
        if st.button("Очистить всю историю", type="primary"):
            if confirm:
                try:
                    api_client.clear_history()
                    st.success("История очищена")
                    st.rerun()
                except Exception as e:
                    st.error(f"Ошибка: {str(e)}")
            else:
                st.warning("Поставьте галочку для подтверждения.")

    except requests.HTTPError as e:
        st.error(f"Ошибка загрузки истории: {e.response.text}")
    except Exception as e:
        st.error(f"Ошибка: {str(e)}")