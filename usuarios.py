import streamlit as st
from database import ejecutar_query, obtener_datos

def mostrar_usuarios():
    st.title("👥 Gestión de Usuarios")

    tab1, tab2 = st.tabs(["📋 Ver Usuarios", "➕ Registrar Usuario"])

    # ── TAB 1: VER USUARIOS ──────────────────────
    with tab1:
        st.subheader("Usuarios Registrados")

        datos, columnas = obtener_datos("""
            SELECT 
                id_usuario,
                nombre,
                cargo,
                sede,
                email,
                fecha_registro
            FROM usuarios
            ORDER BY nombre
        """)

        if datos:
            import pandas as pd
            df = pd.DataFrame(datos, columns=columnas)
            st.dataframe(df, use_container_width=True)
            st.caption(f"Total: {len(df)} usuarios registrados")
        else:
            st.info("No hay usuarios registrados todavía.")

    # ── TAB 2: REGISTRAR USUARIO ─────────────────
    with tab2:
        st.subheader("Registrar Nuevo Usuario")

        with st.form("form_usuario"):
            col1, col2 = st.columns(2)

            with col1:
                nombre = st.text_input("Nombre completo *")
                cargo = st.text_input("Cargo")

            with col2:
                sede = st.text_input("Sede")
                email = st.text_input("Email")

            submitted = st.form_submit_button("💾 Guardar Usuario")

            if submitted:
                if not nombre:
                    st.error("El nombre es obligatorio")
                else:
                    resultado = ejecutar_query("""
                        INSERT INTO usuarios (nombre, cargo, sede, email)
                        VALUES (%s, %s, %s, %s)
                    """, (nombre, cargo, sede, email))

                    if resultado:
                        from historial import registrar_cambio
                        usuario_actual = st.session_state.get("username", "desconocido")
                        registrar_cambio("usuarios", 0, "creacion",
                            "—", f"Nuevo usuario: {nombre} ({cargo})", usuario_actual)
                        st.success(f"✅ Usuario '{nombre}' registrado correctamente")
                        st.balloons()