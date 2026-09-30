import os
import streamlit as st
import pandas as pd
from google.cloud import bigquery
from google import genai

# ==============================================================================
# 1. CONFIGURACIÓN DE PÁGINA
# ==============================================================================
st.set_page_config(
    page_title="Congreso CDMX | Monitor Legislativo e IA",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# 2. CONEXIÓN A GCP (BigQuery & Vertex AI)
# ==============================================================================
GCP_KEY_PATH = "gcp-key.json"
PROJECT_ID = "proyecto-elt-gcp"
LOCATION = "us-central1"
DATASET_ID = "congreso_cdmx"

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GCP_KEY_PATH

@st.cache_resource
def get_clients():
    bq = bigquery.Client(project=PROJECT_ID)
    ai = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
    return bq, ai

try:
    bq_client, ai_client = get_clients()
except Exception as e:
    st.error(f"Error conectando con GCP: {e}")
    st.stop()

# ==============================================================================
# 3. BARRA LATERAL (Filtros Globales Dinámicos)
# ==============================================================================
MAPA_LEGISLATURAS = {
    "III Legislatura (2024-2027)": "III",
    "II Legislatura (2021-2024 - Histórico)": "II",
    "I Legislatura (2018-2021 - Histórico)": "I"
}

with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/c/ca/Logo_Congreso_de_la_Ciudad_de_M%C3%A9xico.svg/1200px-Logo_Congreso_de_la_Ciudad_de_M%C3%A9xico.svg.png", width=190)
    st.title("Monitor Legislativo")
    st.caption("Congreso de la Ciudad de México | GCP & IA")
    st.markdown("---")
    
    legislatura_sel = st.selectbox(
        "Periodo Constitucional:",
        list(MAPA_LEGISLATURAS.keys())
    )
    leg_id = MAPA_LEGISLATURAS[legislatura_sel]
    
    st.markdown("---")
    st.info("💡 **Stack Tecnológico:** Google BigQuery (Data Warehouse & Vector Store) + Vertex AI (`text-embedding-004` & Gemini 2.5 Flash).")

# ==============================================================================
# 4. PESTAÑAS PRINCIPALES
# ==============================================================================
tab_bi, tab_rag = st.tabs(["📊 Monitor de Asistencias & Iniciativas", "🤖 Asistente RAG de Consultas"])

# ------------------------------------------------------------------------------
# PESTAÑA 1: ANALÍTICA INTEGRADA (ASISTENCIAS + LEYES APROBADAS)
# ------------------------------------------------------------------------------
with tab_bi:
    # 1. Cargar Asistencias
    @st.cache_data(ttl=600)
    def load_asistencias():
        sql = f"SELECT * FROM `{PROJECT_ID}.{DATASET_ID}.vw_kpi_asistencias`"
        return bq_client.query(sql).to_dataframe()

    # 2. Cargar Iniciativas y Leyes
    @st.cache_data(ttl=600)
    def load_iniciativas():
        sql = f"""
        SELECT 
            iniciativa_id,
            legislatura_id,
            diputado_id,
            diputado_nombre,
            partido,
            titulo,
            materia,
            estatus_proceso,
            fecha_presentacion
        FROM `{PROJECT_ID}.{DATASET_ID}.fact_iniciativas_vectors`
        """
        return bq_client.query(sql).to_dataframe()

    df_todo_asist = load_asistencias()
    df_todo_ini = load_iniciativas()

    df_leg_asist = df_todo_asist[df_todo_asist["legislatura_id"] == leg_id].copy()
    df_leg_ini = df_todo_ini[df_todo_ini["legislatura_id"] == leg_id].copy()

    # --- FILTRO POR BANCADA Y BÚSQUEDA ---
    c_filtro1, c_filtro2 = st.columns([1.5, 2.5])
    with c_filtro1:
        if not df_leg_asist.empty:
            partidos = ["Todas las Bancadas"] + sorted(df_leg_asist["grupo_parlamentario"].dropna().unique().tolist())
        else:
            partidos = ["Todas las Bancadas"]
        partido_filtro = st.selectbox("🎯 Filtrar por Grupo Parlamentario:", partidos)

    with c_filtro2:
        busqueda_texto = st.text_input("🔍 Buscar por Diputado(a), Alcaldía o Materia:", placeholder="Ej. Tatuaje, Atayde, Iztapalapa...")

    # Aplicar Filtros
    df_filtrado_asist = df_leg_asist.copy()
    df_filtrado_ini = df_leg_ini.copy()

    if partido_filtro != "Todas las Bancadas":
        df_filtrado_asist = df_filtrado_asist[df_filtrado_asist["grupo_parlamentario"] == partido_filtro]
        df_filtrado_ini = df_filtrado_ini[df_filtrado_ini["partido"] == partido_filtro]
    
    if busqueda_texto.strip():
        txt = busqueda_texto.strip().lower()
        df_filtrado_asist = df_filtrado_asist[
            df_filtrado_asist["nombre_completo"].str.lower().str.contains(txt) |
            df_filtrado_asist["distrito_alcaldia"].str.lower().str.contains(txt)
        ]
        df_filtrado_ini = df_filtrado_ini[
            df_filtrado_ini["titulo"].str.lower().str.contains(txt) |
            df_filtrado_ini["diputado_nombre"].str.lower().str.contains(txt) |
            df_filtrado_ini["materia"].str.lower().str.contains(txt)
        ]

    sub_grupo = f" · {partido_filtro}" if partido_filtro != "Todas las Bancadas" else ""
    st.subheader(f"🏛️ Monitor Parlamentario: {legislatura_sel}{sub_grupo}")

    if df_leg_asist.empty:
        st.warning(f"ℹ️ Aún no hay datos cargados para la **{legislatura_sel}**.")
    else:
        # --- TARJETAS KPI COMBINADAS ---
        total_dips = len(df_filtrado_asist)
        prom_asist = df_filtrado_asist["porcentaje_asistencia"].mean() if total_dips > 0 else 0
        total_iniciativas = len(df_filtrado_ini)
        total_aprobadas = len(df_filtrado_ini[df_filtrado_ini["estatus_proceso"] == "Aprobada por el Pleno"])

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("👥 Legisladores", f"{total_dips}")
        col2.metric("📈 Asistencia Promedio", f"{prom_asist:.1f}%")
        col3.metric("📝 Iniciativas Presentadas", f"{total_iniciativas}")
        col4.metric("⚖️ Leyes / Decretos Aprobados", f"{total_aprobadas}")

        st.markdown("---")

        # --- SECCIÓN DESTACADA: CATÁLOGO DE LEYES Y DECRETOS APROBADOS ---
        df_leyes = df_filtrado_ini[df_filtrado_ini["estatus_proceso"] == "Aprobada por el Pleno"].copy()
        
        st.markdown("##### ⚖️ Iniciativas Aprobadas por el Pleno (Convertidas en Ley o Decreto)")
        if df_leyes.empty:
            st.info("No hay iniciativas con dictamen de ley aprobado para el filtro actual.")
        else:
            config_leyes = {
                "iniciativa_id": st.column_config.TextColumn("Código", width="small"),
                "titulo": st.column_config.TextColumn("Título del Decreto / Ley", width="large"),
                "diputado_nombre": st.column_config.TextColumn("Diputada / Diputado Proponente", width="medium"),
                "partido": st.column_config.TextColumn("Grupo", width="small"),
                "materia": st.column_config.TextColumn("Materia", width="medium"),
                "fecha_presentacion": st.column_config.DateColumn("Fecha Presentación", format="YYYY-MM-DD", width="small"),
            }
            st.dataframe(
                df_leyes[["iniciativa_id", "titulo", "diputado_nombre", "partido", "materia", "fecha_presentacion"]],
                column_config=config_leyes,
                use_container_width=True,
                hide_index=True
            )

        st.markdown("---")

        # --- GRÁFICAS COMPARATIVAS ---
        c_graf1, c_graf2 = st.columns(2)
        with c_graf1:
            st.markdown("##### 📊 Asistencia Promedio por Bancada (%)")
            resumen_asist = df_leg_asist.groupby("grupo_parlamentario")["porcentaje_asistencia"].mean().reset_index()
            resumen_asist = resumen_asist.sort_values(by="porcentaje_asistencia", ascending=False)
            resumen_asist.columns = ["Grupo Parlamentario", "Asistencia Promedio (%)"]
            st.bar_chart(resumen_asist.set_index("Grupo Parlamentario"), color="#2563EB", horizontal=True)

        with c_graf2:
            st.markdown("##### 📜 Iniciativas por Grupo Parlamentario")
            if not df_leg_ini.empty:
                resumen_ini = df_leg_ini.groupby("partido")["iniciativa_id"].count().reset_index()
                resumen_ini.columns = ["Grupo Parlamentario", "Total Iniciativas"]
                resumen_ini = resumen_ini.sort_values(by="Total Iniciativas", ascending=False)
                st.bar_chart(resumen_ini.set_index("Grupo Parlamentario"), color="#059669", horizontal=True)
            else:
                st.info("Sin registros de iniciativas para graficar.")

        st.markdown("---")

        # --- TABLA NOMINAL DE DIPUTADOS Y ASISTENCIAS ---
        st.markdown(f"##### 📋 Registro Nominal de Asistencias ({len(df_filtrado_asist)} legisladores)")
        
        df_mostrar_asist = df_filtrado_asist[[
            "nombre_completo", "grupo_parlamentario", "tipo_eleccion",
            "distrito_alcaldia", "total_sesiones", "asistencias_presentes",
            "faltas_justificadas", "faltas_injustificadas", "porcentaje_asistencia"
        ]].copy()

        column_configuration = {
            "nombre_completo": st.column_config.TextColumn("Diputada / Diputado", width="large"),
            "grupo_parlamentario": st.column_config.TextColumn("Bancada", width="medium"),
            "tipo_eleccion": st.column_config.TextColumn("Elección", width="small"),
            "distrito_alcaldia": st.column_config.TextColumn("Distrito / Alcaldía", width="medium"),
            "total_sesiones": st.column_config.NumberColumn("Sesiones", format="%d", width="small"),
            "asistencias_presentes": st.column_config.NumberColumn("Asistencias", format="%d", width="small"),
            "faltas_justificadas": st.column_config.NumberColumn("Justificadas", format="%d", width="small"),
            "faltas_injustificadas": st.column_config.NumberColumn("Injustificadas", format="%d", width="small"),
            "porcentaje_asistencia": st.column_config.ProgressColumn(
                "% Asistencia",
                format="%0.1f%%",
                min_value=0,
                max_value=100,
                width="medium"
            ),
        }

        st.dataframe(
            df_mostrar_asist,
            column_config=column_configuration,
            use_container_width=True,
            hide_index=True,
            height=380
        )

# ------------------------------------------------------------------------------
# PESTAÑA 2: ASISTENTE RAG (BÚSQUEDA VECTORIAL CON GEMINI)
# ------------------------------------------------------------------------------
with tab_rag:
    st.subheader(f"🤖 Asistente RAG: Iniciativas ({legislatura_sel})")
    st.markdown("Interroga las propuestas de ley en lenguaje natural. El modelo recupera el texto oficial de BigQuery mediante **Similitud Coseno**.")

    st.markdown("##### 💡 Consultas sugeridas:")
    c1, c2, c3 = st.columns(3)
    if "rag_query" not in st.session_state:
        st.session_state["rag_query"] = ""

    with c1:
        if st.button("⚖️ Iniciativas Aprobadas (Leyes)"):
            st.session_state["rag_query"] = "¿Cuántas y cuáles iniciativas se han aprobado en el Pleno?"
    with c2:
        if st.button("🚦 Movilidad y Obras"):
            st.session_state["rag_query"] = "¿Qué propuesta hay sobre medidas mínimas de seguridad en obras públicas y movilidad?"
    with c3:
        if st.button("🐾 Bienestar Animal / Medio Ambiente"):
            st.session_state["rag_query"] = "¿Qué iniciativas existen sobre protección ambiental o de bienestar animal?"

    pregunta = st.text_input(
        "Escribe tu pregunta ciudadana:",
        value=st.session_state["rag_query"],
        placeholder="Ej. ¿Qué iniciativas se han aprobado y qué temas regulan?"
    )

    if st.button("Consultar Iniciativas", type="primary"):
        if not pregunta.strip():
            st.warning("Ingresa una pregunta para consultar la base de datos.")
        else:
            with st.spinner("Buscando en BigQuery y consultando con Gemini..."):
                try:
                    emb_res = ai_client.models.embed_content(
                        model="text-embedding-004",
                        contents=pregunta,
                    )
                    q_vector = emb_res.embeddings[0].values

                    sql_vec = f"""
                    SELECT 
                        iniciativa_id,
                        diputado_nombre,
                        partido,
                        titulo,
                        materia,
                        estatus_proceso,
                        resumen_texto,
                        fecha_presentacion,
                        (1 - ML.DISTANCE(text_embedding, {q_vector}, 'COSINE')) AS cosine_similarity
                    FROM `{PROJECT_ID}.{DATASET_ID}.fact_iniciativas_vectors`
                    WHERE legislatura_id = '{leg_id}'
                    ORDER BY cosine_similarity DESC
                    LIMIT 5
                    """
                    results = list(bq_client.query(sql_vec).result())

                    if not results:
                        st.warning(f"No se encontraron iniciativas para la {legislatura_sel}.")
                    else:
                        context = "\n\n".join([
                            f"[ID: {r.iniciativa_id} | Proponente: {r.diputado_nombre} ({r.partido}) | Estatus: {r.estatus_proceso} | Materia: {r.materia} | Fecha: {r.fecha_presentacion}]\nTítulo: {r.titulo}\nResumen: {r.resumen_texto}"
                            for r in results
                        ])

                        prompt_rag = f"""Eres el Asistente Legislativo Oficial del Congreso de la Ciudad de México.
Responde a la duda ciudadana utilizando ÚNICAMENTE la siguiente información de contexto oficial provista correspondiente a la {legislatura_sel}.
Si el usuario pregunta por conteos o cuántas iniciativas han sido aprobadas o convertidas en ley, cuenta y desglosa explícitamente según el campo 'Estatus' de cada registro en el contexto.
Cita el título de la iniciativa, el nombre del diputado o diputada proponente y su partido político.
Si la información no se encuentra en el contexto, di textualmente: "Actualmente no se encuentra registrada esa información en los archivos disponibles de la legislatura."

--- CONTEXTO OFICIAL DE BIGQUERY ---
{context}
------------------------------------

PREGUNTA DEL CIUDADANO:
{pregunta}

RESPUESTA FUNDAMENTADA:"""

                        response = ai_client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=prompt_rag,
                        )

                        st.subheader("🏛️ Respuesta del Asistente Legislativo:")
                        st.success(response.text)

                        with st.expander("🔍 Ver iniciativas oficiales recuperadas (Similitud Coseno en BigQuery)"):
                            for r in results:
                                st.markdown(f"**Iniciativa:** `{r.iniciativa_id}` | **Estatus:** `{r.estatus_proceso}` | **Similitud:** `{r.cosine_similarity:.4f}`")
                                st.markdown(f"**Diputado(a):** {r.diputado_nombre} ({r.partido})")
                                st.markdown(f"**Materia:** {r.materia} | **Fecha:** {r.fecha_presentacion}")
                                st.info(r.resumen_texto)

                except Exception as e:
                    st.error(f"Error procesando la consulta: {e}")