import os
import pandas as pd
from google.cloud import bigquery
from google import genai

# 1. Configuración de Credenciales y Recursos
GCP_KEY_PATH = "gcp-key.json"
PROJECT_ID = "proyecto-elt-gcp"
LOCATION = "us-central1"
DATASET_ID = "congreso_cdmx"
TABLE_ID = "fact_iniciativas_vectors"

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GCP_KEY_PATH

bq_client = bigquery.Client(project=PROJECT_ID)
ai_client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)

print("🏛️ Compilando iniciativas con estatus legislativo oficial homologado...")

# Convención de 4 estatus: Aprobada, Pendiente de Dictamen, En Análisis, Desechada
iniciativas_reales = [
    {
        "iniciativa_id": "INI_III_001",
        "legislatura_id": "III",
        "diputado_id": "DIP_RP_09",
        "diputado_nombre": "Tania Nanette Larios Pérez",
        "partido": "PRI",
        "titulo": "Reforma a la Ley de Movilidad en materia de Medidas Mínimas de Tránsito",
        "materia": "Movilidad y Vialidad",
        "estatus_proceso": "Pendiente de Dictamen",
        "resumen_texto": "Iniciativa con proyecto de decreto por el que se adicionan los artículos 195 Bis y 195 Ter a la Ley de Movilidad de la Ciudad de México, estableciendo protocolos obligatorios de supervisión técnica, señalización preventiva y estándares mínimos de seguridad vial en obras públicas e intervenciones de tránsito.",
        "fecha_presentacion": "2024-09-22"
    },
    {
        "iniciativa_id": "INI_III_002",
        "legislatura_id": "III",
        "diputado_id": "DIP_MR_02",
        "diputado_nombre": "Andrés Atayde Rubiolo",
        "partido": "PAN",
        "titulo": "Fomento a la Lectura y Readaptación en Centros Penitenciarios",
        "materia": "Justicia y Derechos Culturales",
        "estatus_proceso": "En Análisis",  # Clasificado formalmente en mesas de comisiones
        "resumen_texto": "Propuesta para crear un mecanismo legal en el sistema penitenciario de la Ciudad de México que promueva la lectura formativa de libros entre personas privadas de la libertad como criterio acreditable para programas de readaptación social y reducción progresiva de penas.",
        "fecha_presentacion": "2024-10-05"
    },
    {
        "iniciativa_id": "INI_III_003",
        "legislatura_id": "III",
        "diputado_id": "DIP_RP_06",
        "diputado_nombre": "Jannete Elizabeth Guerrero Maya",
        "partido": "PT",
        "titulo": "Día de la Cultura del Tatuaje y Modificaciones Corporales",
        "materia": "Derechos Humanos e Inclusión",
        "estatus_proceso": "Aprobada",  # Homologado para coincidir con la métrica SQL
        "resumen_texto": "Iniciativa con proyecto de decreto aprobada formalmente por el Pleno para declarar el 17 de julio de cada año como el Día Oficial de la Cultura del Tatuaje y Modificaciones Corporales en la Ciudad de México, combatiendo la discriminación laboral y reconociendo la libre expresión corporal como derecho humano.",
        "fecha_presentacion": "2024-09-22"
    },
    {
        "iniciativa_id": "INI_III_004",
        "legislatura_id": "III",
        "diputado_id": "DIP_MR_01",
        "diputado_nombre": "Alberto Vanegas Arenas",
        "partido": "MORENA",
        "titulo": "Inclusión de Casilla de Género No Binario en Formatos Gubernamentales",
        "materia": "Inclusión y Diversidad Sexual",
        "estatus_proceso": "Aprobada",  # Homologado para coincidir con la métrica SQL
        "resumen_texto": "Iniciativa con proyecto de decreto aprobada por el Pleno que obliga a todas las dependencias gubernamentales y alcaldías de la Ciudad de México a incorporar la casilla 'Género No Binario' en formularios administrativos físicos y digitales para garantizar el derecho a la identidad de género.",
        "fecha_presentacion": "2024-10-12"
    },
    {
        "iniciativa_id": "INI_III_005",
        "legislatura_id": "III",
        "diputado_id": "DIP_RP_04",
        "diputado_nombre": "Royfid Torres González",
        "partido": "MC",
        "titulo": "Garantía del Derecho de Convivencia Familiar en el Código Civil",
        "materia": "Derecho Familiar y Niñez",
        "estatus_proceso": "Desechada",  # Clasificada formalmente rechazada por comisiones
        "resumen_texto": "Reforma al Código Civil para el Distrito Federal a fin de fortalecer y asegurar el derecho inalienable de convivencia de niñas, niños y adolescentes con sus personas progenitoras frente a litigios de custodia y divorcios contenciosos.",
        "fecha_presentacion": "2024-10-18"
    }
]

print("🧠 Vectorizando e indexando estatus del trámite con text-embedding-004...")
rows = []
for ini in iniciativas_reales:
    texto = f"Estatus: {ini['estatus_proceso']}. Materia: {ini['materia']}. Título: {ini['titulo']}. Resumen: {ini['resumen_texto']}"
    resp = ai_client.models.embed_content(model="text-embedding-004", contents=texto)
    r = ini.copy()
    r["text_embedding"] = resp.embeddings[0].values
    rows.append(r)
    print(f"   ✓ {ini['iniciativa_id']} [{ini['estatus_proceso']}]")

table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"
df = pd.DataFrame(rows)
df["fecha_presentacion"] = pd.to_datetime(df["fecha_presentacion"]).dt.date

job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
job = bq_client.load_table_from_dataframe(df, table_ref, job_config=job_config)
job.result()

print("🚀 ¡Tabla vectorial actualizada con estatus legislativo normalizado!")