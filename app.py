import streamlit as st
import pandas as pd
from datetime import datetime
import webbrowser
from streamlit_calendar import calendar
st.set_page_config(layout="wide")


# Archivos locales
PACIENTES = "pacientes.csv"
EVOLUCIONES = "evoluciones.csv"
PAGOS = "pagos.csv"
CITAS = "citas.csv"

# Cargar datos
def cargar_datos(archivo):
    try:
        return pd.read_csv(archivo)
    except:
        return pd.DataFrame()

df_pacientes = cargar_datos(PACIENTES)
df_evoluciones = cargar_datos(EVOLUCIONES)
df_pagos = cargar_datos(PAGOS)
df_citas = cargar_datos(CITAS)

st.set_page_config(page_title="App Odontología", layout="wide")
st.title("🦷 Dra. Jessica Mayor - Rehabilitadora Oral")

menu = st.sidebar.selectbox("Menú", ["Registrar paciente", "Historia clínica", "Pagos", "Citas", "Recordatorios"])

# Registrar paciente
if menu == "Registrar paciente":
    st.subheader("📋 Registrar nuevo paciente")
    with st.form("registro_paciente"):
        cedula = st.text_input("Cédula", max_chars=20)
        nombre = st.text_input("Nombre completo")
        telefono = st.text_input("Teléfono celular")
        fecha_nacimiento = st.date_input("Fecha de nacimiento")
        email = st.text_input("Correo electrónico")
        submitted = st.form_submit_button("Guardar")

        if submitted:
            if not cedula or not nombre or not telefono:
                st.warning("Por favor completa todos los campos obligatorios.")
            elif cedula in df_pacientes["cedula"].values:
                st.warning("Este paciente ya está registrado.")
            else:
                nuevo = pd.DataFrame([{
                    "cedula": cedula,
                    "nombre": nombre,
                    "telefono": telefono,
                    "fecha_nacimiento": fecha_nacimiento,
                    "email": email
                }])
                df_pacientes = pd.concat([df_pacientes, nuevo], ignore_index=True)
                df_pacientes.to_csv(PACIENTES, index=False)
                st.success("Paciente registrado exitosamente.")

# Historia clínica
if menu == "Historia clínica":
    st.subheader("📑 Historia clínica del paciente")
    cedulas = df_pacientes["cedula"].unique()
    seleccion = st.selectbox("Seleccionar paciente por cédula", cedulas)

    if seleccion:
        datos_paciente = df_pacientes[df_pacientes["cedula"] == seleccion].iloc[0]
        st.markdown(f"**Nombre:** {datos_paciente['nombre']}")

        with st.form("form_evolucion"):
            fecha = st.date_input("Fecha de evolución")
            motivo = st.text_area("Motivo de consulta")
            diagnostico = st.text_area("Diagnóstico")
            tratamiento = st.text_area("Tratamiento propuesto")
            evolucion = st.text_area("Evolución")
            enviar = st.form_submit_button("Guardar evolución")

            if enviar:
                nueva_evo = pd.DataFrame([{
                    "cedula": seleccion,
                    "fecha": fecha,
                    "motivo": motivo,
                    "diagnostico": diagnostico,
                    "tratamiento": tratamiento,
                    "evolucion": evolucion
                }])
                df_evoluciones = pd.concat([df_evoluciones, nueva_evo], ignore_index=True)
                df_evoluciones.to_csv(EVOLUCIONES, index=False)
                st.success("Evolución registrada.")

        st.markdown("### 📄 Evoluciones anteriores")
        evoluciones_paciente = df_evoluciones[df_evoluciones["cedula"] == seleccion]
        st.dataframe(evoluciones_paciente)

# Pagos
if menu == "Pagos":
    st.subheader("💰 Pagos del tratamiento")
    opciones_pacientes = df_pacientes.apply(lambda x: f"{x['cedula']} - {x['nombre']}", axis=1)
    seleccion = st.selectbox("Seleccionar paciente", opciones_pacientes)
    cedula_seleccionada = int(seleccion.split(" - ")[0])  # ✅ Convertido a entero

    if cedula_seleccionada:
        total_tratamiento = st.number_input("Valor total del tratamiento", min_value=0)
        fecha_abono = st.date_input("Fecha del abono")
        valor_abono = st.number_input("Valor del abono", min_value=0)
        guardar_pago = st.button("Registrar abono")

        if guardar_pago:
            nuevo_pago = pd.DataFrame([{
                "cedula": cedula_seleccionada,
                "valor_total": total_tratamiento,
                "fecha_abono": fecha_abono,
                "valor_abono": valor_abono
            }])
            df_pagos = pd.concat([df_pagos, nuevo_pago], ignore_index=True)
            df_pagos.to_csv(PAGOS, index=False)
            st.success("Abono registrado correctamente.")

        # Campo para editar
        nuevo_valor_total = st.number_input("💵 Nuevo valor total del tratamiento", value=float(total_tratamiento), min_value=0.0, step=500.0)

        # Guardar el nuevo valor
        if st.button("Actualizar valor total"):
            df_pacientes.loc[df_pacientes["cedula"] == cedula_seleccionada, "valor_total"] = nuevo_valor_total  # ✅ Corrección aquí
            df_pacientes.to_csv(PACIENTES, index=False)
            st.success("✅ Valor total actualizado correctamente.")

        pagos_paciente = df_pagos[df_pagos["cedula"] == cedula_seleccionada]
        suma_abonos = pagos_paciente["valor_abono"].sum()
        ultimo_total = pagos_paciente["valor_total"].max()
        saldo = max(0, ultimo_total - suma_abonos)

        st.markdown(f"**Total del tratamiento:** ${ultimo_total:,.0f}")
        st.markdown(f"**Total abonado:** ${suma_abonos:,.0f}")
        st.markdown(f"**Saldo pendiente:** ${saldo:,.0f}")
        st.dataframe(pagos_paciente)

# Recordatorio
if menu == "Recordatorios":
    st.subheader("📲 Enviar recordatorio por WhatsApp")
    seleccion = st.selectbox("Seleccionar paciente", df_pacientes["cedula"].unique())
    if seleccion:
        paciente = df_pacientes[df_pacientes["cedula"] == seleccion].iloc[0]
        mensaje = st.text_area("Mensaje para el paciente", f"Hola {paciente['nombre']}, te recordamos tu cita odontológica.")
        enviar = st.button("Enviar por WhatsApp")

        if enviar:
            numero = paciente['telefono'].replace("+", "").replace(" ", "")
            link = f"https://wa.me/57{numero}?text={mensaje.replace(' ', '%20')}"
            webbrowser.open_new_tab(link)
            st.success("Abriendo WhatsApp Web...")
if menu == "Citas":
    st.subheader("📅 Agendar nueva cita y ver calendario")

    seleccion = st.selectbox("Seleccionar paciente", df_pacientes["cedula"].unique())

    if "cita_guardada" not in st.session_state:
        st.session_state["cita_guardada"] = False

    if seleccion:
        datos = df_pacientes[df_pacientes["cedula"] == seleccion].iloc[0]
        st.markdown(f"**Paciente:** {datos['nombre']}")

        with st.form("form_cita"):
            fecha_cita = st.date_input("Fecha de la cita")
            hora_cita = st.time_input("Hora de la cita")
            duracion_minutos = st.selectbox("Duración de la cita (minutos)", [15, 30, 45, 60, 90, 120])
            motivo = st.text_input("Motivo de la cita")
            guardar = st.form_submit_button("Agendar cita")

        if guardar and not st.session_state["cita_guardada"]:
            hora_fin = (datetime.combine(fecha_cita, hora_cita) + pd.Timedelta(minutes=duracion_minutos)).time()

            nueva_cita = {
                "cedula": seleccion,
                "fecha": fecha_cita.strftime("%Y-%m-%d"),
                "hora": hora_cita.strftime("%H:%M"),
                "hora_fin": hora_fin.strftime("%H:%M"),
                "motivo": motivo
            }

            existe = (
                (df_citas["cedula"] == nueva_cita["cedula"]) &
                (df_citas["fecha"] == nueva_cita["fecha"]) &
                (df_citas["hora"] == nueva_cita["hora"])
            ).any()

            if not existe:
                nueva_cita_df = pd.DataFrame([nueva_cita])
                df_citas = pd.concat([df_citas, nueva_cita_df], ignore_index=True)
                df_citas.to_csv(CITAS, index=False)
                st.success("✅ Cita agendada correctamente.")
            else:
                st.warning("⚠️ Esta cita ya existe.")

            st.session_state["cita_guardada"] = True

    if st.session_state["cita_guardada"]:
        if st.button("Agendar otra cita"):
            st.session_state["cita_guardada"] = False

    st.markdown("### 📆 Próximas citas")
    if not df_citas.empty:
        df_citas["fecha"] = pd.to_datetime(df_citas["fecha"], errors='coerce')
        hoy = pd.to_datetime(datetime.now().date())
        citas_futuras = df_citas[df_citas["fecha"] >= hoy].copy()
        citas_futuras = citas_futuras.sort_values(by=["fecha", "hora"])
        citas_futuras = citas_futuras.merge(df_pacientes[["cedula", "nombre"]], on="cedula", how="left")
        citas_futuras["fecha"] = citas_futuras["fecha"].dt.strftime("%Y-%m-%d")
        st.dataframe(citas_futuras[["fecha", "hora", "nombre", "motivo"]])
    else:
        st.info("No hay citas registradas aún.")

    st.markdown("### 🗓️ Todas las citas en calendario")
    df_citas["fecha"] = pd.to_datetime(df_citas["fecha"], errors="coerce")
    df_todas_citas = df_citas.merge(df_pacientes[["cedula", "nombre"]], on="cedula", how="left")

    paciente_filtro = st.selectbox("Filtrar por paciente (opcional)", ["Todos"] + df_todas_citas["nombre"].dropna().unique().tolist())

    if paciente_filtro != "Todos":
        df_todas_citas = df_todas_citas[df_todas_citas["nombre"] == paciente_filtro]

    def convertir_citas_a_eventos(df):
     eventos = []
     for idx, row in df.iterrows():
        start = f"{row['fecha'].date()}T{row['hora']}:00"
        end = f"{row['fecha'].date()}T{row['hora_fin']}:59"
        eventos.append({
            "id": idx,  # 👈 Esta línea es la clave
            "title": f"{row['nombre']} - {row['motivo']}",
            "start": start,
            "end": end,
            "extendedProps": {
                "cedula": row["cedula"],
                "valor_total": row.get("valor_total", "N/A"),
                "abono": row.get("abono", "N/A"),
                "saldo": row.get("saldo", "N/A"),
                "motivo": row["motivo"]
            }
        })
     return eventos

    eventos = convertir_citas_a_eventos(df_todas_citas)
    calendar_options = {
        "initialView": "timeGridWeek",
        "locale": "es",
        "slotMinTime": "07:00:00",
        "slotMaxTime": "20:00:00"
    }

    returned_event = calendar(events=eventos, options=calendar_options)
    
    if returned_event and "eventClick" in returned_event:
     evento = returned_event["eventClick"]["event"]
     props = evento.get("extendedProps", {})
     start = evento.get("start")

if start:
    try:
        start_fecha = start[:10]
        start_hora = start[11:16]

        valor_total = props.get("valor_total", "N/A")
        abono = props.get("abono", "N/A")
        saldo = props.get("saldo", "N/A")

        # Formateo si son valores numéricos válidos
        valor_total = f"${int(valor_total):,}" if str(valor_total).isdigit() else valor_total
        abono = f"${int(abono):,}" if str(abono).isdigit() else abono
        saldo = f"${int(saldo):,}" if str(saldo).isdigit() else saldo

        st.markdown("### 📌 Detalle de la cita seleccionada")
        st.write(f"👤 **Paciente**: {evento['title']}")
        st.write(f"🪪 **Cédula**: {props.get('cedula', 'N/A')}")
        st.write(f"📋 **Motivo**: {props.get('motivo', 'N/A')}")
        st.write(f"🗓️ **Fecha**: {start_fecha}")
        st.write(f"🕒 **Hora**: {start_hora}")
    except Exception as e:
        st.error(f"❌ Error mostrando la cita: {e}")
    else:
     st.info("⚠️ Seleccionaste un evento, pero no tiene campo 'start'.")

else:
    st.info("Haz clic en una cita para ver los detalles aquí.")

from datetime import datetime

# Asegúrate de que la columna 'fecha' esté en formato datetime
df_citas["fecha"] = pd.to_datetime(df_citas["fecha"], errors="coerce")

# Filtrar las citas con fecha mayor o igual a hoy
hoy = datetime.today().date()
citas_futuras = df_citas[df_citas["fecha"].dt.date >= hoy]

st.markdown("### 🗑️ Eliminar citas")
for i, row in citas_futuras.iterrows():
    col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 3, 1])
    with col1:
        st.write(row["fecha"])
    with col2:
        st.write(row["hora"])
    with col3:
        st.write(row.get("nombre", ""))
    with col4:
        st.write(row["motivo"])
    with col5:
        if st.button("❌", key=f"eliminar_{i}"):
            condicion = (
                (df_citas["cedula"] == row["cedula"]) &
                (df_todas_citas["nombre"] == row["nombre"])&
                (df_citas["fecha"].dt.date == row["fecha"].date()) &
                (df_citas["hora"] == row["hora"])
            )
            df_citas = df_citas[~condicion]
            df_citas.to_csv(CITAS, index=False)
            # En lugar de st.experimental_rerun()
            st.session_state["cita_guardada"] = False
            st.success("✅ Cita eliminada. Recarga manualmente si no ves los cambios.")


