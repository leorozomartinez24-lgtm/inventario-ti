import streamlit as st
from database import ejecutar_query, obtener_datos
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
import io
from datetime import datetime

def generar_pdf_acta(activo, usuario, observaciones):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                           rightMargin=2*cm, leftMargin=2*cm,
                           topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    elementos = []

    titulo_style = ParagraphStyle('titulo', parent=styles['Title'],
                                  fontSize=16, spaceAfter=6,
                                  textColor=colors.HexColor('#1F4E79'))
    elementos.append(Paragraph("ACTA DE ENTREGA DE ACTIVO TECNOLÓGICO", titulo_style))
    elementos.append(Paragraph("Corporación Unificada Nacional de Educación Superior — CUN",
                               styles['Normal']))
    elementos.append(Spacer(1, 0.5*cm))

    fecha_style = ParagraphStyle('fecha', parent=styles['Normal'],
                                  fontSize=10, textColor=colors.grey)
    elementos.append(Paragraph(
        f"Fecha de entrega: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        fecha_style))
    elementos.append(Spacer(1, 0.8*cm))

    elementos.append(Paragraph("INFORMACIÓN DEL ACTIVO", styles['Heading2']))
    elementos.append(Spacer(1, 0.3*cm))

    datos_activo = [
        ["Campo", "Valor"],
        ["Nombre", activo[1]],
        ["Tipo", activo[2] or ""],
        ["Marca", activo[3] or ""],
        ["Modelo", activo[4] or ""],
        ["Serial", activo[5] or ""],
        ["Sede", activo[8] or ""],
        ["Estado", activo[7] or ""],
        ["Vencimiento garantía", str(activo[6]) if activo[6] else "No registrado"],
    ]

    tabla_activo = Table(datos_activo, colWidths=[5*cm, 12*cm])
    tabla_activo.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1F4E79')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1),
         [colors.HexColor('#EBF3FB'), colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    elementos.append(tabla_activo)
    elementos.append(Spacer(1, 0.8*cm))

    elementos.append(Paragraph("INFORMACIÓN DEL RESPONSABLE", styles['Heading2']))
    elementos.append(Spacer(1, 0.3*cm))

    datos_usuario = [
        ["Campo", "Valor"],
        ["Nombre completo", usuario[1]],
        ["Cargo", usuario[2] or ""],
        ["Sede", usuario[3] or ""],
        ["Email", usuario[4] or ""],
    ]

    tabla_usuario = Table(datos_usuario, colWidths=[5*cm, 12*cm])
    tabla_usuario.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1F4E79')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1),
         [colors.HexColor('#EBF3FB'), colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    elementos.append(tabla_usuario)
    elementos.append(Spacer(1, 0.8*cm))

    if observaciones:
        elementos.append(Paragraph("OBSERVACIONES", styles['Heading2']))
        elementos.append(Spacer(1, 0.3*cm))
        elementos.append(Paragraph(observaciones, styles['Normal']))
        elementos.append(Spacer(1, 0.8*cm))

    elementos.append(Spacer(1, 1.5*cm))
    elementos.append(Paragraph("FIRMAS", styles['Heading2']))
    elementos.append(Spacer(1, 0.5*cm))

    firmas = [
        ["_______________________", "    ", "_______________________"],
        ["Entregado por", "    ", "Recibido por"],
        ["Área de TI", "    ", usuario[1]],
    ]

    tabla_firmas = Table(firmas, colWidths=[7*cm, 3*cm, 7*cm])
    tabla_firmas.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elementos.append(tabla_firmas)

    doc.build(elementos)
    buffer.seek(0)
    return buffer

def mostrar_actas():
    st.title("📄 Actas de Entrega")

    tab1, tab2, tab3 = st.tabs([
        "➕ Generar Acta",
        "📎 Subir Acta Firmada",
        "🔍 Buscar por Usuario"
    ])

    # ── TAB 1: GENERAR ACTA ──────────────────────
    with tab1:
        st.subheader("Generar Nueva Acta de Entrega")

        col1, col2 = st.columns(2)
        with col1:
            id_activo = st.number_input("ID del activo", min_value=1, step=1)
            activo, _ = obtener_datos("""
                SELECT id_activo, nombre, tipo, marca, modelo, serial,
                       fecha_garantia, estado, sede, id_usuario
                FROM activos WHERE id_activo = %s
            """, (id_activo,))
            if activo:
                a = activo[0]
                st.success(f"✅ Activo: {a[1]}")
                st.write(f"**Tipo:** {a[2]} | **Marca:** {a[3]} | **Serial:** {a[5]}")
            else:
                st.warning("Escribe un ID para buscar el activo")

        with col2:
            usuarios, _ = obtener_datos(
                "SELECT id_usuario, nombre, cargo, sede, email FROM usuarios ORDER BY nombre")
            if usuarios:
                opciones = [f"{u[0]} - {u[1]}" for u in usuarios]
                seleccion = st.selectbox("Responsable que recibe", opciones)
                id_usuario_sel = int(seleccion.split(" - ")[0])
                usuario_sel = [u for u in usuarios if u[0] == id_usuario_sel][0]
            else:
                st.warning("No hay usuarios registrados")
                usuario_sel = None

        observaciones = st.text_area("Observaciones (opcional)",
                                     placeholder="Estado del equipo, accesorios incluidos, etc.")

        if activo and usuario_sel:
                            if st.button("📄 Generar Acta PDF", type="primary"):
                    ejecutar_query("""
                        INSERT INTO actas_entrega (id_activo, id_usuario, observaciones)
                        VALUES (%s, %s, %s)
                    """, (id_activo, usuario_sel[0], observaciones))

                    from historial import registrar_cambio
                    usuario_actual = st.session_state.get("username", "desconocido")
                    registrar_cambio(
                        "actas_entrega", id_activo, "generacion_acta",
                        "—",
                        f"Acta generada para activo: {a[1]} | Responsable: {usuario_sel[1]}",
                        usuario_actual
                    )

                    pdf = generar_pdf_acta(a, usuario_sel, observaciones)
                    st.success("✅ Acta generada y guardada correctamente")
                st.download_button(
                    label="📥 Descargar Acta PDF",
                    data=pdf,
                    file_name=f"acta_entrega_{a[1]}_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf"
                )

    # ── TAB 2: SUBIR ACTA FIRMADA ────────────────
    with tab2:
        st.subheader("📎 Subir Acta Firmada Escaneada")

        actas, _ = obtener_datos("""
            SELECT ac.id_acta, a.nombre, u.nombre, ac.fecha_entrega
            FROM actas_entrega ac
            JOIN activos a ON ac.id_activo = a.id_activo
            JOIN usuarios u ON ac.id_usuario = u.id_usuario
            ORDER BY ac.fecha_entrega DESC
        """)

        if actas:
            opciones_actas = [f"Acta #{a[0]} — {a[1]} → {a[2]} ({str(a[3])[:10]})" 
                             for a in actas]
            seleccion_acta = st.selectbox("Selecciona el acta", opciones_actas)
            id_acta_sel = int(seleccion_acta.split("#")[1].split(" ")[0])

            archivo = st.file_uploader(
                "Sube el acta firmada escaneada (PDF o imagen)",
                type=["pdf", "png", "jpg", "jpeg"])

            if archivo and st.button("📎 Guardar Acta Firmada", type="primary"):
                contenido = archivo.read()
                ejecutar_query("""
                    UPDATE actas_entrega 
                    SET archivo_firmado = %s, nombre_archivo = %s
                    WHERE id_acta = %s
                """, (contenido, archivo.name, id_acta_sel))
                st.success("✅ Acta firmada guardada correctamente")
        else:
            st.info("No hay actas generadas todavía. Genera una primero.")

    # ── TAB 3: BUSCAR POR USUARIO ────────────────
    with tab3:
        st.subheader("🔍 Actas por Usuario")

        usuarios, _ = obtener_datos(
            "SELECT id_usuario, nombre FROM usuarios ORDER BY nombre")

        if usuarios:
            opciones_usr = [f"{u[0]} - {u[1]}" for u in usuarios]
            seleccion_usr = st.selectbox("Selecciona un usuario", opciones_usr)
            id_usr = int(seleccion_usr.split(" - ")[0])

            actas_usr, _ = obtener_datos("""
                SELECT 
                    ac.id_acta,
                    a.nombre as activo,
                    a.tipo,
                    a.serial,
                    ac.fecha_entrega,
                    ac.observaciones,
                    CASE WHEN ac.archivo_firmado IS NOT NULL 
                         THEN '✅ Sí' ELSE '⏳ Pendiente' END as firmada
                FROM actas_entrega ac
                JOIN activos a ON ac.id_activo = a.id_activo
                WHERE ac.id_usuario = %s
                ORDER BY ac.fecha_entrega DESC
            """, (id_usr,))

            if actas_usr:
                import pandas as pd
                df = pd.DataFrame(actas_usr, columns=[
                    "ID", "Activo", "Tipo", "Serial",
                    "Fecha entrega", "Observaciones", "Firmada"])
                st.dataframe(df, use_container_width=True)
                st.caption(f"Total: {len(df)} actas para este usuario")

                # Descargar acta firmada
                st.divider()
                st.subheader("📥 Descargar acta firmada")
                id_descargar = st.number_input("ID del acta a descargar", 
                                               min_value=1, step=1)
                
                if st.button("Buscar acta"):
                    archivo_acta, _ = obtener_datos("""
                        SELECT archivo_firmado, nombre_archivo 
                        FROM actas_entrega 
                        WHERE id_acta = %s AND id_usuario = %s
                    """, (id_descargar, id_usr))
                    
                    if archivo_acta and archivo_acta[0][0]:
                        st.download_button(
                            label="📥 Descargar acta firmada",
                            data=bytes(archivo_acta[0][0]),
                            file_name=archivo_acta[0][1],
                            mime="application/octet-stream"
                        )
                    else:
                        st.warning("Esta acta aún no tiene archivo firmado subido")
            else:
                st.info("Este usuario no tiene actas generadas todavía.")
        else:
            st.info("No hay usuarios registrados.")
