import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# ── Configuración de la página ──────────────────
st.set_page_config(
    page_title="Inventario TI",
    page_icon="💻",
    layout="wide"
)

# ── Cargar estilos CSS ──────────────────────────
with open("styles.css", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ── Cargar usuarios desde config.yaml ───────────
with open("config.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)

# ── Crear el autenticador ────────────────────────
authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"],
)

# ── Pantalla de login ────────────────────────────
if st.session_state.get("authentication_status") != True:
    st.markdown("""
    <div style="
        display: flex;
        justify-content: center;
        margin-top: 40px;
        margin-bottom: 10px;
    ">
        <div style="
            background: linear-gradient(135deg, #1A1D27 0%, #0E1117 100%);
            border: 1px solid #2E75B6;
            border-radius: 20px;
            padding: 40px 50px;
            width: 440px;
            box-shadow: 0 8px 40px #2E75B633;
            text-align: center;
        ">
            <div style="font-size: 54px; margin-bottom: 10px;">💻</div>
            <h1 style="
                color: #FFFFFF;
                font-size: 24px;
                font-weight: 800;
                margin-bottom: 4px;
            ">Inventario TI</h1>
            <p style="
                color: #90CAF9;
                font-size: 13px;
                margin-bottom: 20px;
            ">Sistema de gestión de activos tecnológicos</p>
            <div style="
                height: 1px;
                background: linear-gradient(90deg, transparent, #2E75B6, transparent);
                margin-bottom: 20px;
            "></div>
            <p style="color: #90CAF9; font-size: 12px; margin: 0;">
                🔐 Ingresa tus credenciales para continuar
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Mostrar el formulario de login ───────────────
try:
    authenticator.login()
except Exception as e:
    st.error(f"Error: {e}")

# ── Lógica según el resultado ────────────────────
if st.session_state.get("authentication_status") == False:
    st.error("Usuario o contraseña incorrectos")

elif st.session_state.get("authentication_status") == None:
    st.warning("Por favor ingresa tu usuario y contraseña")

elif st.session_state.get("authentication_status") == True:

    username = st.session_state.get("username")
    name = st.session_state.get("name")
    role = config["credentials"]["usernames"][username]["role"]

    # ── Sidebar ──────────────────────────────────
    st.sidebar.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #1F4E79 0%, #1A1D27 100%);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 16px;
        border: 1px solid #2E75B6;
        text-align: center;
    ">
        <div style="font-size: 32px;">👤</div>
        <div style="color: #FFFFFF; font-weight: 700; font-size: 15px; margin-top: 6px;">{name}</div>
        <div style="
            background: #2E75B6;
            color: white;
            font-size: 11px;
            padding: 3px 10px;
            border-radius: 20px;
            display: inline-block;
            margin-top: 6px;
            font-weight: 600;
        ">{role.upper()}</div>
    </div>
    """, unsafe_allow_html=True)

    authenticator.logout("🚪 Cerrar sesión", "sidebar")
    st.sidebar.divider()
    st.sidebar.markdown("<p style='color:#90CAF9; font-size:12px; margin-bottom:8px;'>NAVEGACIÓN</p>", unsafe_allow_html=True)

    # ── Menú según el rol ────────────────────────
    if role == "admin":
        menu = st.sidebar.selectbox("", [
            "📊 Dashboard",
            "💻 Inventario",
            "👥 Usuarios",
            "📄 Actas de entrega",
            "🕒 Historial de cambios",
        ])
    else:
        menu = st.sidebar.selectbox("", [
            "📊 Dashboard",
            "💻 Inventario",
        ])

    st.sidebar.markdown("""
    <div style="
        position: fixed;
        bottom: 20px;
        font-size: 11px;
        color: #2E75B6;
        text-align: center;
    ">
        Inventario TI v1.0 © 2025
    </div>
    """, unsafe_allow_html=True)

    # ── Contenido según módulo ───────────────────
    if menu == "📊 Dashboard":
        from dashboard import mostrar_dashboard
        mostrar_dashboard()

    elif menu == "💻 Inventario":
        from inventario import mostrar_inventario
        mostrar_inventario()

    elif menu == "👥 Usuarios":
        from usuarios import mostrar_usuarios
        mostrar_usuarios()

    elif menu == "📄 Actas de entrega":
        from actas import mostrar_actas
        mostrar_actas()

    elif menu == "🕒 Historial de cambios":
        from historial import mostrar_historial
        mostrar_historial()
