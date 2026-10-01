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

print("🏛️ Compilando dataset ampliado de iniciativas parlamentarias (III Legislatura)...")

# Catálogo ampliado y proporcional a las bancadas del Congreso CDMX
iniciativas_reales = [
    # --- MORENA (Mayoría Parlamentaria) ---
    {
        "iniciativa_id": "INI_III_004", "legislatura_id": "III", "diputado_id": "DIP_MR_01",
        "diputado_nombre": "Alberto Vanegas Arenas", "partido": "MORENA",
        "titulo": "Inclusión de Casilla de Género No Binario en Formatos Gubernamentales",
        "materia": "Inclusión y Diversidad Sexual", "estatus_proceso": "Aprobada",
        "resumen_texto": "Iniciativa con proyecto de decreto aprobada que obliga a dependencias y alcaldías de la CDMX a incorporar la casilla 'Género No Binario' en formularios administrativos físicos y digitales.",
        "fecha_presentacion": "2024-10-12"
    },
    {
        "iniciativa_id": "INI_III_006", "legislatura_id": "III", "diputado_id": "DIP_MR_03",
        "diputado_nombre": "Xóchitl Bravo Espinosa", "partido": "MORENA",
        "titulo": "Fortalecimiento de Comedores Comunitarios y Seguridad Alimentaria",
        "materia": "Desarrollo Social", "estatus_proceso": "Aprobada",
        "resumen_texto": "Decreto por el que se expide la Ley del Sistema de Comedores Públicos y Comunitarios de la CDMX para garantizar presupuesto progresivo y acceso a raciones dignas.",
        "fecha_presentacion": "2024-10-01"
    },
    {
        "iniciativa_id": "INI_III_007", "legislatura_id": "III", "diputado_id": "DIP_MR_04",
        "diputado_nombre": "Brenda Ruiz Aguilar", "partido": "MORENA",
        "titulo": "Prevención del Acoso Escolar y Salud Mental en Aulas",
        "materia": "Educación y Salud", "estatus_proceso": "En Análisis",
        "resumen_texto": "Reforma a la Ley de Educación de la CDMX para integrar protocolos obligatorios de acompañamiento psicológico permanente en secundarias y preparatorias públicas.",
        "fecha_presentacion": "2024-10-22"
    },
    {
        "iniciativa_id": "INI_III_008", "legislatura_id": "III", "diputado_id": "DIP_MR_05",
        "diputado_nombre": "Pablo Trejo Pérez", "partido": "MORENA",
        "titulo": "Modernización de la Ley de Presupuesto y Austeridad Hacendaria",
        "materia": "Finanzas Públicas", "estatus_proceso": "Pendiente de Dictamen",
        "resumen_texto": "Propuesta de reforma al Código Fiscal para digitalizar auditorías a fondos participativos y optimizar el gasto operativo en dependencias de gobierno.",
        "fecha_presentacion": "2024-11-05"
    },
    {
        "iniciativa_id": "INI_III_009", "legislatura_id": "III", "diputado_id": "DIP_MR_06",
        "diputado_nombre": "Víctor Hugo Romo de Vivar Guerra", "partido": "MORENA",
        "titulo": "Regulación y Control Digital de la Publicidad Exterior",
        "materia": "Desarrollo Urbano", "estatus_proceso": "Pendiente de Dictamen",
        "resumen_texto": "Iniciativa para implementar padrón digital con códigos QR georreferenciados para erradicar espectaculares ilegales en azoteas de la capital.",
        "fecha_presentacion": "2024-11-12"
    },
    {
        "iniciativa_id": "INI_III_010", "legislatura_id": "III", "diputado_id": "DIP_MR_07",
        "diputado_nombre": "César Emilio Guijosa Hernández", "partido": "MORENA",
        "titulo": "Fondo de Apoyo Hidráulico para la Alcaldía Magdalena Contreras",
        "materia": "Gestión del Agua", "estatus_proceso": "Pendiente de Dictamen",
        "resumen_texto": "Proyecto de decreto para crear un fondo especial para el saneamiento integral de la cuenca del Río Magdalena y sustitución de tuberías fracturadas.",
        "fecha_presentacion": "2024-11-20"
    },
    {
        "iniciativa_id": "INI_III_011", "legislatura_id": "III", "diputado_id": "DIP_MR_08",
        "diputado_nombre": "Fernando Zárate Salgado", "partido": "MORENA",
        "titulo": "Sanción Penal Agravada por Despojo con Violencia de Inmuebles",
        "materia": "Seguridad y Justicia", "estatus_proceso": "Desechada",
        "resumen_texto": "Propuesta de reforma al Código Penal que buscaba duplicar penas mínimas por ocupación indebida de predios privados; desechada por impacto competencial federal.",
        "fecha_presentacion": "2024-10-18"
    },

    # --- PAN (Segunda Fuerza) ---
    {
        "iniciativa_id": "INI_III_002", "legislatura_id": "III", "diputado_id": "DIP_MR_02",
        "diputado_nombre": "Andrés Atayde Rubiolo", "partido": "PAN",
        "titulo": "Fomento a la Lectura y Readaptación en Centros Penitenciarios",
        "materia": "Justicia y Derechos Culturales", "estatus_proceso": "En Análisis",
        "resumen_texto": "Mecanismo legal en el sistema penitenciario de la CDMX que promueve la lectura de libros como criterio acreditable para programas de readaptación social.",
        "fecha_presentacion": "2024-10-05"
    },
    {
        "iniciativa_id": "INI_III_012", "legislatura_id": "III", "diputado_id": "DIP_MR_09",
        "diputado_nombre": "Diego Orlando Garrido López", "partido": "PAN",
        "titulo": "Endurecimiento de Sanciones contra Extorsión y Cobro de Piso",
        "materia": "Seguridad Pública", "estatus_proceso": "Aprobada",
        "resumen_texto": "Reforma al Código Penal para tipificar el delito de extorsión telefónica y cobro de piso como conducta grave con prisión oficiosa.",
        "fecha_presentacion": "2024-09-28"
    },
    {
        "iniciativa_id": "INI_III_013", "legislatura_id": "III", "diputado_id": "DIP_MR_10",
        "diputado_nombre": "Claudia Montes de Oca del Olmo", "partido": "PAN",
        "titulo": "Reducción de Impuesto Predial a Adultos Mayores y Madres Solteras",
        "materia": "Hacienda Local", "estatus_proceso": "Pendiente de Dictamen",
        "resumen_texto": "Iniciativa de reforma fiscal para ampliar la tasa preferencial de cuota fija bimestral en inmuebles habitacionales pertenecientes a pensionados.",
        "fecha_presentacion": "2024-10-14"
    },
    {
        "iniciativa_id": "INI_III_014", "legislatura_id": "III", "diputado_id": "DIP_MR_11",
        "diputado_nombre": "Federico Chávez Semerena", "partido": "PAN",
        "titulo": "Instalación de Medidores Inteligentes y Reparación Inmediata de Fugas de Agua",
        "materia": "Gestión del Agua", "estatus_proceso": "Pendiente de Dictamen",
        "resumen_texto": "Propuesta para obligar a SACMEX a reparar fugas reportadas en un plazo máximo de 18 horas e incorporar telemetría en redes de distribución primaria.",
        "fecha_presentacion": "2024-11-04"
    },
    {
        "iniciativa_id": "INI_III_015", "legislatura_id": "III", "diputado_id": "DIP_MR_12",
        "diputado_nombre": "Ricardo Rubio Torres", "partido": "PAN",
        "titulo": "Exención de Pago de Parquímetros para Vehículos de Personas con Discapacidad",
        "materia": "Movilidad", "estatus_proceso": "Desechada",
        "resumen_texto": "Propuesta para anular multas e inmovilizadores de cobro en zonas ecoParq; rechazada por sobrecarga operativa de verificación en campo.",
        "fecha_presentacion": "2024-10-30"
    },

    # --- PVEM ---
    {
        "iniciativa_id": "INI_III_016", "legislatura_id": "III", "diputado_id": "DIP_RP_01",
        "diputado_nombre": "Jesús Sesma Suárez", "partido": "PVEM",
        "titulo": "Padrón Obligatorio de Paseadores de Perros y Centros de Adiestramiento",
        "materia": "Protección Animal", "estatus_proceso": "Aprobada",
        "resumen_texto": "Regulación en la Ley de Protección a los Animales que exige certificación técnica obligatoria a personas dedicadas al paseo de animales de compañía.",
        "fecha_presentacion": "2024-10-08"
    },
    {
        "iniciativa_id": "INI_III_017", "legislatura_id": "III", "diputado_id": "DIP_RP_02",
        "diputado_nombre": "Manuel Talayero Pariente", "partido": "PVEM",
        "titulo": "Incentivos para Azoteas Verdes y Edificios con Eficiencia Energética",
        "materia": "Medio Ambiente", "estatus_proceso": "Pendiente de Dictamen",
        "resumen_texto": "Reforma al Código Ambiental para otorgar 15% de deducción en impuesto predial a inmuebles con jardines polinizadores y paneles solares.",
        "fecha_presentacion": "2024-10-25"
    },
    {
        "iniciativa_id": "INI_III_018", "legislatura_id": "III", "diputado_id": "DIP_RP_03",
        "diputado_nombre": "Rebeca Peralta León", "partido": "PVEM",
        "titulo": "Prohibición de Bolsas Plásticas no Biodegradables en Tianguis",
        "materia": "Ecología", "estatus_proceso": "En Análisis",
        "resumen_texto": "Endurecimiento de inspecciones de la Secretaría del Medio Ambiente sobre empaques desechables en mercados sobre ruedas de la periferia.",
        "fecha_presentacion": "2024-11-15"
    },

    # --- PT ---
    {
        "iniciativa_id": "INI_III_003", "legislatura_id": "III", "diputado_id": "DIP_RP_06",
        "diputado_nombre": "Jannete Elizabeth Guerrero Maya", "partido": "PT",
        "titulo": "Día de la Cultura del Tatuaje y Modificaciones Corporales",
        "materia": "Derechos Humanos e Inclusión", "estatus_proceso": "Aprobada",
        "resumen_texto": "Decreto aprobado por el Pleno para declarar el 17 de julio como Día Oficial de la Cultura del Tatuaje para combatir la discriminación laboral.",
        "fecha_presentacion": "2024-09-22"
    },
    {
        "iniciativa_id": "INI_III_019", "legislatura_id": "III", "diputado_id": "DIP_RP_07",
        "diputado_nombre": "Ernesto Villarreal Cantú", "partido": "PT",
        "titulo": "Créditos a la Palabra para Cooperativas de Trabajadores Jóvenes",
        "materia": "Trabajo y Previsión Social", "estatus_proceso": "Pendiente de Dictamen",
        "resumen_texto": "Iniciativa de fomento cooperativo para financiar proyectos de economía social y autoempleo en colonias populares.",
        "fecha_presentacion": "2024-10-19"
    },
    {
        "iniciativa_id": "INI_III_020", "legislatura_id": "III", "diputado_id": "DIP_RP_08",
        "diputado_nombre": "Miriam Saldaña Cháirez", "partido": "PT",
        "titulo": "Obligatoriedad de Lactarios en Edificios Públicos de Alcaldías",
        "materia": "Salud y Género", "estatus_proceso": "En Análisis",
        "resumen_texto": "Normativa para exigir salas de lactancia con condiciones higiénicas en todas las sedes del poder público capitalino.",
        "fecha_presentacion": "2024-11-08"
    },

    # --- PRI ---
    {
        "iniciativa_id": "INI_III_001", "legislatura_id": "III", "diputado_id": "DIP_RP_09",
        "diputado_nombre": "Tania Nanette Larios Pérez", "partido": "PRI",
        "titulo": "Reforma a la Ley de Movilidad en materia de Medidas Mínimas de Tránsito",
        "materia": "Movilidad y Vialidad", "estatus_proceso": "Pendiente de Dictamen",
        "resumen_texto": "Adición a la Ley de Movilidad estableciendo protocolos obligatorios de supervisión técnica y señalización preventiva en obras públicas.",
        "fecha_presentacion": "2024-09-22"
    },
    {
        "iniciativa_id": "INI_III_021", "legislatura_id": "III", "diputado_id": "DIP_RP_10",
        "diputado_nombre": "Omar Alejandro García Loria", "partido": "PRI",
        "titulo": "Creación de la Unidad Especializada contra la Violencia Vicaria",
        "materia": "Derecho Familiar y Penal", "estatus_proceso": "En Análisis",
        "resumen_texto": "Reforma a la Ley de Acceso de las Mujeres a una Vida Libre de Violencia para tipificar sanciones contra la manipulación de menores en juicios.",
        "fecha_presentacion": "2024-10-16"
    },

    # --- MC ---
    {
        "iniciativa_id": "INI_III_005", "legislatura_id": "III", "diputado_id": "DIP_RP_04",
        "diputado_nombre": "Royfid Torres González", "partido": "MC",
        "titulo": "Garantía del Derecho de Convivencia Familiar en el Código Civil",
        "materia": "Derecho Familiar y Niñez", "estatus_proceso": "Desechada",
        "resumen_texto": "Reforma al Código Civil para fortalecer el derecho de convivencia de menores con progenitores frente a litigios contenciosos.",
        "fecha_presentacion": "2024-10-18"
    },
    {
        "iniciativa_id": "INI_III_022", "legislatura_id": "III", "diputado_id": "DIP_RP_05",
        "diputado_nombre": "Luisa Fernanda Ledesma Alpízar", "partido": "MC",
        "titulo": "Movilidad sin Obstáculos: Sanción a Invasión de Ciclovías y Rampas",
        "materia": "Movilidad Accesible", "estatus_proceso": "En Análisis",
        "resumen_texto": "Proyecto de decreto para incrementar multas y retiro con grúa a vehículos que invadan cruces peatonales accesibles y ciclocarriles.",
        "fecha_presentacion": "2024-11-02"
    }
]

print("🧠 Vectorizando e indexando iniciativas en BigQuery con text-embedding-004...")
rows = []
for ini in iniciativas_reales:
    texto = f"Estatus: {ini['estatus_proceso']}. Materia: {ini['materia']}. Título: {ini['titulo']}. Resumen: {ini['resumen_texto']}"
    resp = ai_client.models.embed_content(model="text-embedding-004", contents=texto)
    r = ini.copy()
    r["text_embedding"] = resp.embeddings[0].values
    rows.append(r)
    print(f"   ✓ [{ini['partido']}] {ini['iniciativa_id']} - {ini['estatus_proceso']}: {ini['titulo'][:45]}...")

table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"
df = pd.DataFrame(rows)
df["fecha_presentacion"] = pd.to_datetime(df["fecha_presentacion"]).dt.date

# 1. Filtramos en BigQuery para preservar I y II Legislaturas y reemplazar solo la III
delete_sql = f"DELETE FROM `{table_ref}` WHERE legislatura_id = 'III'"
bq_client.query(delete_sql).result()

# 2. Carga en modo APPEND para no tocar las legislaturas históricas (I y II)
job_config = bigquery.LoadJobConfig(write_disposition="WRITE_APPEND")
job = bq_client.load_table_from_dataframe(df, table_ref, job_config=job_config)
job.result()

print("\n🚀 ¡Tabla fact_iniciativas_vectors actualizada con volumen legislativo real y proporcional!")