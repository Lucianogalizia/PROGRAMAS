# pulling-app/backend/app/utils.py

import pandas as pd
import io

def parse_datasheet(content: bytes) -> pd.DataFrame:
    """
    Toma el contenido bruto de un Excel (.xls/.xlsx/.xlsm),
    busca la pestaña 'Data Sheet' y devuelve un DataFrame.
    """
    try:
        xls = pd.ExcelFile(io.BytesIO(content), engine="openpyxl")
    except Exception as e:
        raise ValueError(f"No pude abrir el Excel: {e}")

    if "Data Sheet" not in xls.sheet_names:
        raise ValueError("No encontré la pestaña 'Data Sheet' en el Excel.")

    try:
        df = xls.parse("Data Sheet")
    except Exception as e:
        raise ValueError(f"Error al parsear hoja 'Data Sheet': {e}")

    return df


