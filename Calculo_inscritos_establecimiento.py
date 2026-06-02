import pandas as pd

path_fonasa = r"C:\Users\fariass\OneDrive - SUBSECRETARIA DE SALUD PUBLICA\SEREMIRM - Estadistica\A Estadisticas Sanitarias y Demograficas\POBLACIONES\INSCRITOS\Datos FONASA\Inscritos 2025 (Base pago 2026)\T9626 Inscritos APS RM.xlsx"

fonasa1 = pd.read_excel(path_fonasa, sheet_name='Municipales', skiprows=3)
fonasa2 = pd.read_excel(path_fonasa, sheet_name='ONG', skiprows=3)
fonasa3 = pd.read_excel(path_fonasa, sheet_name='Servicio de Salud', skiprows=3)

fonasa = pd.concat([fonasa1, fonasa2, fonasa3], ignore_index=True)

sexo_map = {"Mujer": "Mujeres", "Hombre": "Hombres", "Indeterminado": "Sin informaci\u00f3n"}
if 'Sexo' in fonasa.columns:
    fonasa['Sexo'] = fonasa['Sexo'].replace(sexo_map)

ss_rm = [
    'Metropolitano Central', 'Metropolitano Norte', 'Metropolitano Occidente',
    'Metropolitano Oriente', 'Metropolitano Sur', 'Metropolitano Sur Oriente', 'Metropolitano Central'
]
fonasa_rm = fonasa.loc[fonasa['Servicio de Salud'].isin(ss_rm)].copy()


def sumar_denominador_fonasa(
    fonasa_rm,
    edades=None,
    sexo=None,
    prevalencias=None
):
    df_final_list = []

    df_fon = fonasa_rm.copy()

    if sexo is not None:
        df_fon = df_fon[df_fon['Sexo'].isin(sexo)]

    if edades is not None:
        if prevalencias is not None and len(prevalencias) == len(edades):
            for i, rango_edad in enumerate(edades):
                tmp = df_fon[df_fon['Edad'].isin(rango_edad)].copy()
                tmp['Inscritos'] = tmp['Inscritos'] * prevalencias[i]
                df_final_list.append(tmp)
            df_concat = pd.concat(df_final_list, ignore_index=True)
        else:
            df_concat = df_fon[df_fon['Edad'].isin(edades[0])]
    else:
        df_concat = df_fon

    df_group = df_concat.groupby('C\u00f3digo Centro')['Inscritos'].sum().reset_index()

    df_group = df_group.rename(columns={
        'C\u00f3digo Centro': 'IdEstablecimiento',
        'Inscritos': 'Inscritos_suma_fonasa'
    })

    return df_group


ms2 = sumar_denominador_fonasa(
    fonasa_rm=fonasa_rm,
    edades=[range(25, 65)],
    sexo=["Mujeres"]
)

ms3a = sumar_denominador_fonasa(
    fonasa_rm=fonasa_rm,
    edades=[range(0, 10)],
    sexo=None,
    prevalencias=None
)

ms3b = sumar_denominador_fonasa(
    fonasa_rm=fonasa_rm,
    edades=[range(6, 7)],
    sexo=None,
    prevalencias=None
)

ms4a = sumar_denominador_fonasa(
    fonasa_rm=fonasa_rm,
    edades=[range(15, 25), range(25, 45), range(45, 65), range(65, 200)],
    sexo=None,
    prevalencias=[0.018, 0.063, 0.183, 0.306]
)

ms5 = sumar_denominador_fonasa(
    fonasa_rm=fonasa_rm,
    edades=[range(15, 25), range(25, 45), range(45, 65), range(65, 200)],
    sexo=None,
    prevalencias=[0.007, 0.106, 0.451, 0.733]
)

ms7 = sumar_denominador_fonasa(
    fonasa_rm=fonasa_rm,
    edades=[range(40, 120), range(5, 40)],
    sexo=None,
    prevalencias=[0.117, 0.10]
)

lista_ms = [
    (ms2, "II"),
    (ms3a, "IIIa"),
    (ms3b, "IIIb"),
    (ms4a, "IVa"),
    (ms5, "V"),
    (ms7, "VII")
]

df_final = pd.concat(
    [df.assign(MS=etiqueta) for df, etiqueta in lista_ms],
    ignore_index=True
)[["IdEstablecimiento", "MS", "Inscritos_suma_fonasa"]]

df_final.to_csv("data/ms_fonasa.csv", index=False)
