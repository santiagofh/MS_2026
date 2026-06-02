import os
import pandas as pd
from datetime import datetime

base_dir = r"D:\DATA\REM\REM_2026\Datos"

path_REM_A = os.path.join(base_dir, "SerieA2026.csv")
path_REM_BM = os.path.join(base_dir, "SerieBM2026.csv")
path_REM_BS = os.path.join(base_dir, "SerieBS2026.csv")
path_REM_D = os.path.join(base_dir, "SerieP2026.csv")
path_REM_P = os.path.join(base_dir, "SerieP2026.csv")

def obtener_fecha_corte(ruta_archivo):
    if os.path.exists(ruta_archivo):
        timestamp = os.path.getmtime(ruta_archivo)
        fecha = datetime.fromtimestamp(timestamp)
        return fecha.strftime("%Y-%m-%d")
    return "No disponible"


fecha_corte_REM_A = obtener_fecha_corte(path_REM_A)
fecha_corte_REM_BM = obtener_fecha_corte(path_REM_BM)
fecha_corte_REM_BS = obtener_fecha_corte(path_REM_BS)
fecha_corte_REM_D = obtener_fecha_corte(path_REM_D)
fecha_corte_REM_P = obtener_fecha_corte(path_REM_P)

rem_list = ["REM A", "REM BM", "REM BS", "REM D", "REM P"]
fechas = [
    fecha_corte_REM_A,
    fecha_corte_REM_BM,
    fecha_corte_REM_BS,
    fecha_corte_REM_D,
    fecha_corte_REM_P
]

df_corte = pd.DataFrame({
    "REM": rem_list,
    "Fecha_corte": fechas
})

df_corte.to_csv('Fecha_corte_REM.csv', index=False)
