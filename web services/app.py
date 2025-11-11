# streamlit_finance.py
# Front-end (Streamlit) for the Noticias API served by app.py
# Endpoints covered:
# - GET    /noticias               (list with pagination)
# - POST   /noticias               (create)
# - GET    /noticias/{id}          (get by id)
# - PUT    /noticias/{id}          (update by id)
# - DELETE /noticias/{id}          (delete by id)

import os
import requests
import streamlit as st
import streamlit.components.v1 as components

from datetime import date, datetime
import yaml

# Calcula la ruta del archivo YAML relativo a app.py
BASE_DIR = os.path.dirname(__file__)
YAML_PATH = os.path.join(BASE_DIR, "noticias.yaml")

API_BASE = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

# ------------------------------
# Helpers
# ------------------------------
def to_yyyy_mm_dd(d):
    if isinstance(d, date):
        return d.strftime("%Y-%m-%d")
    if isinstance(d, str) and d:
        for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y-%m-%dT%H:%M:%S", "%a, %d %b %Y %H:%M:%S %Z"):
            try:
                return datetime.strptime(d, fmt).strftime("%Y-%m-%d")
            except ValueError:
                continue
    return None

def api_list_noticias(page=1, limit=5, query=None):
    try:
        params = {"page": page, "limit": limit}
        if query:
            params["query"] = query
        r = requests.get(f"{API_BASE}/noticias", params=params, timeout=10)
        try:
            return r.status_code, r.json()
        except ValueError:
            return r.status_code, {"message": "Response was not valid JSON", "raw": r.text}
    except requests.RequestException as e:
        return 0, {"message": str(e)}

def api_create_noticia(payload):
    try:
        r = requests.post(f"{API_BASE}/noticias", json=payload, timeout=10)
        return r.status_code, r.json()
    except requests.RequestException as e:
        return 0, {"message": str(e)}

def api_get_noticia(id: int):
    try:
        r = requests.get(f"{API_BASE}/noticias/{id}", timeout=10)
        try:
            body = r.json()
        except Exception:
            body = {"message": r.text}
        return r.status_code, body
    except requests.RequestException as e:
        return 0, {"message": str(e)}

def api_update_noticia(id: int, payload):
    try:
        r = requests.put(f"{API_BASE}/noticias/{id}", json=payload, timeout=10)
        return r.status_code, r.json()
    except requests.RequestException as e:
        return 0, {"message": str(e)}

def api_delete_noticia(id: int):
    try:
        r = requests.delete(f"{API_BASE}/noticias/{id}", timeout=10)
        if r.status_code == 204:
            return r.status_code, {"message": "Noticia eliminada exitosamente"}
        try:
            return r.status_code, r.json()
        except Exception:
            return r.status_code, {"message": r.text}
    except requests.RequestException as e:
        return 0, {"message": str(e)}

def render_api_response(status, body, success_codes=(200, 201, 204)):
    if status in success_codes:
        st.success(body if isinstance(body, str) else body.get("message", "OK"))
    elif status == 404:
        st.warning(body.get("message", "Noticia no encontrada"))
    elif status == 0:
        st.error(f"Error de conexión: {body.get('message')}")
    else:
        st.error(f"Error {status}: {body.get('message', body)}")

# ------------------------------
# UI
# ------------------------------
st.set_page_config(page_title="Noticias Admin", page_icon="📰", layout="wide")
st.title("📰 Noticias Admin")
st.caption(f"API base: {API_BASE}")

tabs = st.tabs(["📄 Browse", "➕ Create", "✏️ Edit / Delete", "📑 Presentation", "📖 Swagger UI"])

# ------------------------------
# Tab: Presentation
# ------------------------------
with tabs[3]:
    st.subheader("📑 API Specification (noticias.yaml)")
    yaml_file = YAML_PATH

    try:
        with open(yaml_file, "r", encoding="utf-8") as f:
            raw_content = f.read()
        try:
            yaml_content = yaml.safe_load(raw_content)
            st.json(yaml_content)
        except Exception:
            st.warning("⚠️ Could not parse YAML, showing raw content instead.")
        st.code(raw_content, language="yaml")
    except FileNotFoundError:
        st.error(f"YAML file not found: {yaml_file}")
    except Exception as e:
        st.error(f"Error loading YAML: {e}")

# ------------------------------
# Tab: Browse
# ------------------------------
with tabs[0]:
    st.subheader("📰 Últimas noticias")

    col1, col2 = st.columns([4,1])
    with col1:
        query = st.text_input("Buscar", placeholder="Ingrese palabra clave...")
    with col2:
        if st.button("🔄 Actualizar"):
            st.session_state["page"] = 1

    current_page = st.session_state.get("page", 1)
    status, body = api_list_noticias(page=current_page, limit=5, query=query)

    if status == 200 and isinstance(body, dict):
        items = body.get("items", [])
        total_items = body.get("total_items", 0)
        limit = body.get("limit", 5)
        total_pages = (total_items // limit) + (1 if total_items % limit else 0)

        if not items:
            st.info("No hay noticias disponibles.")
        else:
            for item in items:
                with st.container():
                    st.markdown(f"### {item.get('titulo', 'Sin título')}")
                    st.caption(f"Publicado: {item.get('fecha_publicacion', 'Desconocida')} | Fuente: {item.get('fuente', 'N/A')}")
                    st.write(item.get("resumen", "Sin resumen."))
                    st.divider()

            cols = st.columns(min(total_pages, 10))
            for i in range(1, total_pages + 1):
                if cols[(i-1) % len(cols)].button(str(i)):
                    st.session_state["page"] = i
                    st.experimental_rerun()
    else:
        render_api_response(status, body)

# ------------------------------
# Tab: Create
# ------------------------------
with tabs[1]:
    st.subheader("➕ Crear nueva noticia")
    with st.form("form_create"):
        col1, col2 = st.columns(2)
        with col1:
            titulo = st.text_input("Título")
            fuente = st.text_input("Fuente")
            departamento = st.text_input("Departamento")
        with col2:
            fecha = st.date_input("Fecha de publicación", value=date.today())
        resumen = st.text_area("Resumen", height=100)
        contenido = st.text_area("Contenido", height=150)
        submitted = st.form_submit_button("✅ Crear")
        if submitted:
            payload = {
                "titulo": titulo,
                "resumen": resumen,
                "contenido": contenido,
                "fecha_publicacion": to_yyyy_mm_dd(fecha),
                "fuente": fuente,
                "departamento": departamento
            }
            status, body = api_create_noticia(payload)
            render_api_response(status, body)

# ------------------------------
# Tab: Edit / Delete
# ------------------------------
with tabs[2]:
    st.subheader("✏️ Editar o eliminar noticia")
    with st.form("form_load"):
        edit_id = st.number_input("ID de la noticia", min_value=1)
        load = st.form_submit_button("📥 Cargar")
    if load:
        status, data = api_get_noticia(edit_id)
        if status == 200:
            with st.form("form_edit"):
                col1, col2 = st.columns(2)
                with col1:
                    titulo_e = st.text_input("Título", value=data.get("titulo", ""))
                    fuente_e = st.text_input("Fuente", value=data.get("fuente", ""))
                with col2:
                    fecha_e = st.date_input("Fecha de publicación", value=date.today())
                resumen_e = st.text_area("Resumen", value=data.get("resumen", ""))
                contenido_e = st.text_area("Contenido", value=data.get("contenido", ""))
                col3, col4 = st.columns(2)
                update = col3.form_submit_button("💾 Guardar cambios")
                delete = col4.form_submit_button("🗑️ Eliminar")

                if update:
                    payload = {
                        "titulo": titulo_e,
                        "resumen": resumen_e,
                        "contenido": contenido_e,
                        "fecha_publicacion": to_yyyy_mm_dd(fecha_e),
                        "fuente": fuente_e,
                    }
                    status, body = api_update_noticia(edit_id, payload)
                    render_api_response(status, body)
                if delete:
                    confirm = st.checkbox("Confirmar eliminación")
                    if confirm:
                        status, body = api_delete_noticia(edit_id)
                        render_api_response(status, body)
        else:
            render_api_response(status, data)

# ------------------------------
# Tab: Swagger UI
# ------------------------------
with tabs[4]:
    st.subheader("📖 Swagger UI")
    try:
        with open(YAML_PATH, "r", encoding="utf-8") as f:
            raw_yaml = f.read()
        swagger_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
          <title>Swagger UI</title>
          <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist/swagger-ui.css" />
          <script src="https://cdn.jsdelivr.net/npm/js-yaml@4.1.0/dist/js-yaml.min.js"></script>
        </head>
        <body>
          <div id="swagger-ui"></div>
          <script src="https://unpkg.com/swagger-ui-dist/swagger-ui-bundle.js"></script>
          <script>
            const spec = jsyaml.load(`{raw_yaml}`);
            const ui = SwaggerUIBundle({{
              spec: spec,
              dom_id: '#swagger-ui',
              deepLinking: true,
              presets: [SwaggerUIBundle.presets.apis],
              layout: "BaseLayout"
            }});
          </script>
        </body>
        </html>
        """
        components.html(swagger_html, height=900, scrolling=True)
    except Exception as e:
        st.error(f"Error loading Swagger UI: {e}")

