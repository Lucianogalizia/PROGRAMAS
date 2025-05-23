from pandas import DataFrame

def finalizacion(df: DataFrame) -> list:
    """
    Módulo Final: Cierre del Programa de Pulling
    – Se incluye siempre al final de cualquier programa, sin excepción.
    """
    return [
        {
            "manobra_normalizada": "VARIOS",
            "punto_programa": 58,
            "descripcion": "Tareas varias.",
            "activity_phase": "SPV",
            "activity_code": "SPV",
            "activity_subcode": "SPV",
            "tiempo": ""
        },
        {
            "manobra_normalizada": "ARMA BDP",
            "punto_programa": 59,
            "descripcion": "Armar BDP.",
            "activity_phase": "SP04",
            "activity_code": "SP15",
            "activity_subcode": "260",
            "tiempo": ""
        },
        {
            "manobra_normalizada": "DESMONTA EQUIPO",
            "punto_programa": 61,
            "descripcion": (
                "Acondicionar boca de pozo, material sobrante y locación, instalar rotador de varillas "
                "y accesorios de superficie. Desmontar. Informar a Coordinación y Sala de Monitoreo de Pulling "
                "la finalización de la intervención y transporte a próxima locación. Generar acta de entrega/recepción "
                "de locación. Indicar si el puente de producción queda armado."
            ),
            "activity_phase": "SP01",
            "activity_code": "SP11",
            "activity_subcode": "202",
            "tiempo": ""
        }
    ]
