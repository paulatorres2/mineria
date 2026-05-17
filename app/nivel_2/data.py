NIVEL_DATA: dict = {
    "numero": "02",
    "titulo": "Conocimiento Multidimensional",
    "herramienta": "Modelo Estrella",
    "descripcion": (
        "Modelado OLAP mediante un esquema estrella con tablas de hechos y dimensiones. "
        "Permite realizar consultas analíticas cruzando variables como tiempo, región, "
        "tipo de crimen y características de la víctima para descubrir relaciones no evidentes."
    ),
    "color_tag": "Nivel 2 — Multidimensional",

    "semma": [
        {
            "fase": "Sample",
            "descripcion": "Hasta 500 000 registros extraídos de la API pública datos.gov.co vía Socrata JSON.",
        },
        {
            "fase": "Explore",
            "descripcion": "Distribución por departamento, arma, sexo y fecha; detección de valores nulos.",
        },
        {
            "fase": "Modify",
            "descripcion": "Normalización en cuatro dimensiones y tabla de hechos; casteo de tipos y nulos.",
        },
        {
            "fase": "Model",
            "descripcion": "Consultas OLAP sobre el esquema estrella: agrupaciones y tendencias cruzadas.",
        },
        {
            "fase": "Assess",
            "descripcion": "Interpretación de patrones regionales, tendencia temporal y perfiles de víctima.",
        },
    ],

    "dimensiones": [
        {
            "nombre": "dim_tiempo",
            "color_class": "dim--tiempo",
            "campos": ["tiempo_id (PK)", "fecha_hecho", "anio", "mes", "trimestre", "dia_semana"],
        },
        {
            "nombre": "dim_ubicacion",
            "color_class": "dim--ubicacion",
            "campos": ["ubicacion_id (PK)", "cod_depto", "departamento", "cod_muni", "municipio", "zona"],
        },
        {
            "nombre": "dim_arma",
            "color_class": "dim--arma",
            "campos": ["arma_id (PK)", "arma_medio"],
        },
        {
            "nombre": "dim_modalidad",
            "color_class": "dim--modalidad",
            "campos": ["modalidad_id (PK)", "modalidad_presunta", "sexo", "spoa_caracterizacion"],
        },
    ],

    "fact_table": {
        "nombre": "fact_homicidios",
        "campos": [
            "tiempo_id (FK)",
            "ubicacion_id (FK)",
            "arma_id (FK)",
            "modalidad_id (FK)",
            "cantidad",
        ],
    },

    "consultas": [
        {
            "id": "por_departamento_anio",
            "label": "Consulta 01",
            "titulo": "Homicidios por Departamento y Año",
            "descripcion": "Sumatoria de casos agrupados por región y año calendario, ordenados de más reciente a más antiguo.",
            "columnas": ["Departamento", "Año", "Total"],
            "campos": ["departamento", "anio", "total"],
        },
        {
            "id": "arma_zona_top10",
            "label": "Consulta 02",
            "titulo": "Top 10 — Arma y Zona",
            "descripcion": "Las diez combinaciones de arma/medio y zona (urbana/rural) con mayor número de homicidios.",
            "columnas": ["Arma / Medio", "Zona", "Total"],
            "campos": ["arma_medio", "zona", "total"],
        },
        {
            "id": "tendencia_mensual",
            "label": "Consulta 03",
            "titulo": "Tendencia Mensual",
            "descripcion": "Evolución mes a mes del volumen de homicidios en orden cronológico.",
            "columnas": ["Año", "Mes", "Total"],
            "campos": ["anio", "mes", "total"],
        },
        {
            "id": "sexo_modalidad_top15",
            "label": "Consulta 04",
            "titulo": "Top 15 — Sexo y Modalidad",
            "descripcion": "Los quince perfiles de víctima más frecuentes cruzando sexo y modalidad presunta del homicidio.",
            "columnas": ["Sexo", "Modalidad Presunta", "Total"],
            "campos": ["sexo", "modalidad_presunta", "total"],
        },
    ],
}
