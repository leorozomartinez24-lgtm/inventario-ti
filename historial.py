import streamlit as st
from database import ejecutar_query, obtener_datos
import pandas as pd

def registrar_cambio(tabla, id_registro, campo, valor_anterior, valor_nuevo, usuario):
    ejecutar_query("""
        INSERT INTO historial_cambios 
        (tabla_afectada, id_registro, campo_modificado, 
         valor_anterior, valor_nuevo, usuario_sistema)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (tabla, id_registro, campo, str(valor_anterior), str(valor_nuevo), usuario))

def mostrar_historial():
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #1F4E79 0%, #0E1117 100%);
        border-radius: 16px;
        padding: 24px 32px;
        margin-bottom: 24px;
        border-left: 4px solid #2E75B6;
        box-shadow: 0 4px 30px #2E75B633;
    ">
        <h1 style="color: #FFFFFF; margin: 0; font-size: 28px; font-weight: 800;">
            🕒 Historial de Cambios
        </h1>
        <p style="color: #90CAF9; margin: 6px 0 0 0; font-size: 14px;">
            Registro completo de auditoría del sistema
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        filtro_tabla = st.selectbox("Filtrar por módulo",
            ["Todos", "activos", "usuarios"])
    with col2:
        filtro_campo = st.selectbox("Filtrar por acción",
            ["Todas", "creacion", "nombre", "tipo", "marca", "modelo",
             "serial", "sede", "estado", "responsable", "fecha_garantia"])
    with col3:
        filtro_usuario = st.text_input("Filtrar por usuario")

    query = """
        SELECT 
            id_historial,
            tabla_afectada       AS "Módulo",
            id_registro          AS "ID Registro",
            campo_modificado     AS "Acción / Campo",
            valor_anterior       AS "Valor anterior",
            valor_nuevo          AS "Valor nuevo",
            usuario_sistema      AS "Usuario",
            TO_CHAR(fecha_cambio, 'DD/MM/YYYY HH24:MI:SS') AS "Fecha"
        FROM historial_cambios
        WHERE 1=1
    """
    params = []

    if filtro_tabla != "Todos":
        query += " AND tabla_afectada = %s"
        params.append(filtro_tabla)
    if filtro_campo != "Todas":
        query += " AND campo_modificado = %s"
        params.append(filtro_campo)
    if filtro_usuario:
        query += " AND usuario_sistema ILIKE %s"
        params.append(f"%{filtro_usuario}%")

    query += " ORDER BY fecha_cambio DESC"

    datos, columnas = obtener_datos(query, params if params else None)

    if datos:
        df = pd.DataFrame(datos, columns=columnas)
        st.dataframe(df, use_container_width=True, height=500)
        st.markdown(f"""
        <div style="color: #90CAF9; font-size: 13px; margin-top: 8px;">
            📋 {len(df)} registros encontrados
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #1B3A2D 0%, #1A1D27 100%);
            border: 1px solid #4CAF50;
            border-radius: 12px;
            padding: 16px 20px;
            color: #4CAF50;
        ">
            ✅ No hay cambios registrados todavía.
        </div>
        """, unsafe_allow_html=True)