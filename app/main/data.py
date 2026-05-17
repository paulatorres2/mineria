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
        {"titulo": "Cuerpos policiales",
         "descripcion": "Necesitan distribuir patrullajes y recursos de forma inteligente para maximizar la prevención del delito."},
        {"titulo": "Alcaldías y gobiernos locales",
         "descripcion": "Son responsables de las políticas públicas de seguridad y deben justificar inversiones con datos concretos."},
        {"titulo": "Investigadores y analistas",
         "descripcion": "Requieren datos abiertos y modelos predictivos para estudiar la dinámica criminal y proponer soluciones basadas en evidencia."},
    ],
    "contexto":
    "La distribución del crimen en entornos urbanos sigue patrones espaciales y temporales identificables. Estudios de criminología ambiental demuestran que ciertos vecindarios, horarios y tipos de delito se agrupan de forma consistente. Con el crecimiento de las ciudades y la disponibilidad de datos abiertos de crimen, la minería de datos se convierte en una herramienta clave para transformar enormes volúmenes de reportes policiales en conocimiento accionable que guíe estrategias de prevención del delito.",

    "empresa": {
        "nombre": "Ministerio de Defensa Nacional - MinDefensa, Bogotá D.C.",
        "descripcion": "El Ministerio de Defensa Nacional desde el Viceministerio para las Políticas de Defensa y Seguridad Nacional, creó el Observatorio de Derechos Humanos y Defensa Nacional, con el propósito de generar datos estadísticos actualizados y oficiales que evidencian las actividades que se realizan desde el Sector Defensa para garantizar el goce efectivo de los derechos humanos de la población colombiana.",
    },

    "dataset": {
        "nombre": "HOMICIDIO",
        "registros": "334K registros",
        "variables": "11 columnas (Fecha, Departamento, Municipio, Zona, Sexo, Arma Medio, Cantidad, etc)",
        "fuente": "datos.gov",
        "url": "https://www.datos.gov.co/Seguridad-y-Defensa/HOMICIDIO/m8fd-ahd9/about_data",
        "formato": "CSV",
        "periodo": "2003 – Presente",
    },
}
