NIVEL_DATA: dict = {
    "numero": "04",
    "titulo": "Conocimiento Profundo",
    "herramienta": "Apache Spark · MLlib",
    "descripcion": (
        "Entrenamiento y evaluación de modelos de aprendizaje automático con PySpark MLlib. "
        "Procesa más de 1.5 millones de registros a escala para pronosticar el volumen mensual de homicidios, "
        "evaluar métricas de regresión y construir conocimiento predictivo accionable."
    ),
    "color_tag": "Nivel 4 — Profundo",

    "semma": [
        {
            "fase": "Sample",
            "descripcion": "1 500 000 registros cargados desde archivo Parquet local y convertidos a Spark DataFrame distribuido.",
        },
        {
            "fase": "Explore",
            "descripcion": "Cuatro groupBy distribuidos: por departamento/año, arma/zona, tendencia mensual y top municipios.",
        },
        {
            "fase": "Modify",
            "descripcion": "Window functions de Spark generan rezagos lag_1…lag_12, componentes cíclicas mes_sin/mes_cos y tendencia lineal.",
        },
        {
            "fase": "Model",
            "descripcion": "GBTRegressor de MLlib (100 iteraciones, profundidad 4) entrenado con split temporal estricto (últimos 24 meses = test).",
        },
        {
            "fase": "Assess",
            "descripcion": "RMSE, MAE (RegressionEvaluator) y MAPE sobre el conjunto de prueba. Pronóstico recursivo a 3 meses con model.transform().",
        },
    ],

    "pipeline_stages": [
        {
            "num": "01",
            "nombre": "Agregación Mensual",
            "desc": "groupBy(anio, mes) distribuido → ~280 filas. Índice t_idx = anio×100+mes para ordenamiento.",
        },
        {
            "num": "02",
            "nombre": "Window Lag Features",
            "desc": "F.lag() sobre Window ordenado por t_idx genera lag_1…lag_12, mes_sin, mes_cos y tendencia t.",
        },
        {
            "num": "03",
            "nombre": "VectorAssembler",
            "desc": "Ensambla los 8 features numéricos en un vector denso para el estimador.",
        },
        {
            "num": "04",
            "nombre": "GBTRegressor",
            "desc": "Gradient Boosted Trees Regressor (100 iter, maxDepth=4). Predice total mensual de homicidios.",
        },
    ],

    "consultas": [
        {
            "id": "por_departamento_anio",
            "label": "Análisis 01",
            "titulo": "Homicidios por Departamento y Año",
            "descripcion": (
                "groupBy distribuido sobre departamento y año. "
                "Permite comparar volúmenes regionales y detectar tendencias históricas con Spark."
            ),
            "columnas": ["Departamento", "Año", "Total"],
            "campos": ["departamento", "anio", "total"],
        },
        {
            "id": "arma_zona_top10",
            "label": "Análisis 02",
            "titulo": "Top 10 — Arma y Zona",
            "descripcion": (
                "Diez combinaciones de arma/medio y zona con mayor frecuencia. "
                "Esta operación se usa como base de la comparación de tiempos Spark vs Pandas."
            ),
            "columnas": ["Arma / Medio", "Zona", "Total"],
            "campos": ["arma_medio", "zona", "total"],
        },
        {
            "id": "tendencia_mensual",
            "label": "Análisis 03",
            "titulo": "Tendencia Mensual",
            "descripcion": "Evolución cronológica mes a mes del volumen de homicidios procesada con Spark.",
            "columnas": ["Año", "Mes", "Total"],
            "campos": ["anio", "mes", "total"],
        },
        {
            "id": "top_municipios",
            "label": "Análisis 04",
            "titulo": "Top 20 Municipios",
            "descripcion": "Municipios con mayor acumulado histórico de homicidios según el dataset completo.",
            "columnas": ["Municipio", "Departamento", "Total"],
            "campos": ["municipio", "departamento", "total"],
        },
    ],
}
