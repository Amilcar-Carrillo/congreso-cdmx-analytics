import os
import pandas as pd
from google.cloud import bigquery

# 1. Configuración de Credenciales y BigQuery
GCP_KEY_PATH = "gcp-key.json"
PROJECT_ID = "proyecto-elt-gcp"
DATASET_ID = "congreso_cdmx"
TABLE_ID = "dim_diputados"

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GCP_KEY_PATH
client = bigquery.Client(project=PROJECT_ID)

print("🏛️ Preparando Directorio Oficial de la III Legislatura (Congreso CDMX)...")

# 2. Catálogo Oficial de Diputados (III Legislatura 2024-2027)
diputados_oficiales = [
    # MAYORÍA RELATIVA (Distritos)
    {"diputado_id": "DIP_MR_01", "nombre_completo": "Alberto Vanegas Arenas", "partido": "MORENA", "grupo_parlamentario": "Morena", "tipo_eleccion": "MR", "distrito_alcaldia": "Distrito 14 - Tlalpan"},
    {"diputado_id": "DIP_MR_02", "nombre_completo": "Andrés Atayde Rubiolo", "partido": "PAN", "grupo_parlamentario": "Partido Acción Nacional", "tipo_eleccion": "MR", "distrito_alcaldia": "Distrito 17 - Benito Juárez"},
    {"diputado_id": "DIP_MR_03", "nombre_completo": "Martha Soledad Ávila Ventura", "partido": "MORENA", "grupo_parlamentario": "Morena", "tipo_eleccion": "MR", "distrito_alcaldia": "Distrito 28 - Iztapalapa"},
    {"diputado_id": "DIP_MR_04", "nombre_completo": "Jesús Sesma Suárez", "partido": "PVEM", "grupo_parlamentario": "Partido Verde Ecologista de México", "tipo_eleccion": "MR", "distrito_alcaldia": "Distrito 5 - Azcapotzalco"},
    {"diputado_id": "DIP_MR_05", "nombre_completo": "Daniela Gicela Álvarez Camacho", "partido": "PAN", "grupo_parlamentario": "Partido Acción Nacional", "tipo_eleccion": "MR", "distrito_alcaldia": "Distrito 16 - Tlalpan"},
    {"diputado_id": "DIP_MR_06", "nombre_completo": "Pablo Trejo Pérez", "partido": "PRD", "grupo_parlamentario": "Partido de la Revolución Democrática", "tipo_eleccion": "MR", "distrito_alcaldia": "Distrito 15 - Iztacalco"},
    {"diputado_id": "DIP_MR_07", "nombre_completo": "Israel Moreno Rivera", "partido": "PVEM", "grupo_parlamentario": "Partido Verde Ecologista de México", "tipo_eleccion": "MR", "distrito_alcaldia": "Distrito 10 - Venustiano Carranza"},
    {"diputado_id": "DIP_MR_08", "nombre_completo": "Adriana María Guadalupe Espinosa de los Monteros", "partido": "MORENA", "grupo_parlamentario": "Morena", "tipo_eleccion": "MR", "distrito_alcaldia": "Distrito 8 - Tláhuac"},
    {"diputado_id": "DIP_MR_09", "nombre_completo": "Judith Vanegas Tapia", "partido": "MORENA", "grupo_parlamentario": "Morena", "tipo_eleccion": "MR", "distrito_alcaldia": "Distrito 7 - Milpa Alta y Tláhuac"},
    {"diputado_id": "DIP_MR_10", "nombre_completo": "Claudia Montes de Oca Olmo", "partido": "PAN", "grupo_parlamentario": "Partido Acción Nacional", "tipo_eleccion": "MR", "distrito_alcaldia": "Distrito 23 - Álvaro Obregón"},
    {"diputado_id": "DIP_MR_11", "nombre_completo": "Elvia Estrada Barba", "partido": "PVEM", "grupo_parlamentario": "Partido Verde Ecologista de México", "tipo_eleccion": "MR", "distrito_alcaldia": "Distrito 11 - Venustiano Carranza e Iztacalco"},
    {"diputado_id": "DIP_MR_12", "nombre_completo": "Víctor Varela López", "partido": "PVEM", "grupo_parlamentario": "Partido Verde Ecologista de México", "tipo_eleccion": "MR", "distrito_alcaldia": "Distrito 27 - Iztapalapa"},
    {"diputado_id": "DIP_MR_13", "nombre_completo": "Rebeca Peralta León", "partido": "PVEM", "grupo_parlamentario": "Partido Verde Ecologista de México", "tipo_eleccion": "MR", "distrito_alcaldia": "Distrito 24 - Iztapalapa"},
    {"diputado_id": "DIP_MR_14", "nombre_completo": "Emilio Guijosa Hernández", "partido": "MORENA", "grupo_parlamentario": "Morena", "tipo_eleccion": "MR", "distrito_alcaldia": "Distrito 33 - Magdalena Contreras"},
    {"diputado_id": "DIP_MR_15", "nombre_completo": "Alejandro Carbajal González", "partido": "MORENA", "grupo_parlamentario": "Asociación Parlamentaria Progresista de la Transformación", "tipo_eleccion": "MR", "distrito_alcaldia": "Distrito 3 - Azcapotzalco"},
    {"diputado_id": "DIP_MR_16", "nombre_completo": "Gerardo Villanueva Albarrán", "partido": "MORENA", "grupo_parlamentario": "Asociación Parlamentaria Progresista de la Transformación", "tipo_eleccion": "MR", "distrito_alcaldia": "Distrito 26 - Coyoacán"},
    {"diputado_id": "DIP_MR_17", "nombre_completo": "Raúl de Jesús Torres Guerrero", "partido": "PAN", "grupo_parlamentario": "Partido Acción Nacional", "tipo_eleccion": "MR", "distrito_alcaldia": "Diputación Migrante"},
    # REPRESENTACIÓN PROPORCIONAL (Plurinominales)
    {"diputado_id": "DIP_RP_01", "nombre_completo": "Frida Jimena Guillén Ortiz", "partido": "PAN", "grupo_parlamentario": "Partido Acción Nacional", "tipo_eleccion": "RP", "distrito_alcaldia": "Plurinominal"},
    {"diputado_id": "DIP_RP_02", "nombre_completo": "Diego Orlando Garrido López", "partido": "PAN", "grupo_parlamentario": "Partido Acción Nacional", "tipo_eleccion": "RP", "distrito_alcaldia": "Plurinominal"},
    {"diputado_id": "DIP_RP_03", "nombre_completo": "Olivia Garza de los Santos", "partido": "PAN", "grupo_parlamentario": "Partido Acción Nacional", "tipo_eleccion": "RP", "distrito_alcaldia": "Plurinominal"},
    {"diputado_id": "DIP_RP_04", "nombre_completo": "Royfid Torres González", "partido": "MC", "grupo_parlamentario": "Movimiento Ciudadano", "tipo_eleccion": "RP", "distrito_alcaldia": "Plurinominal"},
    {"diputado_id": "DIP_RP_05", "nombre_completo": "Luisa Fernanda Ledesma Alpízar", "partido": "MC", "grupo_parlamentario": "Movimiento Ciudadano", "tipo_eleccion": "RP", "distrito_alcaldia": "Plurinominal"},
    {"diputado_id": "DIP_RP_06", "nombre_completo": "Jannete Elizabeth Guerrero Maya", "partido": "PT", "grupo_parlamentario": "Partido del Trabajo", "tipo_eleccion": "RP", "distrito_alcaldia": "Plurinominal"},
    {"diputado_id": "DIP_RP_07", "nombre_completo": "Silvia Sánchez Barrios", "partido": "PRI", "grupo_parlamentario": "Asociación Parlamentaria Mujeres por el Comercio Feminista e Incluyente", "tipo_eleccion": "RP", "distrito_alcaldia": "Plurinominal"},
    {"diputado_id": "DIP_RP_08", "nombre_completo": "Leticia Haro Jiménez", "partido": "PRI", "grupo_parlamentario": "Asociación Parlamentaria Mujeres por el Comercio Feminista e Incluyente", "tipo_eleccion": "RP", "distrito_alcaldia": "Plurinominal"},
    {"diputado_id": "DIP_RP_09", "nombre_completo": "Tania Nanette Larios Pérez", "partido": "PRI", "grupo_parlamentario": "Partido Revolucionario Institucional", "tipo_eleccion": "RP", "distrito_alcaldia": "Plurinominal"},
    {"diputado_id": "DIP_RP_10", "nombre_completo": "Omar Alejandro García Loria", "partido": "PRI", "grupo_parlamentario": "Partido Revolucionario Institucional", "tipo_eleccion": "RP", "distrito_alcaldia": "Plurinominal"},
    {"diputado_id": "DIP_RP_11", "nombre_completo": "Nora del Carmen Bárbara Arias Contreras", "partido": "PRD", "grupo_parlamentario": "Partido de la Revolución Democrática", "tipo_eleccion": "RP", "distrito_alcaldia": "Plurinominal"},
]

df = pd.DataFrame(diputados_oficiales)
df["legislatura_id"] = "III"
df["estatus"] = "Activo"
df["foto_url"] = ""
df["fecha_registro"] = pd.Timestamp.now()

print(f"✅ Se procesaron {len(df)} legisladores clave de la III Legislatura.")

# 3. Sobrescribir los 3 registros de prueba con la lista oficial completa
table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

job_config = bigquery.LoadJobConfig(
    write_disposition="WRITE_TRUNCATE"  # Sobrescribe datos de prueba dejando la tabla limpia y oficial
)

print(f"☁️ Sincronizando con BigQuery ({table_ref})...")
job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)
job.result()

print(f"🚀 ¡Directorio oficial cargado exitosamente en BigQuery!")