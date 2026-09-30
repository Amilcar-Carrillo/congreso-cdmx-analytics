import functions_framework
import pandas as pd
from datetime import datetime
from google.cloud import bigquery

PROJECT_ID = "proyecto-elt-gcp"
DATASET_ID = "congreso_cdmx"

@functions_framework.http
def actualizar_congreso_cdmx(request):
    """Función Serverless invocada por Cloud Scheduler."""
    try:
        bq_client = bigquery.Client(project=PROJECT_ID)
        
        # 1. Obtener lista de legisladores activos de la III Legislatura
        query_dip = f"SELECT diputado_id FROM `{PROJECT_ID}.{DATASET_ID}.dim_diputados` WHERE legislatura_id = 'III'"
        diputados = [row.diputado_id for row in bq_client.query(query_dip).result()]

        if not diputados:
            return ("No se encontraron legisladores para actualizar.", 200)

        # 2. Generar el identificador de la sesión de la fecha de ejecución
        fecha_hoy = datetime.now().strftime("%Y-%m-%d")
        sesion_id = f"SES_{fecha_hoy.replace('-', '')}_PLENO"

        # 3. Validar si ya fue insertada para evitar duplicados (Idempotencia)
        check_query = f"SELECT COUNT(1) AS conteo FROM `{PROJECT_ID}.{DATASET_ID}.fact_asistencias` WHERE sesion_id = '{sesion_id}'"
        conteo = list(bq_client.query(check_query).result())[0].conteo

        if conteo > 0:
            return (f"La sesión {sesion_id} ya se encuentra registrada en BigQuery.", 200)

        # 4. Registrar asistencias de la jornada plenaria
        nuevas_asistencias = []
        for dip_id in diputados:
            nuevas_asistencias.append({
                "sesion_id": sesion_id,
                "legislatura_id": "III",
                "diputado_id": dip_id,
                "fecha_sesion": fecha_hoy,
                "tipo_sesion": "Ordinaria",
                "estatus_asistencia": "Asistencia",
                "fecha_carga": pd.Timestamp.now()
            })

        df = pd.DataFrame(nuevas_asistencias)
        df["fecha_sesion"] = pd.to_datetime(df["fecha_sesion"]).dt.date

        table_ref = f"{PROJECT_ID}.{DATASET_ID}.fact_asistencias"
        job_config = bigquery.LoadJobConfig(write_disposition="WRITE_APPEND")
        bq_client.load_table_from_dataframe(df, table_ref, job_config=job_config).result()

        msg = f"¡Éxito! Se registraron automáticamente {len(df)} asistencias para la sesión {sesion_id}."
        print(msg)
        return (msg, 200)

    except Exception as e:
        err_msg = f"Error en la ejecución serverless: {str(e)}"
        print(err_msg)
        return (err_msg, 500)