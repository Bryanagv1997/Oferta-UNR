## ----------------
## Librerías
## ----------------
from db_utils import LeerTabla
import pandas as pd

## -- Se obtiene la tabla de horarios desde la DB PostgreSQL 
df  = LeerTabla(tabla="horario")
df_filtrado = df[df["modalidad"] == "Compra"]
df_filtrado['año'] = df_filtrado['periodo'].dt.year

## ----------------
## Obtener los PPP de compra de Santa Fe
## ----------------

promedio_ponderado = (
    df_filtrado.groupby('año')
    .apply(lambda x: round((x['GWh'] * x['tarifa']).sum() / x['GWh'].sum(),2))
    .reset_index(name='PPP')
)

## ------------ 
## Procesamiento 
## ------------ 

## -- Leer la curva de consumo del usuario. NOTA: El formato debe ser una tabla con 2 columnas. Una indicando la hora y otra el consumo en kWh.
## NOTA: Teniendo en cuenta la curva tipica del cliente se halla el coeficiente de variación y relativo con reglas del 30%

df_demanda = pd.read_csv("matriz_unr.csv").iloc[:23,:2]  ### Garantizar que se leen 24 filas (0-23 horas) y 2 columnas (hora y consumo kWh)

columnas_esperadas = ["hora","consumo"]

try:
    df_demanda.columns = columnas_esperadas
except Exception as e:
    print("❌ El archivo de consumo no tiene el formato esperado.")


def clasificar_perfil(cv, cr):
    """
    Clasifica el tipo de curva energética según el Coeficiente de Variación (cv)
    y el Coeficiente Relativo (cr).

    Reglas:
    - Si CV y CR son <0.05 → 'Plano'
    - Si uno de los dos es menor a 0.3 → 'Piso'
    - Si ambos son mayores a 0.3 → 'Techo'
    """
    if cv <= 0.05 and cr <= 0.05:
        return "Plano"
    elif cv < 0.3 or cr < 0.3:
        return "Piso"
    elif cv > 0.3 and cr > 0.3:
        return "Techo"
    else:
        return "Indefinido"
#### Los años que yo quiero que mi usuario se contrate
def filtrar_periodo_contrato(df, año_inicial, duracion_contrato):
    '''Función para obtener el DF con los años que el usuario quiere contratar.'''
    año_final = año_inicial + duracion_contrato - 1
    df.rename(columns={"PPP": "PPP G base"},inplace=True)
    df_filtrado = df[(df['año'] >= año_inicial) & (df['año'] <= año_final)]
    return df_filtrado


#### Hallo los AOM actuales de SFEC
def agregar_columna_ipc(df, ipc_base=0.0482, incremento_extra=0.05, valor_inicial=290, nombre_columna="Gastos SFEC"):
    """
    Agrega una columna al DataFrame que aumenta cada año según IPC + incremento adicional para los gastos de SFEC.

    Parámetros:
    - df: DataFrame con columna 'año'
    - ipc_base: IPC anual estimado (ej: 0.0482 para 4.82%)
    - incremento_extra: Porcentaje adicional (ej: 0.05 para 5%)
    - valor_inicial: Valor base para el primer año 290 MCOP --> Estos son aproximadamente los AOM actuales de SFEC para 2025.
    - nombre_columna: Nombre de la nueva columna (nómina + gastos adminstrativos de SFE)
    Retorna:
    - DataFrame con la nueva columna agregada
    """
    tasa_total = ipc_base + incremento_extra
    años = df['año'].sort_values().unique()
    ### Se le suma (2) dos pesos para tener un valor agregado de costos SIC y CND 
    valores = {año: round((valor_inicial) * ((1 + tasa_total) ** i), 2) for i, año in enumerate(años)}
    df[nombre_columna] = df['año'].map(valores)
    df['AOM+SIC'] = round(df[nombre_columna]*12/df['GWh'],2) + 2
    return df


def aplicar_ajuste(df, columna_valores, tipo_curva):
    """
    Aplica ajustes económicos sobre la columna seleccionada según el tipo de curva.

    Reglas:
    - Si tipo_curva es 'Piso': se aplica 10% de ganancia → valor * 1.10
    - Si es 'Plano': se descuenta 1% sobre el resultado que tendría 'Piso' → valor * 1.10 * 0.99
    - Si es 'Techo': se incrementa 1% sobre el resultado que tendría 'Piso' → valor * 1.10 * 1.01

    Parámetros:
    - df: DataFrame que contiene la columna de valores
    - columna_valores: str, nombre de la columna a ajustar
    - tipo_curva: str, puede ser 'Piso', 'Plano' o 'Techo'

    Retorna:
    - DataFrame con una nueva columna 'Ajuste económico'
    """

    # Valor base ajustado por tipo
    if tipo_curva == "Piso":
        factor = 1.10  ## ganar un 10% sobre el valor de compra de la energia (incluodos costos AOM y SIC)
    elif tipo_curva == "Plano":
        factor = 1.10 * 0.99  # descuento del 1% sobre el piso
    elif tipo_curva == "Techo":
        factor = 1.10 * 1.01  # recargo del 1% sobre el piso
    else:
        raise ValueError("Tipo de curva inválido. Usa 'Piso', 'Plano' o 'Techo'.")

    # Aplicar el ajuste a la columna
    df["PPP G venta"] = round(df[columna_valores] * factor,2)

    return df


## -- Este DF ajusta la tarifa segun la curva de demanda.
# df_ajustado = aplicar_ajuste(df_G, "PPP G compra", tipo_curva=clasificar_perfil(cv, cr))

## Ana Gabriela propuso 3 categorias de volumenes: 55-300 MW, 300-700 MW, >700 MW

volumenes_anteriores = [55, 110, 220, 440, 880]
volumenes_nuevos = [55, 300, 700]  # Nuevos rangos propuestos

## Se tiene tasa de fildelidad del 0.15% y de volumen del 0.10%. --> Se ajusta a 0.2% debido a menores categorias de volumenes

def generar_tasas_fidelidad_volumen(años=range(3, 11), volumenes=volumenes_nuevos, tasa_fidelidad_base=0.0015, tasa_volumen_base=0.0020):
    """
    Crea un DataFrame con tasas de fidelidad y volumen que crecen proporcionalmente.

    - Fidelidad: de 0% en año 3 y voy creciendo de 0.15% por año.
    - Volumen: se duplica por cada rango, empezando en 0% para el primer.

    Retorna:
    - DataFrame DE TASAS con columnas: 'Año', 'Tasa Fidelidad (%)', 'Rango Volumen', 'Tasa Volumen (%)'
    """
    filas = []
    años_lista = list(años)
    # total_periodos = len(años_lista) - 1  # 7 para años 3–10

    for i, año in enumerate(años_lista):
        tasa_fidelidad = round((i ) * tasa_fidelidad_base, 5) if i > 0 else 0

        for j, vol_min in enumerate(volumenes):
            vol_max = volumenes[j + 1] if j + 1 < len(volumenes) else "∞"
            rango = f"{vol_min}-{vol_max}" if vol_max != "∞" else f">{vol_min}"
            tasa_volumen = round(tasa_volumen_base * (j) if j > 0 else 0, 5)

            filas.append({
                "Año": año,
                "Tasa Fidelidad (%)": round(tasa_fidelidad * 100, 2),
                "Rango Volumen": rango,
                "Tasa Volumen (%)": round(tasa_volumen * 100, 2)
            })
    df_tasas = pd.DataFrame(filas)
    df_tasas["Tasa Total (%)"] = round(df_tasas["Tasa Fidelidad (%)"] + df_tasas["Tasa Volumen (%)"],2)
    return df_tasas

df_tasas = generar_tasas_fidelidad_volumen()
rangos = df_tasas["Rango Volumen"].unique()

## -- Calcular el rango de volumen
def rango_consumo_cliente(df_demanda):
    volumen_mensual = df_demanda["consumo"].sum()*30/1000 ## Estimar el consumo a 30 días en MWh
    if volumen_mensual<300:
        rango_cliente = rangos[0]
    elif volumen_mensual < 700:
        rango_cliente = rangos[1]
    else:
        rango_cliente = rangos[2]
    return rango_cliente

def matriz_tarifas(duracion, año_inicio, df_curva=df_demanda):
    '''Función general para calcular la matriz de precios basada en duración, año de inicio y consumo del usuario

        Esta será la entrada para la APP Dash.
    
    '''
    
    df_base = filtrar_periodo_contrato(promedio_ponderado, año_inicio, duracion)
    gastos=agregar_columna_ipc(df_filtrado.groupby("año")[['GWh']].sum().reset_index())
    df_unido = pd.merge(df_base, gastos, on='año', how='inner')
    
    ## Curva consumo
    media = df_curva['consumo'].mean()
    desviacion = df_curva['consumo'].std()
    maximo = df_curva['consumo'].max()
    minimo = df_curva['consumo'].min()

    cv = desviacion/media
    cr = (maximo - minimo)/media
    
    gastos=agregar_columna_ipc(df_filtrado.groupby("año")[['GWh']].sum().reset_index())
    df_unido = pd.merge(df_base, gastos, on='año', how='inner')

    columnas_deseadas = ['año', 'PPP G base', 'AOM+SIC']
    df_G = df_unido[columnas_deseadas]
    df_G ["PPP G compra"]=round(df_G["PPP G base"] + df_G["AOM+SIC"],2)
    
    ## -- Este DF ajusta la tarifa segun la curva de demanda.
    df_ajustado = aplicar_ajuste(df_G, "PPP G compra", tipo_curva=clasificar_perfil(cv, cr))
    
    df_tasas = generar_tasas_fidelidad_volumen()
    # rangos = df_tasas["Rango Volumen"].unique()
    
    ## -- Filtrar el DF de tasas segun la duracion del contrato y el rango de columen del cliente
    fila_seleccionada = df_tasas[(df_tasas["Año"] == duracion) 
                                 & (df_tasas["Rango Volumen"] == rango_consumo_cliente(df_demanda))]
    
    ## -- Añadir las tasas al DF ajustado (que ya toma en cuenta la curva de consumo)
    df_ajustado["Tasa de descuento (%)"]=fila_seleccionada["Tasa Total (%)"].values[0]
    
    ## -- Ajustar los precios de venta con la tasa de descuento.
    df_ajustado["PPP G venta con descuento"] =round((100-df_ajustado['Tasa de descuento (%)'])*df_ajustado['PPP G venta']/100,2)
    
    return df_ajustado

def valores_posibles():
    duraciones = [i for i in range(1,promedio_ponderado["año"].shape[0]+1) if i<=10]
    años_inicio = promedio_ponderado["año"].unique()
    return duraciones, años_inicio