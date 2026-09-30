import os
import pandas as pd
from google.cloud import bigquery
from google import genai

# 1. Configuración de credenciales y entorno
GCP_KEY_PATH = "gcp-key.json"
PROJECT_ID = "proyecto-elt-gcp"
LOCATION = "us-central1"
DATASET_ID = "congreso_cdmx"
TABLE_ID = "fact_iniciativas_vectors"

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GCP_KEY_PATH

bq_client = bigquery.Client(project=PROJECT_ID)
ai_client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)

# 2. Catálogo histórico (I y II Legislaturas)
iniciativas_historicas = [
    # --- I LEGISLATURA (2018-2021) ---
    {
        "iniciativa_id": "INI_I_001",
        "legislatura_id": "I",
        "diputado_id": "DIP_I_01",
        "diputado_nombre": "Valentina Batres Guadarrama",
        "partido": "MORENA",
        "titulo": "Ley de Austeridad, Transparencia en Remuneraciones y Eficiencia del Gasto",
        "materia": "Gasto Público y Finanzas",
        "estatus_proceso": "Aprobada",
        "resumen_texto": "Decreto mediante el cual se expide la Ley de Austeridad de la Ciudad de México, regulando topes máximos salariales y eliminando privilegios en dependencias gubernamentales.",
        "fecha_presentacion": "2018-12-11"
    },
    {
        "iniciativa_id": "INI_I_002",
        "legislatura_id": "I",
        "diputado_id": "DIP_I_02",
        "diputado_nombre": "Alessandra Rojo de la Vega Piccolo",
        "partido": "PVEM",
        "titulo": "Prohibición Integral de Plásticos de un Solo Uso en Comercios",
        "materia": "Medio Ambiente y Ecología",
        "estatus_proceso": "Aprobada",
        "resumen_texto": "Reforma a la Ley de Residuos Sólidos del Distrito Federal para prohibir la comercialización y entrega de bolsas, popotes, cubiertos y recipientes plásticos desechables.",
        "fecha_presentacion": "2019-05-09"
    },
    {
        "iniciativa_id": "INI_I_003",
        "legislatura_id": "I",
        "diputado_id": "DIP_I_03",
        "diputado_nombre": "Mauricio Tabe Echartea",
        "partido": "PAN",
        "titulo": "Agravante de Pena por Robo con Violencia a Pasajeros en Red de Transporte",
        "materia": "Seguridad y Justicia Penal",
        "estatus_proceso": "En Análisis",
        "resumen_texto": "Propuesta de reforma al Código Penal local para catalogar como delito grave sin derecho a fianza el asalto a usuarios dentro del Metro, Metrobús y microbuses.",
        "fecha_presentacion": "2019-10-17"
    },
    {
        "iniciativa_id": "INI_I_004",
        "legislatura_id": "I",
        "diputado_id": "DIP_I_04",
        "diputado_nombre": "Armando Tonatiuh González Case",
        "partido": "PRI",
        "titulo": "Fondo Metropolitano Emergente de Reactivación para Mercados Públicos",
        "materia": "Fomento Económico",
        "estatus_proceso": "Pendiente de Dictamen",
        "resumen_texto": "Creación de un fondo presupuestal tripartita destinado a créditos blandos y subsidios directos a locatarios y tianguistas tras contingencias sanitarias y económicas.",
        "fecha_presentacion": "2020-04-23"
    },
    {
        "iniciativa_id": "INI_I_005",
        "legislatura_id": "I",
        "diputado_id": "DIP_I_05",
        "diputado_nombre": "Víctor Hugo Lobo Román",
        "partido": "PRD",
        "titulo": "Contribución Especial sobre Facturación Bruta a Plataformas Digitales Extranjeras",
        "materia": "Hacienda y Fiscal",
        "estatus_proceso": "Desechada",
        "resumen_texto": "Iniciativa para fijar una tasa impositiva del 5% a servicios de streaming y comercio electrónico internacional sin domicilio fiscal en la capital, rechazada en comisiones unidas.",
        "fecha_presentacion": "2020-11-19"
    },

    # --- II LEGISLATURA (2021-2024) ---
    {
        "iniciativa_id": "INI_II_001",
        "legislatura_id": "II",
        "diputado_id": "DIP_II_01",
        "diputado_nombre": "Jesús Sesma Suárez",
        "partido": "PVEM",
        "titulo": "Ley de Protección y Bienestar a los Animales de la Ciudad de México",
        "materia": "Derechos de los Animales",
        "estatus_proceso": "Aprobada",
        "resumen_texto": "Nueva ley integral para prohibir la venta de animales en vía pública, regular refugios, obligar al registro en RUAC y elevar penas corporales contra el maltrato animal.",
        "fecha_presentacion": "2023-02-14"
    },
    {
        "iniciativa_id": "INI_II_002",
        "legislatura_id": "II",
        "diputado_id": "DIP_II_02",
        "diputado_nombre": "Martha Soledad Ávila Ventura",
        "partido": "MORENA",
        "titulo": "Regulación del Hospedaje Turístico Temporal en Plataformas Digitales",
        "materia": "Turismo y Vivienda",
        "estatus_proceso": "Aprobada",
        "resumen_texto": "Reforma a la Ley de Turismo local que crea un padrón obligatorio de anfitriones de plataformas como Airbnb y limita al 50% anual el uso de inmuebles para evitar gentrificación.",
        "fecha_presentacion": "2023-11-28"
    },
    {
        "iniciativa_id": "INI_II_003",
        "legislatura_id": "II",
        "diputado_id": "DIP_II_03",
        "diputado_nombre": "Federico Döring Casar",
        "partido": "PAN",
        "titulo": "Obligatoriedad de Sistemas Cosecha de Lluvia en Edificaciones Nuevas",
        "materia": "Gestión Integral del Agua",
        "estatus_proceso": "En Análisis",
        "resumen_texto": "Modificación a la Ley de Aguas y Ley de Desarrollo Urbano para condicionar licencias de construcción comercial y habitacional a la instalación de plantas de captación pluvial.",
        "fecha_presentacion": "2023-04-18"
    },
    {
        "iniciativa_id": "INI_II_004",
        "legislatura_id": "II",
        "diputado_id": "DIP_II_04",
        "diputado_nombre": "Mónica Fernández César",
        "partido": "PRI",
        "titulo": "Tasa Cero en Impuesto sobre Nóminas a Contrataciones de Primer Empleo",
        "materia": "Trabajo y Empleo Joven",
        "estatus_proceso": "Pendiente de Dictamen",
        "resumen_texto": "Estímulo fiscal de exención del ISN durante 24 meses a personas físicas y morales que contraten formalmente a jóvenes recién egresados sin experiencia previa.",
        "fecha_presentacion": "2022-09-08"
    },
    {
        "iniciativa_id": "INI_II_005",
        "legislatura_id": "II",
        "diputado_id": "DIP_II_05",
        "diputado_nombre": "Royfid Torres González",
        "partido": "MC",
        "titulo": "Tope Tarifario Obligatorio y Eliminación del Fraccionamiento en Estacionamientos",
        "materia": "Defensa del Consumidor",
        "estatus_proceso": "Desechada",
        "resumen_texto": "Proyecto de decreto para homologar cobros en centros comerciales por fracciones exactas de 15 minutos con gratuidad los primeros 30 minutos, desechado por comisiones.",
        "fecha_presentacion": "2022-05-19"
    }
]

print("🧠 Vectorizando iniciativas históricas (I y II Legislatura) con text-embedding-004...")
rows = []
for ini in iniciativas_historicas:
    texto = f"Estatus: {ini['estatus_proceso']}. Materia: {ini['materia']}. Título: {ini['titulo']}. Resumen: {ini['resumen_texto']}"
    resp = ai_client.models.embed_content(model="text-embedding-004", contents=texto)
    r = ini.copy()
    r["text_embedding"] = resp.embeddings[0].values
    rows.append(r)
    print(f"   ✓ [{ini['legislatura_id']}] {ini['iniciativa_id']} - {ini['estatus_proceso']}: {ini['titulo'][:50]}...")

table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"
df = pd.DataFrame(rows)
df["fecha_presentacion"] = pd.to_datetime(df["fecha_presentacion"]).dt.date

# Inserción incremental (APPEND) para preservar la III Legislatura
job_config = bigquery.LoadJobConfig(write_disposition="WRITE_APPEND")
job = bq_client.load_table_from_dataframe(df, table_ref, job_config=job_config)
job.result()

print("\n🚀 ¡Backfill histórico completado exitosamente en BigQuery!")