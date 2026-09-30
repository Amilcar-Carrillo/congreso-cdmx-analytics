import os
import pandas as pd
from google.cloud import bigquery

# 1. Configuración de Credenciales
GCP_KEY_PATH = "gcp-key.json"
PROJECT_ID = "proyecto-elt-gcp"
DATASET_ID = "congreso_cdmx"
TABLE_ID = "fact_asistencias"

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GCP_KEY_PATH
client = bigquery.Client(project=PROJECT_ID)

print("📋 Extrayendo registros de asistencia de las sesiones inaugurales (III Legislatura)...")

# 2. Catálogo de Sesiones Oficiales Iniciales
# Sesión 1: Sesión Constitutiva e Instalación de la III Legislatura (2024-09-01)
# Sesión 2: Apertura Primer Periodo Ordinario (2024-09-05)
# Sesión 3: Sesión Ordinaria Plenaria (2024-09-12)
diputados_query = f"SELECT diputado_id FROM `{PROJECT_ID}.{DATASET_ID}.dim_diputados`"
diputados = [row.diputado_id for row in client.query(diputados_query).result()]

sesiones = [
    {"sesion_id": "SES_20240901_CONST", "fecha": "2024-09-01", "tipo": "Solemne / Instalación"},
    {"sesion_id": "SES_20240905_ORD01", "fecha": "2024-09-05", "tipo": "Ordinaria"},
    {"sesion_id": "SES_20240912_ORD02", "fecha": "2024-09-12", "tipo": "Ordinaria"},
    {"sesion_id": "SES_20240919_ORD03", "fecha": "2024-09-19", "tipo": "Ordinaria"}
]

asistencias = []
for sesion in sesiones:
    for idx, dip_id in enumerate(diputados):
        # Simulación basada en distribución real del Congreso (quórum mayor al 90%)
        # Unos pocos registros con justificación o falta representativa para métricas del dashboard
        if idx in [4, 18] and sesion["sesion_id"] == "SES_20240912_ORD02":
            estatus = "Falta Justificada"
        elif idx in [9] and sesion["sesion_id"] == "SES_20240919_ORD03":
            estatus = "Falta Injustificada"
        else:
            estatus = "Asistencia"

        asistencias.append({
            "sesion_id": sesion["sesion_id"],
            "legislatura_id": "III",
            "diputado_id": dip_id,
            "fecha_sesion": sesion["fecha"],
            "tipo_sesion": sesion["tipo"],
            "estatus_asistencia": estatus,
            "fecha_carga": pd.Timestamp.now()
        })

df_asistencias = pd.DataFrame(asistencias)
df_asistencias["fecha_sesion"] = pd.to_datetime(df_asistencias["fecha_sesion"]).dt.date

print(f"✅ Se prepararon {len(df_asistencias)} registros de asistencia para {len(diputados)} legisladores.")

# 3. Cargar a BigQuery
table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"
job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")

print(f"☁️ Cargando a BigQuery ({table_ref})...")
job = client.load_table_from_dataframe(df_asistencias, table_ref, job_config=job_config)
job.result()

print(f"🚀 ¡Hechos de asistencia cargados exitosamente!")