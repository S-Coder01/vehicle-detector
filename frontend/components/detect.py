import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
import requests
from frontend.api_client import APIClient
from frontend.utils import draw_bboxes_on_image, CLASS_NAMES_RU, CLASS_COLORS

def show_detect_page(api_client: APIClient):
    st.title("Детекция транспортных средств")

    if "detect_result" not in st.session_state:
        st.session_state["detect_result"] = None
    if "uploaded_image_bytes" not in st.session_state:
        st.session_state["uploaded_image_bytes"] = None

    model_option = st.radio(
        "Выберите модель:",
        ["yolo26n_fast (быстрая)", "yolo26l_accurate (точная)"],
        index=0
    )
    model_name = model_option.split()[0]

    conf_threshold = st.slider("Порог уверенности", 0.0, 1.0, 0.25, 0.05)

    uploaded_file = st.file_uploader("Загрузите изображение", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        image_bytes = uploaded_file.read()
        st.session_state["uploaded_image_bytes"] = image_bytes
        st.image(image_bytes, caption="Загруженное изображение", width='stretch')

        if st.button("Выполнить детекцию"):
            with st.spinner("Детекция..."):
                try:
                    result = api_client.detect(image_bytes, model_name, conf_threshold)
                    st.session_state["detect_result"] = {
                        "detections": result["detections"],
                        "image_width": result["image_width"],
                        "image_height": result["image_height"],
                        "model_used": result["model_used"],
                        "conf_threshold": conf_threshold
                    }
                    st.success(f"Найдено объектов: {len(result['detections'])}")
                except requests.HTTPError as e:
                    st.error(f"Ошибка API: {e.response.text}")
                except Exception as e:
                    st.error(f"Ошибка: {str(e)}")

        if st.session_state["detect_result"] is not None:
            result_data = st.session_state["detect_result"]
            detections = result_data["detections"]

            st.subheader("Настройки отображения")
            col1, col2 = st.columns(2)
            with col1:
                show_labels = st.checkbox("Показывать названия классов", value=True)
                show_class_ids = st.checkbox("Показывать номера классов", value=False)
            with col2:
                class_filter = st.multiselect(
                    "Фильтр классов (оставьте пустым для всех)",
                    options=list(CLASS_NAMES_RU.keys()),
                    format_func=lambda x: f"{x}: {CLASS_NAMES_RU[x]}"
                )

            if st.checkbox("Показать легенду", value=True):
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

            if detections:
                filter_classes = class_filter if class_filter else None
                orig_bytes = st.session_state["uploaded_image_bytes"]
                if orig_bytes:
                    result_image_bytes = draw_bboxes_on_image(
                        orig_bytes,
                        detections,
                        show_labels=show_labels,
                        show_class_ids=show_class_ids,
                        filter_classes=filter_classes
                    )
                    st.image(result_image_bytes, caption="Результат детекции", width='stretch')
                else:
                    st.warning("Изображение не найдено в сессии. Загрузите заново.")
            else:
                st.info("Объекты не обнаружены.")
    else:
        st.session_state["detect_result"] = None
        st.session_state["uploaded_image_bytes"] = None