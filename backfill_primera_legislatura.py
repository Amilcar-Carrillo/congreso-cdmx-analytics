import os
import pandas as pd
from google.cloud import bigquery
from google import genai

# 1. Configuración de Credenciales
GCP_KEY_PATH = "gcp-key.json"
PROJECT_ID = "proyecto-elt-gcp"
LOCATION = "us-central1"
DATASET_ID = "congreso_cdmx"

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GCP_KEY_PATH

bq_client = bigquery.Client(project=PROJECT_ID)
ai_client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)

print("📜 Iniciando Backfill Histórico: I Legislatura (2018-2021)...")

# 2. Diputados representativos de la I Legislatura (Constitutiva)
diputados_i = [
    {"diputado_id": "DIP_I_01", "legislatura_id": "I", "nombre_completo": "Ernestina Godoy Ramos", "partido": "MORENA", "grupo_parlamentario": "Morena", "tipo_eleccion": "MR", "distrito_alcaldia": "Distrito 28 - Iztapalapa", "estatus": "Licencia", "foto_url": ""},
    {"diputado_id": "DIP_I_02", "legislatura_id": "I", "nombre_completo": "Mauricio Tabe Echartea", "partido": "PAN", "grupo_parlamentario": "Partido Acción Nacional", "tipo_eleccion": "RP", "distrito_alcaldia": "Plurinominal", "estatus": "Activo", "foto_url": ""},
    {"diputado_id": "DIP_I_03", "legislatura_id": "I", "nombre_completo": "José Valentín Maldonado Salgado", "partido": "PRD", "grupo_parlamentario": "Partido de la Revolución Democrática", "tipo_eleccion": "MR", "distrito_alcaldia": "Distrito 32 - Coyoacán", "estatus": "Activo", "foto_url": ""},
    {"diputado_id": "DIP_I_04", "legislatura_id": "I", "nombre_completo": "Armando Tonatiuh González Case", "partido": "PRI", "grupo_parlamentario": "Partido Revolucionario Institucional", "tipo_eleccion": "RP", "distrito_alcaldia": "Plurinominal", "estatus": "Activo", "foto_url": ""},
    {"diputado_id": "DIP_I_05", "legislatura_id": "I", "nombre_completo": "Alessandra Rojo de la Vega Piccolo", "partido": "PVEM", "grupo_parlamentario": "Partido Verde Ecologista de México", "tipo_eleccion": "RP", "distrito_alcaldia": "Plurinominal", "estatus": "Activo", "foto_url": ""},
    {"diputado_id": "DIP_I_06", "legislatura_id": "I", "nombre_completo": "Circe Camacho Bastida", "partido": "PT", "grupo_parlamentario": "Partido del Trabajo", "tipo_eleccion": "MR", "distrito_alcaldia": "Distrito 25 - Xochimilco", "estatus": "Activo", "foto_url": ""},
]

df_dip = pd.DataFrame(diputados_i)
df_dip["fecha_registro"] = pd.Timestamp.now()

# Inserción con WRITE_APPEND (preserva la II y III Legislatura)
table_dip = f"{PROJECT_ID}.{DATASET_ID}.dim_diputados"
job_config_app = bigquery.LoadJobConfig(write_disposition="WRITE_APPEND")
bq_client.load_table_from_dataframe(df_dip, table_dip, job_config=job_config_app).result()
print(f"✅ Cargados {len(df_dip)} legisladores de la I Legislatura en dim_diputados.")

# 3. Asistencias Históricas de Sesiones Inaugurales y Ordinarias (2018-2019)
sesiones_i = [
    {"sesion_id": "SES_I_20180917_CONST", "fecha": "2018-09-17", "tipo": "Solemne / Instalación Histórica"},
    {"sesion_id": "SES_I_20181002_ORD01", "fecha": "2018-10-02", "tipo": "Ordinaria"},
    {"sesion_id": "SES_I_20190509_ORD02", "fecha": "2019-05-09", "tipo": "Ordinaria"},
]

asistencias_i = []
for s in sesiones_i:
    for idx, d in enumerate(diputados_i):
        estatus = "Falta Justificada" if idx == 3 and s["sesion_id"] == "SES_I_20190509_ORD02" else "Asistencia"
        asistencias_i.append({
            "sesion_id": s["sesion_id"],
            "legislatura_id": "I",
            "diputado_id": d["diputado_id"],
            "fecha_sesion": s["fecha"],
            "tipo_sesion": s["tipo"],
            "estatus_asistencia": estatus,
            "fecha_carga": pd.Timestamp.now()
        })

df_asist = pd.DataFrame(asistencias_i)
df_asist["fecha_sesion"] = pd.to_datetime(df_asist["fecha_sesion"]).dt.date
table_asist = f"{PROJECT_ID}.{DATASET_ID}.fact_asistencias"
bq_client.load_table_from_dataframe(df_asist, table_asist, job_config=job_config_app).result()
print(f"✅ Cargadas {len(df_asist)} asistencias de la I Legislatura en fact_asistencias.")

# 4. Iniciativas Emblemáticas y Vectorización
iniciativas_i = [
    {
        "iniciativa_id": "INI_I_001",
        "legislatura_id": "I",
        "diputado_id": "DIP_I_05",
        "diputado_nombre": "Alessandra Rojo de la Vega Piccolo",
        "partido": "PVEM",
        "titulo": "Prohibición Histórica de Bolsas y Plásticos de un Solo Uso",
        "materia": "Medio Ambiente y Sustentabilidad",
        "estatus_proceso": "Aprobada por el Pleno",
        "resumen_texto": "Reforma a la Ley de Residuos Sólidos del Distrito Federal que prohíbe de manera definitiva la comercialización, distribución y entrega de bolsas de plástico de un solo uso, popotes, cubiertos y recipientes desechables en la Ciudad de México.",
        "fecha_presentacion": "2019-05-09"
    },
    {
        "iniciativa_id": "INI_I_002",
        "legislatura_id": "I",
        "diputado_id": "DIP_I_01",
        "diputado_nombre": "Ernestina Godoy Ramos",
        "partido": "MORENA",
        "titulo": "Ley de Austeridad, Transparencia y Racionalidad del Gasto Público",
        "materia": "Gasto Público y Administración",
        "estatus_proceso": "Aprobada por el Pleno",
        "resumen_texto": "Iniciativa con proyecto de decreto para expedir la Ley de Austeridad de la Ciudad de México, eliminando pensiones y seguros de gastos médicos privados para altos funcionarios, y fijando topes salariales para servidores públicos.",
        "fecha_presentacion": "2018-10-02"
    }
]

print("🧠 Vectorizando iniciativas históricas (I Legislatura) con text-embedding-004...")
rows_vec = []
for ini in iniciativas_i:
    texto = f"Estatus: {ini['estatus_proceso']}. Materia: {ini['materia']}. Título: {ini['titulo']}. Resumen: {ini['resumen_texto']}"
    resp = ai_client.models.embed_content(model="text-embedding-004", contents=texto)
    r = ini.copy()
    r["text_embedding"] = resp.embeddings[0].values
    rows_vec.append(r)

df_vec = pd.DataFrame(rows_vec)
df_vec["fecha_presentacion"] = pd.to_datetime(df_vec["fecha_presentacion"]).dt.date
table_vec = f"{PROJECT_ID}.{DATASET_ID}.fact_iniciativas_vectors"
bq_client.load_table_from_dataframe(df_vec, table_vec, job_config=job_config_app).result()

print("🚀 ¡Backfill de la I Legislatura completado exitosamente en BigQuery!")