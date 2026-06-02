import os
import pandas as pd

directory_2025 = r"D:\DATA\REM\REM_2025"
directory_2026 = r"D:\DATA\REM\REM_2026"

all_codes = [
    "02010420",
    "03500366",
    "02010321",
    "03500331",
    "03500334",
    "P1206010",
    "P1206020",
    "P1206030",
    "P1206040",
    "P1206050",
    "P1206060",
    "P1206070",
    "P1206080",
    "03500364",
    "03500365",
    "09220100",
    "P4180300",
    "P4200200",
    "P4190809",
    "P4170300",
    "P4190500",
    "P4190600",
    "P4150602",
    "P4180200",
    "P4200100",
    "A0200002",
    "A0200001",
    "P3161041",
    "P3161045"
]


def leer_y_filtrar_archivos(directorio, all_codes, sep=";", chunksize=1000):
    datos_filtrados = []
    datos_dir = os.path.join(directorio, "Datos")

    if not os.path.isdir(datos_dir):
        print(f"Advertencia: No se encuentra la carpeta Datos en {directorio}")
        return pd.DataFrame()

    for filename in os.listdir(datos_dir):
        if filename.endswith(".csv") or filename.endswith(".txt"):
            filepath = os.path.join(datos_dir, filename)
            for chunk in pd.read_csv(filepath, sep=sep, chunksize=chunksize):
                filtered_chunk = chunk[chunk['CodigoPrestacion'].isin(all_codes)]
                datos_filtrados.append(filtered_chunk)

    if datos_filtrados:
        return pd.concat(datos_filtrados, ignore_index=True)
    else:
        return pd.DataFrame()


leer = True
if leer:
    df_rem_2026 = leer_y_filtrar_archivos(directory_2026, all_codes)
    df_rem_2025 = leer_y_filtrar_archivos(directory_2025, all_codes)

path_deis = r"D:\DATA\ESTABLECIMIENTOS\Establecimientos DEIS MINSAL 30-01-2026.xlsx"
df_deis = pd.read_excel(path_deis, skiprows=1)

df_deis = df_deis.rename(columns={
    'Código Vigente': 'IdEstablecimiento',
    'Código Dependencia Jerárquica (SEREMI / Servicio de Salud)': 'IdServicio',
    'Código Región': 'IdRegion',
    'IdComuna': 'Código Comuna'
})

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

region_id = 13


def sumar_columnas_por_establecimiento(df, codigos, columnas_sumar, region_id):
    cols_grup = ['IdEstablecimiento', 'Ano', 'Mes']
    df_filt = df.loc[
        (df['CodigoPrestacion'].isin(codigos)) &
        (df['IdRegion'] == region_id)
    ].copy()

    for col in columnas_sumar:
        if col not in df_filt.columns:
            df_filt[col] = 0

    df_filt[columnas_sumar] = df_filt[columnas_sumar].fillna(0)

    df_grouped = df_filt.groupby(cols_grup)[columnas_sumar].sum().reset_index()

    df_grouped['suma'] = df_grouped[columnas_sumar].sum(axis=1)

    return df_grouped[cols_grup + ['suma']]


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

    df_group = df_concat.groupby('Código Centro')['Inscritos'].sum().reset_index()

    df_group = df_group.rename(columns={
        'Código Centro': 'IdEstablecimiento',
        'Inscritos': 'Inscritos_suma_fonasa'
    })

    return df_group


def calcular_MSI(df_rem_2025, df_rem_2026, region_id):
    df_2025_oct_to_dec = df_rem_2025.loc[df_rem_2025['Mes'] >= 10].copy()
    df_2026_jan_to_sep = df_rem_2026.loc[df_rem_2026['Mes'] <= 9].copy()
    df_combined = pd.concat([df_2025_oct_to_dec, df_2026_jan_to_sep], ignore_index=True)

    df_num = sumar_columnas_por_establecimiento(
        df=df_combined,
        codigos=["02010420", "03500366"],
        columnas_sumar=["Col08", "Col09", "Col10", "Col11"],
        region_id=region_id
    )
    df_num = df_num.rename(columns={'suma': 'Numerador_MSI'})

    df_den = sumar_columnas_por_establecimiento(
        df=df_combined,
        codigos=["02010321", "03500334", "03500331"],
        columnas_sumar=["Col08", "Col09", "Col10", "Col11"],
        region_id=region_id
    )
    df_den = df_den.rename(columns={'suma': 'Denominador_MSI'})

    df_merge = pd.merge(
        df_num,
        df_den,
        on=['IdEstablecimiento', 'Ano', 'Mes'],
        how='outer'
    )

    return df_merge


def calcular_MSII(df_rem, fonasa_rm, region_id):
    df_num = sumar_columnas_por_establecimiento(
        df=df_rem,
        codigos=[
            "P1206010", "P1206020", "P1206030", "P1206040", "P1206050",
            "P1206060", "P1206070", "P1206080"
        ],
        columnas_sumar=["Col01", "Col02"],
        region_id=region_id
    )
    df_num = df_num.rename(columns={'suma': 'Numerador_MSII'})

    df_den_fona = sumar_denominador_fonasa(
        fonasa_rm=fonasa_rm,
        edades=[range(25, 65)],
        sexo=["Mujeres"]
    )
    df_den_fona = df_den_fona.rename(columns={'Inscritos_suma_fonasa': 'Denominador_MSII'})

    df_merge = pd.merge(df_num, df_den_fona,
                        on='IdEstablecimiento',
                        how='outer')
    return df_merge


def calcular_MSIIIa(df_rem, fonasa_rm, region_id):
    cols_numerador = [
        "Col04", "Col05", "Col06", "Col07", "Col08", "Col09", "Col10", "Col11",
        "Col12", "Col13", "Col14", "Col15", "Col16", "Col17", "Col18", "Col19",
        "Col20", "Col21", "Col22", "Col23"
    ]
    df_num = sumar_columnas_por_establecimiento(
        df=df_rem,
        codigos=["03500364", "03500365"],
        columnas_sumar=cols_numerador,
        region_id=region_id
    )
    df_num = df_num.rename(columns={'suma': 'Numerador_MSIIIa'})

    df_den_fona = sumar_denominador_fonasa(
        fonasa_rm=fonasa_rm,
        edades=[range(0, 10)],
        sexo=None,
        prevalencias=None
    )
    df_den_fona = df_den_fona.rename(columns={'Inscritos_suma_fonasa': 'Denominador_MSIIIa'})

    df_merge = pd.merge(df_num, df_den_fona,
                        on='IdEstablecimiento',
                        how='outer')
    return df_merge


def calcular_MSIIIb(df_rem, fonasa_rm, region_id):
    df_num = sumar_columnas_por_establecimiento(
        df=df_rem,
        codigos=["09220100"],
        columnas_sumar=["Col16", "Col17"],
        region_id=region_id
    )
    df_num = df_num.rename(columns={'suma': 'Numerador_MSIIIb'})

    df_den_fona = fonasa_rm.copy()
    df_den_fona = df_den_fona[df_den_fona['Edad'] == 6]
    df_den_fona_group = df_den_fona.groupby('Código Centro')['Inscritos'].sum().reset_index()
    df_den_fona_group = df_den_fona_group.rename(columns={
        'Código Centro': 'IdEstablecimiento',
        'Inscritos': 'Denominador_MSIIIb'
    })

    df_merge = pd.merge(df_num, df_den_fona_group,
                        on='IdEstablecimiento',
                        how='outer')
    return df_merge


def calcular_MSIVa(df_rem, fonasa_rm, region_id):
    df_num = sumar_columnas_por_establecimiento(
        df=df_rem,
        codigos=["P4180300", "P4200200"],
        columnas_sumar=["Col01"],
        region_id=region_id
    )
    df_num = df_num.rename(columns={'suma': 'Numerador_MSIVa'})

    edades_list = [range(15, 25), range(25, 45), range(45, 65), range(65, 200)]
    prevalencias_list = [0.018, 0.063, 0.183, 0.306]
    df_den_fona = sumar_denominador_fonasa(
        fonasa_rm=fonasa_rm,
        edades=edades_list,
        sexo=None,
        prevalencias=prevalencias_list
    )
    df_den_fona = df_den_fona.rename(columns={'Inscritos_suma_fonasa': 'Denominador_MSIVa'})

    df_merge = pd.merge(df_num, df_den_fona,
                        on='IdEstablecimiento',
                        how='outer')
    return df_merge


def calcular_MSIVb(df_rem, region_id):
    df_num = sumar_columnas_por_establecimiento(
        df=df_rem,
        codigos=["P4190809", "P4170300", "P4190500", "P4190600"],
        columnas_sumar=["Col01"],
        region_id=region_id
    )
    df_num = df_num.rename(columns={'suma': 'Numerador_MSIVb'})

    df_den = sumar_columnas_por_establecimiento(
        df=df_rem,
        codigos=["P4150602"],
        columnas_sumar=["Col01"],
        region_id=region_id
    )
    df_den = df_den.rename(columns={'suma': 'Denominador_MSIVb'})

    df_merge = pd.merge(df_num, df_den,
                        on=['IdEstablecimiento', 'Ano', 'Mes'],
                        how='outer')
    return df_merge


def calcular_MSV(df_rem, fonasa_rm, region_id):
    df_num = sumar_columnas_por_establecimiento(
        df=df_rem,
        codigos=["P4180200", "P4200100"],
        columnas_sumar=["Col01"],
        region_id=region_id
    )
    df_num = df_num.rename(columns={'suma': 'Numerador_MSV'})

    edades_list = [range(15, 25), range(25, 45), range(45, 65), range(65, 200)]
    prevalencias_list = [0.007, 0.106, 0.451, 0.733]
    df_den_fona = sumar_denominador_fonasa(
        fonasa_rm=fonasa_rm,
        edades=edades_list,
        sexo=None,
        prevalencias=prevalencias_list
    )
    df_den_fona = df_den_fona.rename(columns={'Inscritos_suma_fonasa': 'Denominador_MSV'})

    df_merge = pd.merge(df_num, df_den_fona,
                        on='IdEstablecimiento',
                        how='outer')
    return df_merge


def calcular_MSVI(df_rem, region_id):
    df_num = sumar_columnas_por_establecimiento(
        df=df_rem,
        codigos=["A0200002"],
        columnas_sumar=["Col06"],
        region_id=region_id
    )
    df_num = df_num.rename(columns={'suma': 'Numerador_MSVI'})

    df_den = sumar_columnas_por_establecimiento(
        df=df_rem,
        codigos=["A0200001"],
        columnas_sumar=["Col06"],
        region_id=region_id
    )
    df_den = df_den.rename(columns={'suma': 'Denominador_MSVI'})

    df_merge = pd.merge(df_num, df_den,
                        on=['IdEstablecimiento', 'Ano', 'Mes'],
                        how='outer')
    return df_merge


def calcular_MSVII(df_rem, fonasa_rm, region_id):
    cols_1 = [f"Col{str(i).zfill(2)}" for i in range(6, 38)]
    df_num1 = sumar_columnas_por_establecimiento(
        df=df_rem,
        codigos=["P3161041"],
        columnas_sumar=cols_1,
        region_id=region_id
    )
    df_num1 = df_num1.rename(columns={'suma': 'temp1'})

    df_num2 = sumar_columnas_por_establecimiento(
        df=df_rem,
        codigos=["P3161045"],
        columnas_sumar=["Col01"],
        region_id=region_id
    )
    df_num2 = df_num2.rename(columns={'suma': 'temp2'})

    df_numerador = pd.merge(df_num1, df_num2,
                            on=['IdEstablecimiento', 'Ano', 'Mes'],
                            how='outer')
    df_numerador[['temp1', 'temp2']] = df_numerador[['temp1', 'temp2']].fillna(0)
    df_numerador['Numerador_MSVII'] = df_numerador['temp1'] + df_numerador['temp2']
    df_numerador = df_numerador.drop(columns=['temp1', 'temp2'])

    # ATENCION: range(5, 200) incluye a personas >=40 anios, solapando con range(40, 200).
    # Eso duplica el conteo de 40-119 anios, inflando el denominador ~46%.
    # La prevalencia 0.10 corresponde solo a 5-39 anios. Corregido respecto a 2025.
    edades_list = [range(40, 200), range(5, 40)]
    prevalencias_list = [0.117, 0.10]
    df_den_fona = sumar_denominador_fonasa(
        fonasa_rm=fonasa_rm,
        edades=edades_list,
        sexo=None,
        prevalencias=prevalencias_list
    )
    df_den_fona = df_den_fona.rename(columns={'Inscritos_suma_fonasa': 'Denominador_MSVII'})

    df_merge = pd.merge(df_numerador, df_den_fona,
                        on='IdEstablecimiento',
                        how='outer')

    registros_extra = []
    for establecimiento in df_merge['IdEstablecimiento'].unique():
        if not ((df_merge['IdEstablecimiento'] == establecimiento) & (df_merge['Mes'] == 12)).any():
            denominador = df_merge.loc[df_merge['IdEstablecimiento'] == establecimiento, 'Denominador_MSVII'].values[0]
            ano = df_merge.loc[df_merge['IdEstablecimiento'] == establecimiento, 'Ano'].values[0]

            registros_extra.append({
                'IdEstablecimiento': establecimiento,
                'Ano': ano,
                'Mes': 12,
                'Numerador_MSVII': 0,
                'Denominador_MSVII': denominador
            })

    df_extra = pd.DataFrame(registros_extra)
    df_final = pd.concat([df_merge, df_extra], ignore_index=True)
    return df_final


df_MSI = calcular_MSI(df_rem_2025, df_rem_2026, region_id)
df_MSII = calcular_MSII(df_rem_2026, fonasa_rm, region_id)
df_MSIIIa = calcular_MSIIIa(df_rem_2026, fonasa_rm, region_id)
df_MSIIIb = calcular_MSIIIb(df_rem_2026, fonasa_rm, region_id)
df_MSIVa = calcular_MSIVa(df_rem_2026, fonasa_rm, region_id)
df_MSIVb = calcular_MSIVb(df_rem_2026, region_id)
df_MSV = calcular_MSV(df_rem_2026, fonasa_rm, region_id)
df_MSVI = calcular_MSVI(df_rem_2026, region_id)
df_MSVII = calcular_MSVII(df_rem_2026, fonasa_rm, region_id)


def preparar_df_final(df_in, meta_name, num_col, den_col):
    df_out = df_in.copy()
    df_out['MetaSanitaria'] = meta_name
    df_out = df_out.rename(columns={
        num_col: 'Numerador',
        den_col: 'Denominador'
    })
    for c in ['Ano', 'Mes', 'IdEstablecimiento']:
        if c not in df_out.columns:
            df_out[c] = None
    df_out = df_out[['IdEstablecimiento', 'Ano', 'Mes', 'Numerador', 'Denominador', 'MetaSanitaria']]
    return df_out


dfs_finales = []

dfs_finales.append(preparar_df_final(df_MSI, 'MSI', 'Numerador_MSI', 'Denominador_MSI'))
dfs_finales.append(preparar_df_final(df_MSII, 'MSII', 'Numerador_MSII', 'Denominador_MSII'))
dfs_finales.append(preparar_df_final(df_MSIIIa, 'MSIIIa', 'Numerador_MSIIIa', 'Denominador_MSIIIa'))
dfs_finales.append(preparar_df_final(df_MSIIIb, 'MSIIIb', 'Numerador_MSIIIb', 'Denominador_MSIIIb'))
dfs_finales.append(preparar_df_final(df_MSIVa, 'MSIVa', 'Numerador_MSIVa', 'Denominador_MSIVa'))
dfs_finales.append(preparar_df_final(df_MSIVb, 'MSIVb', 'Numerador_MSIVb', 'Denominador_MSIVb'))
dfs_finales.append(preparar_df_final(df_MSV, 'MSV', 'Numerador_MSV', 'Denominador_MSV'))
dfs_finales.append(preparar_df_final(df_MSVI, 'MSVI', 'Numerador_MSVI', 'Denominador_MSVI'))
dfs_finales.append(preparar_df_final(df_MSVII, 'MSVII', 'Numerador_MSVII', 'Denominador_MSVII'))

df_final = pd.concat(dfs_finales, ignore_index=True)

if 'Dependencia Administrativa' in df_deis.columns:
    dep_col = 'Dependencia Administrativa'
else:
    dep_col = 'DependenciaAdm'

if 'Nivel de Atención' in df_deis.columns:
    nivel_col = 'Nivel de Atención'
else:
    nivel_col = 'NivelAtencion'

cols_merge_deis = ['IdEstablecimiento', dep_col, nivel_col]
df_deis_merge = df_deis.drop_duplicates(subset=['IdEstablecimiento'])

df_final2 = pd.merge(df_final,
                     df_deis_merge[cols_merge_deis],
                     on='IdEstablecimiento',
                     how='left')

df_final2.to_csv('MS2026_v3.csv', index=False, encoding='utf-8')
print("Archivo CSV guardado exitosamente: 'MS2026_v3.csv'")
