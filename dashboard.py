import streamlit as st
from database import obtener_datos
import plotly.graph_objects as go
import pandas as pd

def card_kpi(icono, titulo, valor, color):
    return f"""
    <div style="
        background: linear-gradient(135deg, #1A1D27 0%, #0E1117 100%);
        border: 1px solid {color};
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 20px {color}33;
    ">
        <div style="font-size: 32px; margin-bottom: 8px;">{icono}</div>
        <div style="color: {color}; font-size: 13px; font-weight: 600; 
                    text-transform: uppercase; letter-spacing: 1px;">{titulo}</div>
        <div style="color: #FFFFFF; font-size: 36px; font-weight: 800; 
                    margin-top: 6px; text-shadow: 0 0 20px {color};">{valor}</div>
    </div>
    """

def mostrar_dashboard():

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
            📊 Dashboard de Inventario TI
        </h1>
        <p style="color: #90CAF9; margin: 6px 0 0 0; font-size: 14px;">
            Panel de control — Gestión de activos tecnológicos
        </p>
    </div>
    """, unsafe_allow_html=True)

    total, _ = obtener_datos("SELECT COUNT(*) FROM activos")
    activos, _ = obtener_datos("SELECT COUNT(*) FROM activos WHERE estado = 'Activo'")
    renovar, _ = obtener_datos("SELECT COUNT(*) FROM activos WHERE estado = 'Por renovar'")
    mantenimiento, _ = obtener_datos("SELECT COUNT(*) FROM activos WHERE estado = 'En mantenimiento'")
    usuarios, _ = obtener_datos("SELECT COUNT(*) FROM usuarios")

    col1, col2, col3, col4, col5 = st.columns(5)
    cols = [col1, col2, col3, col4, col5]
    kpis = [
        ("💻", "Total activos", total[0][0], "#2E75B6"),
        ("✅", "Activos", activos[0][0], "#4CAF50"),
        ("⚠️", "Por renovar", renovar[0][0], "#FF9800"),
        ("🔧", "Mantenimiento", mantenimiento[0][0], "#F44336"),
        ("👥", "Usuarios", usuarios[0][0], "#9C27B0"),
    ]
    for col, (icono, titulo, valor, color) in zip(cols, kpis):
        with col:
            st.markdown(card_kpi(icono, titulo, valor, color), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""<div style="height:1px; background: linear-gradient(90deg, transparent, #2E75B6, transparent); margin: 10px 0 24px 0;"></div>""", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        datos_tipo, _ = obtener_datos("""
            SELECT tipo, COUNT(*) as cantidad 
            FROM activos GROUP BY tipo ORDER BY cantidad DESC
        """)
        if datos_tipo:
            df = pd.DataFrame(datos_tipo, columns=["Tipo", "Cantidad"])
            colores = ["#2E75B6", "#4CAF50", "#FF9800", "#F44336", "#9C27B0"]
            fig = go.Figure(data=[go.Bar(
                x=df["Tipo"],
                y=df["Cantidad"],
                marker=dict(
                    color=colores[:len(df)],
                    line=dict(color="#FFFFFF", width=0.5),
                ),
                text=df["Cantidad"],
                textposition="outside",
                textfont=dict(color="#FFFFFF", size=14),
            )])
            fig.update_layout(
                title=dict(text="Activos por Tipo", font=dict(size=16, color="#90CAF9")),
                paper_bgcolor="rgba(26,29,39,0.8)",
                plot_bgcolor="rgba(14,17,23,0.8)",
                font=dict(color="#FAFAFA"),
                xaxis=dict(gridcolor="#2E3347"),
                yaxis=dict(gridcolor="#2E3347"),
                bargap=0.3,
                margin=dict(t=50, b=20, l=20, r=20),
                height=320,
            )
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        datos_estado, _ = obtener_datos("""
            SELECT estado, COUNT(*) as cantidad FROM activos GROUP BY estado
        """)
        if datos_estado:
            df2 = pd.DataFrame(datos_estado, columns=["Estado", "Cantidad"])
            colores_estado = {
                "Activo": "#4CAF50",
                "Por renovar": "#FF9800",
                "En mantenimiento": "#F44336"
            }
            fig2 = go.Figure(data=[go.Pie(
                labels=df2["Estado"],
                values=df2["Cantidad"],
                hole=0.5,
                marker=dict(
                    colors=[colores_estado.get(e, "#2E75B6") for e in df2["Estado"]],
                    line=dict(color="#0E1117", width=3)
                ),
                textfont=dict(size=13, color="white"),
                pull=[0.06] * len(df2),
            )])
            fig2.update_layout(
                title=dict(text="Estado del Inventario", font=dict(size=16, color="#90CAF9")),
                paper_bgcolor="rgba(26,29,39,0.8)",
                font=dict(color="#FAFAFA"),
                legend=dict(bgcolor="rgba(26,29,39,0.8)", bordercolor="#2E75B6", borderwidth=1),
                margin=dict(t=50, b=20, l=20, r=20),
                height=320,
                annotations=[dict(
                    text=f"<b>{sum(df2['Cantidad'])}</b><br>total",
                    x=0.5, y=0.5,
                    font=dict(size=18, color="white"),
                    showarrow=False
                )]
            )
            st.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        datos_sede, _ = obtener_datos("""
            SELECT sede, COUNT(*) as cantidad 
            FROM activos WHERE sede IS NOT NULL AND sede != ''
            GROUP BY sede ORDER BY cantidad DESC
        """)
        if datos_sede:
            df3 = pd.DataFrame(datos_sede, columns=["Sede", "Cantidad"])
            fig3 = go.Figure(data=[go.Bar(
                x=df3["Cantidad"],
                y=df3["Sede"],
                orientation='h',
                marker=dict(
                    color=df3["Cantidad"],
                    colorscale=[[0, "#0E4D8A"], [1, "#00E5FF"]],
                    line=dict(color="#00E5FF", width=0.5),
                ),
                text=df3["Cantidad"],
                textposition="outside",
                textfont=dict(color="#FFFFFF", size=13),
            )])
            fig3.update_layout(
                title=dict(text="Activos por Sede", font=dict(size=16, color="#90CAF9")),
                paper_bgcolor="rgba(26,29,39,0.8)",
                plot_bgcolor="rgba(14,17,23,0.8)",
                font=dict(color="#FAFAFA"),
                xaxis=dict(gridcolor="#2E3347"),
                yaxis=dict(gridcolor="#2E3347"),
                margin=dict(t=50, b=20, l=20, r=20),
                height=320,
            )
            st.plotly_chart(fig3, use_container_width=True)

    with col4:
        datos_marca, _ = obtener_datos("""
            SELECT marca, COUNT(*) as cantidad 
            FROM activos WHERE marca IS NOT NULL AND marca != ''
            GROUP BY marca ORDER BY cantidad DESC
        """)
        if datos_marca:
            df4 = pd.DataFrame(datos_marca, columns=["Marca", "Cantidad"])
            fig4 = go.Figure(data=[go.Bar(
                x=df4["Marca"],
                y=df4["Cantidad"],
                marker=dict(
                    color=df4["Cantidad"],
                    colorscale=[[0, "#4A0080"], [1, "#E040FB"]],
                    line=dict(color="#E040FB", width=0.5),
                ),
                text=df4["Cantidad"],
                textposition="outside",
                textfont=dict(color="#FFFFFF", size=13),
            )])
            fig4.update_layout(
                title=dict(text="Activos por Marca", font=dict(size=16, color="#90CAF9")),
                paper_bgcolor="rgba(26,29,39,0.8)",
                plot_bgcolor="rgba(14,17,23,0.8)",
                font=dict(color="#FAFAFA"),
                xaxis=dict(gridcolor="#2E3347"),
                yaxis=dict(gridcolor="#2E3347"),
                margin=dict(t=50, b=20, l=20, r=20),
                height=320,
            )
            st.plotly_chart(fig4, use_container_width=True)

    st.markdown("""<div style="height:1px; background: linear-gradient(90deg, transparent, #2E75B6, transparent); margin: 10px 0 24px 0;"></div>""", unsafe_allow_html=True)

    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #3A2000 0%, #1A1D27 100%);
        border: 1px solid #FF9800;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 16px;
        box-shadow: 0 4px 20px #FF980033;
    ">
        <h3 style="color: #FF9800; margin: 0; font-size: 18px;">
            ⚠️ Activos con garantía próxima a vencer
        </h3>
    </div>
    """, unsafe_allow_html=True)

    alertas, _ = obtener_datos("""
        SELECT a.nombre, a.tipo, a.marca, a.serial,
               a.fecha_garantia, a.sede, u.nombre as responsable,
               (a.fecha_garantia - CURRENT_DATE) as dias_restantes
        FROM activos a
        LEFT JOIN usuarios u ON a.id_usuario = u.id_usuario
        WHERE a.fecha_garantia IS NOT NULL
          AND a.fecha_garantia <= CURRENT_DATE + INTERVAL '90 days'
          AND a.fecha_garantia >= CURRENT_DATE
        ORDER BY a.fecha_garantia ASC
    """)

    if alertas:
        df_alertas = pd.DataFrame(alertas, columns=[
            "Nombre", "Tipo", "Marca", "Serial",
            "Vence garantía", "Sede", "Responsable", "Días restantes"])
        st.dataframe(df_alertas, use_container_width=True)
        st.markdown(f"""
        <div style="color: #FF9800; font-size: 13px; margin-top: 8px;">
            ⚠️ {len(df_alertas)} activos vencen garantía en los próximos 90 días
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
            box-shadow: 0 4px 20px #4CAF5033;
        ">
            ✅ No hay activos con garantía próxima a vencer
        </div>
        """, unsafe_allow_html=True)