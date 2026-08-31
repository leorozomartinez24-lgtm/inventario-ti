import streamlit as st
from database import ejecutar_query, obtener_datos
import pandas as pd
from datetime import date

def mostrar_inventario():
    st.title("💻 Gestión de Activos")
    
    tab1, tab2, tab3 = st.tabs(["📋 Ver Inventario", "➕ Registrar Activo", "✏️ Editar Activo"])
    
    with tab1:
        st.subheader("Inventario de Activos")
        col1, col2, col3 = st.columns(3)
        with col1:
            filtro_tipo = st.selectbox("Filtrar por tipo", 
                ["Todos", "Computador", "Monitor", "Impresora", "Servidor", "Otro"])
        with col2:
            filtro_estado = st.selectbox("Filtrar por estado",
                ["Todos", "Activo", "Por renovar", "En mantenimiento"])
        with col3:
            filtro_sede = st.text_input("Filtrar por sede")

        query = """
            SELECT a.id_activo, a.nombre, a.tipo, a.marca, a.modelo,
                   a.serial, a.fecha_garantia, a.estado, a.sede,
                   u.nombre as responsable
            FROM activos a
            LEFT JOIN usuarios u ON a.id_usuario = u.id_usuario
            WHERE 1=1
        """
        params = []
        if filtro_tipo != "Todos":
            query += " AND a.tipo = %s"
            params.append(filtro_tipo)
        if filtro_estado != "Todos":
            query += " AND a.estado = %s"
            params.append(filtro_estado)
        if filtro_sede:
            query += " AND a.sede ILIKE %s"
            params.append(f"%{filtro_sede}%")
        query += " ORDER BY a.id_activo DESC"
        datos, columnas = obtener_datos(query, params if params else None)

        if datos:
            df = pd.DataFrame(datos, columns=columnas)
            st.dataframe(df, use_container_width=True)
            st.caption(f"Total: {len(df)} activos encontrados")
            excel = df.to_csv(index=False).encode('utf-8')
            st.download_button(label="📥 Exportar a CSV", data=excel,
                file_name="inventario_ti.csv", mime="text/csv")
        else:
            st.info("No hay activos registrados todavía.")

    with tab2:
        st.subheader("Registrar Nuevo Activo")
        with st.form("form_activo"):
            col1, col2 = st.columns(2)
            with col1:
                nombre = st.text_input("Nombre del activo *")
                tipo = st.selectbox("Tipo *", 
                    ["Computador", "Monitor", "Impresora", "Servidor", "Otro"])
                marca = st.text_input("Marca")
                modelo = st.text_input("Modelo")
                serial = st.text_input("Serial")
            with col2:
                sede = st.text_input("Sede")
                estado = st.selectbox("Estado",
                    ["Activo", "Por renovar", "En mantenimiento"])
                fecha_adquisicion = st.date_input("Fecha de adquisición")
                fecha_garantia = st.date_input("Fecha vencimiento garantía")
                usuarios, _ = obtener_datos(
                    "SELECT id_usuario, nombre FROM usuarios ORDER BY nombre")
                opciones = ["Sin asignar"] + [f"{u[0]} - {u[1]}" for u in usuarios]
                responsable = st.selectbox("Responsable", opciones)
            submitted = st.form_submit_button("💾 Guardar Activo")
            if submitted:
                if not nombre:
                    st.error("El nombre del activo es obligatorio")
                else:
                    id_usuario = None
                    if responsable != "Sin asignar":
                        id_usuario = int(responsable.split(" - ")[0])
                    resultado = ejecutar_query("""
                        INSERT INTO activos 
                        (nombre, tipo, marca, modelo, serial, sede, estado, 
                         fecha_adquisicion, fecha_garantia, id_usuario)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (nombre, tipo, marca, modelo, serial, sede, estado,
                          fecha_adquisicion, fecha_garantia, id_usuario))
                    if resultado:
                       st.success(f"✅ Activo '{nombre}' registrado correctamente")
                       st.balloons()
                        

    with tab3:
        st.subheader("✏️ Editar Activo")
        id_editar = st.number_input("ID del activo a editar", min_value=1, step=1)
        
        activo, _ = obtener_datos("""
            SELECT id_activo, nombre, tipo, marca, modelo, serial, 
                   sede, estado, fecha_garantia, id_usuario
            FROM activos WHERE id_activo = %s
        """, (id_editar,))
        
        if activo:
            a = activo[0]
            
            orig_nombre = a[1]
            orig_tipo = a[2]
            orig_marca = a[3] or ""
            orig_modelo = a[4] or ""
            orig_serial = a[5] or ""
            orig_sede = a[6] or ""
            orig_estado = a[7]
            orig_garantia = a[8]
            orig_usuario = a[9]

            with st.form("form_editar"):
                col1, col2 = st.columns(2)
                with col1:
                    nombre = st.text_input("Nombre", value=orig_nombre, key="edit_nombre")
                    tipo = st.selectbox("Tipo", 
                        ["Computador","Monitor","Impresora","Servidor","Otro"],
                        index=["Computador","Monitor","Impresora","Servidor","Otro"].index(orig_tipo) if orig_tipo in ["Computador","Monitor","Impresora","Servidor","Otro"] else 0)
                    marca = st.text_input("Marca", value=orig_marca, key="edit_marca")
                    modelo = st.text_input("Modelo", value=orig_modelo, key="edit_modelo")
                    serial = st.text_input("Serial", value=orig_serial, key="edit_serial")
                with col2:
                    sede = st.text_input("Sede", value=orig_sede, key="edit_sede")
                    estado = st.selectbox("Estado",
                        ["Activo","Por renovar","En mantenimiento"],
                        index=["Activo","Por renovar","En mantenimiento"].index(orig_estado) if orig_estado in ["Activo","Por renovar","En mantenimiento"] else 0)
                    fecha_garantia = st.date_input(
                        "Vencimiento garantía",
                        value=orig_garantia if orig_garantia else date.today()
                    )
                    usuarios, _ = obtener_datos(
                        "SELECT id_usuario, nombre FROM usuarios ORDER BY nombre")
                    opciones = ["Sin asignar"] + [f"{u[0]} - {u[1]}" for u in usuarios]
                    idx = 0
                    if orig_usuario:
                        for i, op in enumerate(opciones):
                            if op.startswith(str(orig_usuario)):
                                idx = i
                    responsable = st.selectbox("Responsable", opciones, index=idx)

                submitted = st.form_submit_button("💾 Actualizar Activo")
                if submitted:
                    id_usuario = None
                    if responsable != "Sin asignar":
                        id_usuario = int(responsable.split(" - ")[0])
                    
                    resultado = ejecutar_query("""
                        UPDATE activos SET
                            nombre=%s, tipo=%s, marca=%s, modelo=%s,
                            serial=%s, sede=%s, estado=%s,
                            fecha_garantia=%s, id_usuario=%s
                        WHERE id_activo=%s
                    """, (nombre, tipo, marca, modelo, serial, sede,
                          estado, fecha_garantia, id_usuario, id_editar))
                    
                    if resultado:
                        from historial import registrar_cambio
                        usuario_actual = st.session_state.get("username", "desconocido")
                        
                        if orig_nombre != nombre:
                            registrar_cambio("activos", id_editar, "nombre",
                                orig_nombre, nombre, usuario_actual)
                        if orig_tipo != tipo:
                            registrar_cambio("activos", id_editar, "tipo",
                                orig_tipo, tipo, usuario_actual)
                        if orig_marca != marca:
                            registrar_cambio("activos", id_editar, "marca",
                                orig_marca, marca, usuario_actual)
                        if orig_modelo != modelo:
                            registrar_cambio("activos", id_editar, "modelo",
                                orig_modelo, modelo, usuario_actual)
                        if orig_serial != serial:
                            registrar_cambio("activos", id_editar, "serial",
                                orig_serial, serial, usuario_actual)
                        if orig_sede != sede:
                            registrar_cambio("activos", id_editar, "sede",
                                orig_sede, sede, usuario_actual)
                        if orig_estado != estado:
                            registrar_cambio("activos", id_editar, "estado",
                                orig_estado, estado, usuario_actual)
                        if orig_usuario != id_usuario:
                            registrar_cambio("activos", id_editar, "responsable",
                                str(orig_usuario or "Sin asignar"),
                                str(id_usuario or "Sin asignar"),
                                usuario_actual)
                        
                        st.success("✅ Activo actualizado correctamente")
                        st.rerun()
        else:
            st.warning("Escribe un ID para buscar el activo")