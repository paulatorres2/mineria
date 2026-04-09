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
        {
            "icono": "🏨",
            "titulo": "Hoteles y cadenas hoteleras",
            "descripcion": "Pierden ingresos por habitaciones no ocupadas y deben aplicar overbooking riesgoso.",
        },
        {
            "icono": "👤",
            "titulo": "Huéspedes",
            "descripcion": "Son reubicados por overbooking, afectando su experiencia y confianza.",
        },
        {
            "icono": "✈️",
            "titulo": "Agencias de viaje y OTAs",
            "descripcion": "Booking.com, Expedia y similares ven afectados sus modelos de comisión.",
        },
        {
            "icono": "👷",
            "titulo": "Personal hotelero",
            "descripcion": "Su carga laboral se planifica con base en ocupación esperada incorrecta.",
        },
    ],
    "contexto": (
        "Entre 2015 y 2017, la tasa promedio de cancelaciones en Europa superó el 40% en "
        "plataformas digitales. Con el auge de las reservas online y las políticas de cancelación "
        "gratuita, los clientes reservan en múltiples hoteles simultáneamente y cancelan al último "
        "momento. Esto genera una inestabilidad operativa y financiera enorme para los establecimientos."
    ),
    "empresa": {
        "nombre": "Hoteles de Portugal (Dataset Académico)",
        "descripcion": (
            "El dataset proviene de dos hoteles reales de Portugal: un hotel urbano en Lisboa y un "
            "resort en el Algarve. Los datos fueron anonimizados y publicados por Nuno António, "
            "Ana de Almeida y Luis Nunes (2019), luego popularizados a través de plataformas de "
            "datos abiertos."
        ),
    },
    "dataset": {
        "nombre": "Hotel Booking Demand Dataset",
        "registros": "~119,000 reservas",
        "variables": "32 columnas",
        "fuente": "Kaggle",
        "url": "https://www.kaggle.com/datasets/jessemostipak/hotel-booking-demand",
        "formato": "CSV",
        "periodo": "Julio 2015 – Agosto 2017",
    },
    "tecnicas": [
        {
            "nombre": "Clasificación",
            "desc": "Predecir si una reserva será cancelada (variable objetivo: is_canceled).",
        },
        {
            "nombre": "Clustering",
            "desc": "Segmentar perfiles de clientes con mayor propensión a cancelar.",
        },
        {
            "nombre": "Reglas de Asociación",
            "desc": (
                "Identificar patrones como reservas anticipadas + sin depósito + canal OTA → "
                "alta probabilidad de cancelación."
            ),
        },
        {
            "nombre": "Series Temporales",
            "desc": "Detectar épocas del año con mayor tasa de cancelación.",
        },
    ],
}
