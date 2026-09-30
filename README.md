# 🏛️️ Congreso CDMX: Data Pipeline, Hybrid RAG & Legislative Analytics

Plataforma de inteligencia legislativa para el análisis y consulta semántica de la actividad parlamentaria del Congreso de la Ciudad de México (I, II y III Legislaturas), construida sobre una arquitectura Serverless en Google Cloud Platform (GCP).

---

## 📊 Dashboards y Demos en Vivo
* 🔗 **Tablero Ejecutivo en Looker Studio:** [Ver Dashboard de Asistencias e Iniciativas](https://datastudio.google.com/reporting/6d4edf9f-de42-4600-b6ce-a27a21b2ab05)
* 💻 **Aplicación Analítica e Interfaz RAG:** Streamlit con búsqueda vectorial (Vertex AI) y analítica SQL en tiempo real.

---

## 🏗️ Arquitectura del Sistema


[Gaceta / Asistencias]
│
▼
[Cloud Scheduler (Cron)] ──(HTTP Trigger)──► [Cloud Run Functions (Python)]
│
▼
[Google BigQuery Warehouse]
├─ dim_diputados
├─ fact_asistencias
└─ fact_iniciativas_vectors
│
┌──────────────────────────────┴──────────────────────────────┐
▼                                                             ▼
[Looker Studio BI]                                      [Streamlit UI + Vertex AI]
(vw_monitor_integral_diputados)                          (text-embedding-004 + Gemini)


### Componentes Clave:
1. **Pipeline Serverless ELT:** Ingesta programada en Cloud Scheduler (martes y jueves a las 20:00 hrs) conectada a Cloud Run Functions con escala a 0 para optimización FinOps ($0 costo en reposo)[cite: 7, 19].
2. **Data Warehouse Dimensional:** Esquema relacional optimizado en BigQuery (`dim_diputados`, `fact_asistencias`, `fact_iniciativas_vectors`) con inserciones idempotentes[cite: 2, 8, 12].
3. **Hybrid RAG Engine:** Supera las limitaciones del Dense Retrieval convencional al combinar agregaciones analíticas SQL (`COUNTIF` por estatus: Aprobada, En Dictamen, En Análisis, Desechada) con similitud coseno sobre vectores de 768 dimensiones (`text-embedding-004`)[cite: 6, 10, 11].

---

## 🛠️ Stack Tecnológico
* **Cloud & Serverless:** Google Cloud Platform (Cloud Run Functions, Cloud Scheduler, BigQuery)[cite: 2, 7, 8].
* **IA & Generative AI:** Vertex AI (`text-embedding-004`), Gemini LLM, Vector Search (Similitud Coseno)[cite: 6, 11, 12].
* **Ingeniería de Datos:** Python 3.12, SQL (Vistas analíticas y cruces agregados), Pandas, Pandas-GBQ[cite: 2, 10, 14].
* **Visualización & BI:** Looker Studio, Streamlit UI[cite: 5, 15, 20].

---

## 🚀 Instalación y Despliegue Local

1. Clonar el repositorio:
   ```bash
   git clone [https://github.com/TU-USUARIO/congreso-cdmx-analytics.git](https://github.com/TU-USUARIO/congreso-cdmx-analytics.git)
   cd congreso-cdmx-analytics

   Configurar entorno virtual:
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

Credenciales de GCP:

Colocar la clave de cuenta de servicio gcp-key.json en la raíz.

Asignar la variable de entorno:
   
   $env:GOOGLE_APPLICATION_CREDENTIALS = "gcp-key.json"

Iniciar la interfaz web:

streamlit run app.py