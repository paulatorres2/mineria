PROJECT_DATA: dict = {
    "titulo": "Análisis de Crimen y Seguridad",
    "problema": (
        "Las ciudades enfrentan un incremento sostenido de la criminalidad en zonas urbanas, "
        "dificultando la asignación eficiente de recursos policiales y la toma de decisiones "
        "preventivas. La distribución del crimen no es aleatoria: existen patrones espaciales y "
        "temporales que, si se identifican correctamente mediante minería de datos, permiten "
        "anticipar focos de riesgo y actuar antes de que ocurran los delitos."
    ),
  "afectados": [
            {"titulo": "Ciudadanos", 
             "descripcion": "Son las principales víctimas de la inseguridad urbana, viendo afectada su calidad de vida, movilidad y bienestar."},
            { "titulo": "Cuerpos policiales",
             "descripcion": "Necesitan distribuir patrullajes y recursos de forma inteligente para maximizar la prevención del delito."},
            {"titulo": "Alcaldías y gobiernos locales",
             "descripcion": "Son responsables de las políticas públicas de seguridad y deben justificar inversiones con datos concretos."},
            {"titulo": "Investigadores y analistas",
             "descripcion": "Requieren datos abiertos y modelos predictivos para estudiar la dinámica criminal y proponer soluciones basadas en evidencia."},
        ],
  "contexto": 
         "La distribución del crimen en entornos urbanos sigue patrones espaciales y temporales identificables. Estudios de criminología ambiental demuestran que ciertos vecindarios, horarios y tipos de delito se agrupan de forma consistente. Con el crecimiento de las ciudades y la disponibilidad de datos abiertos de crimen, la minería de datos se convierte en una herramienta clave para transformar enormes volúmenes de reportes policiales en conocimiento accionable que guíe estrategias de prevención del delito.",
         
   "empresa": {
            "nombre": "Departamentos de Policía ",
            "descripcion": "Los datasets provienen de los portales de datos abiertos de los departamentos de policía de Chicago (Chicago Data Portal) y Los Ángeles (LA Open Data). Ambas ciudades publican reportes de crimen en tiempo real con información geoespacial, tipo de delito, fecha, localización y resolución del caso, como parte de sus compromisos de transparencia gubernamental.",
        },
   
      "dataset": {
            "nombre": "Chicago Crime Dataset / LA Crime Data",
            "registros": "+7,000,000 registros (Chicago desde 2001)",
            "variables": "22 columnas (tipo delito, fecha, coordenadas, barrio, etc.)",
            "fuente": "Kaggle / Chicago Data Portal",
            "url": "https://www.kaggle.com/datasets/chicago/chicago-crime",
            "formato": "CSV / GeoJSON",
            "periodo": "2001 – Presente",
        },

    # "tecnicas": [
    #     {
    #         # Técnica de Clasificación: Algoritmos supervisados (Árboles de Decisión, 
    #         # Logistic Regression, Random Forest) que aprenden patrones de reservas 
    #         # canceladas vs. confirmadas para predecir nuevas cancelaciones.
    #         "nombre": "Clasificación",
    #         "desc": "Predecir si una reserva será cancelada (variable objetivo: is_canceled).",
    #     },
    #     {
    #         # Técnica de Clustering: Agrupa clientes en segmentos similares sin variable 
    #         # objetivo (aprendizaje no supervisado). Identifica qué tipos de clientes 
    #         # cancelen más (ej: grupos de alto/bajo riesgo de cancelación).
    #         "nombre": "Clustering",
    #         "desc": "Segmentar perfiles de clientes con mayor propensión a cancelar.",
    #     },
    #     {
    #         # Técnica de Reglas de Asociación: Busca relaciones entre variables 
    #         # (si A ocurre, entonces B es probable). Útil para descubrir patrones 
    #         # ocultos que predicen comportamientos sin necesidad de supervisión.
    #         "nombre": "Reglas de Asociación",
    #         "desc": (
    #             "Identificar patrones como reservas anticipadas + sin depósito + canal OTA → "
    #             "alta probabilidad de cancelación."
    #         ),
    #     },
    #     {
    #         # Técnica de Series Temporales: Analiza datos ordenados en el tiempo 
    #         # para detectar tendencias, estacionalidad y patrones cíclicos. 
    #         # Ideal para predecir comportamientos futuros basados en historiales pasados.
    #         "nombre": "Series Temporales",
    #         "desc": "Detectar épocas del año con mayor tasa de cancelación.",
    #     },
    # ],
}
