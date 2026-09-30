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

print("📜 Iniciando Backfill Histórico: II Legislatura (2021-2024)...")

# 2. Diputados representativos de la II Legislatura
diputados_ii = [
    {"diputado_id": "DIP_II_01", "legislatura_id": "II", "nombre_completo": "Christian Damián Von Roehrich", "partido": "PAN", "grupo_parlamentario": "Partido Acción Nacional", "tipo_eleccion": "MR", "distrito_alcaldia": "Distrito 17 - Benito Juárez", "estatus": "Baja", "foto_url": ""},
    {"diputado_id": "DIP_II_02", "legislatura_id": "II", "nombre_completo": "Martha Soledad Ávila Ventura", "partido": "MORENA", "grupo_parlamentario": "Morena", "tipo_eleccion": "MR", "distrito_alcaldia": "Distrito 28 - Iztapalapa", "estatus": "Activo", "foto_url": ""},
    {"diputado_id": "DIP_II_03", "legislatura_id": "II", "nombre_completo": "Jesús Sesma Suárez", "partido": "PVEM", "grupo_parlamentario": "Partido Verde Ecologista de México", "tipo_eleccion": "RP", "distrito_alcaldia": "Plurinominal", "estatus": "Activo", "foto_url": ""},
    {"diputado_id": "DIP_II_04", "legislatura_id": "II", "nombre_completo": "Royfid Torres González", "partido": "MC", "grupo_parlamentario": "Movimiento Ciudadano", "tipo_eleccion": "RP", "distrito_alcaldia": "Plurinominal", "estatus": "Activo", "foto_url": ""},
    {"diputado_id": "DIP_II_05", "legislatura_id": "II", "nombre_completo": "Ernesto Alarcón Jiménez", "partido": "PRI", "grupo_parlamentario": "Partido Revolucionario Institucional", "tipo_eleccion": "MR", "distrito_alcaldia": "Distrito 33 - Magdalena Contreras", "estatus": "Activo", "foto_url": ""},
    {"diputado_id": "DIP_II_06", "legislatura_id": "II", "nombre_completo": "Federico Döring Casar", "partido": "PAN", "grupo_parlamentario": "Partido Acción Nacional", "tipo_eleccion": "RP", "distrito_alcaldia": "Plurinominal", "estatus": "Activo", "foto_url": ""},
    {"diputado_id": "DIP_II_07", "legislatura_id": "II", "nombre_completo": "Circe Camacho Bastida", "partido": "PT", "grupo_parlamentario": "Partido del Trabajo", "tipo_eleccion": "MR", "distrito_alcaldia": "Distrito 25 - Xochimilco", "estatus": "Activo", "foto_url": ""},
]

df_dip = pd.DataFrame(diputados_ii)
df_dip["fecha_registro"] = pd.Timestamp.now()

# Cargar a dim_diputados (con WRITE_APPEND para NO borrar la III Legislatura)
table_dip = f"{PROJECT_ID}.{DATASET_ID}.dim_diputados"
job_config_app = bigquery.LoadJobConfig(write_disposition="WRITE_APPEND")
bq_client.load_table_from_dataframe(df_dip, table_dip, job_config=job_config_app).result()
print(f"✅ Cargados {len(df_dip)} diputados de la II Legislatura en dim_diputados.")

# 3. Asistencias Históricas (Sesiones 2022-2023)
sesiones_ii = [
    {"sesion_id": "SES_II_20220901", "fecha": "2022-09-01", "tipo": "Ordinaria"},
    {"sesion_id": "SES_II_20221015", "fecha": "2022-10-15", "tipo": "Ordinaria"},
    {"sesion_id": "SES_II_20230201", "fecha": "2023-02-01", "tipo": "Ordinaria"},
]

asistencias_ii = []
for s in sesiones_ii:
    for idx, d in enumerate(diputados_ii):
        estatus = "Falta Justificada" if idx == 0 and s["sesion_id"] == "SES_II_20230201" else "Asistencia"
        asistencias_ii.append({
            "sesion_id": s["sesion_id"],
            "legislatura_id": "II",
            "diputado_id": d["diputado_id"],
            "fecha_sesion": s["fecha"],
            "tipo_sesion": s["tipo"],
            "estatus_asistencia": estatus,
            "fecha_carga": pd.Timestamp.now()
        })

df_asist = pd.DataFrame(asistencias_ii)
df_asist["fecha_sesion"] = pd.to_datetime(df_asist["fecha_sesion"]).dt.date
table_asist = f"{PROJECT_ID}.{DATASET_ID}.fact_asistencias"
bq_client.load_table_from_dataframe(df_asist, table_asist, job_config=job_config_app).result()
print(f"✅ Cargadas {len(df_asist)} asistencias de la II Legislatura en fact_asistencias.")

# 4. Iniciativa Histórica y Vectorización
iniciativas_ii = [
    {
        "iniciativa_id": "INI_II_001",
        "legislatura_id": "II",
        "diputado_id": "DIP_II_03",
        "diputado_nombre": "Jesús Sesma Suárez",
        "partido": "PVEM",
        "titulo": "Ley de Protección y Bienestar Animal de la Ciudad de México",
        "materia": "Medio Ambiente y Bienestar Animal",
        "estatus_proceso": "Aprobada por el Pleno",
        "resumen_texto": "Reforma integral a la Ley de Protección a los Animales para sancionar el abandono de animales de compañía, regular guarderías y paseadores de perros, y elevar penas por crueldad y maltrato animal en la CDMX.",
        "fecha_presentacion": "2023-03-28"
    },
    {
        "iniciativa_id": "INI_II_002",
        "legislatura_id": "II",
        "diputado_id": "DIP_II_04",
        "diputado_nombre": "Royfid Torres González",
        "partido": "MC",
        "titulo": "Reconocimiento y Presupuesto para el Sistema Integral de Cuidados",
        "materia": "Bienestar Social y Género",
        "estatus_proceso": "Pendiente de Dictamen",
        "resumen_texto": "Propuesta de ley para establecer el Sistema de Cuidados de la Ciudad de México, garantizando remuneración, apoyo social y relevos para personas cuidadoras de adultos mayores e infantes.",
        "fecha_presentacion": "2022-11-15"
    }
]

print("🧠 Vectorizando iniciativas históricas con text-embedding-004...")
rows_vec = []
for ini in iniciativas_ii:
    texto = f"Estatus: {ini['estatus_proceso']}. Materia: {ini['materia']}. Título: {ini['titulo']}. Resumen: {ini['resumen_texto']}"
    resp = ai_client.models.embed_content(model="text-embedding-004", contents=texto)
    r = ini.copy()
    r["text_embedding"] = resp.embeddings[0].values
    rows_vec.append(r)

df_vec = pd.DataFrame(rows_vec)
df_vec["fecha_presentacion"] = pd.to_datetime(df_vec["fecha_presentacion"]).dt.date
table_vec = f"{PROJECT_ID}.{DATASET_ID}.fact_iniciativas_vectors"
bq_client.load_table_from_dataframe(df_vec, table_vec, job_config=job_config_app).result()

print("🚀 ¡Backfill de la II Legislatura completado exitosamente en BigQuery!")