from dash import Dash, html, dcc, dash_table, Input, Output
from matriz import matriz_tarifas, valores_posibles


duraciones, años_inicio = valores_posibles()

df = matriz_tarifas(duracion=duraciones[4], año_inicio=años_inicio[4])


app = Dash(__name__, suppress_callback_exceptions=True)
server = app.server

app.layout = html.Div(
    children=[
    html.H1("Matriz de precios UNR",style={'textAlign': 'center'}),
    html.Div([
        html.Label("Selecciona la duración del contrato:", style={"color": "white", "fontWeight": "bold", "marginBottom": "5px",
                                                                  "width": "30%",#'display': 'block'
                                                                  }),
        dcc.Dropdown(
            id="dropdown-duracion",
            options=[{"label": i, "value": i} for i in duraciones],
            value=duraciones[2],
            clearable=False,
            style={"width": "30%",'textAlign': 'center',"justifyContent": "center","marginBottom": "20px"}
        ),
    ], style={"display": "flex","flexDirection": "column","alignItems": "center"}),

    html.Div([
        html.Label("Selecciona el año de inicio del contrato:", style={"color": "white", "fontWeight": "bold", "marginBottom": "5px",
                                                                       "width": "30%"}),
        dcc.Dropdown(
            id="dropdown-inicio",
            options=[{"label": i, "value": i} for i in años_inicio],
            value=años_inicio[1],
            clearable=False,
            style={"width": "30%",'textAlign': 'center',"justifyContent": "center"}
        ),
    ], style={"display": "flex","flexDirection": "column","alignItems": "center"}),
    html.Hr(style={
    "border": "0",
    "height": "2px",
    "background": "linear-gradient(to right, transparent, white, transparent)",
    "margin": "30px 0"
}),
    html.Div(id="tabla-output")
              
              ]
)

### ==== CALLBACK ====
@app.callback(
    Output("tabla-output", "children"),
    Input("dropdown-duracion", "value"),
    Input("dropdown-inicio", "value")
)
def actualizar_tabla(duracion, inicio):
    
    df = matriz_tarifas(duracion=duracion, año_inicio=inicio)

    return html.Div(dash_table.DataTable(
        id="tabla-principal",
        data=df.to_dict("records"),
        columns=[{"name": col, "id": col} for col in df.columns],
        page_size=10,
        style_table={"overflowX": "auto"},
        style_cell={"textAlign": "center"},
         css=[  # aquí vinculamos a tus clases del styles.css
        {"selector": ".dash-table-container", "rule": "flex: 1;"},
        {"selector": ".mi-tabla", "rule": ""}
    ],
    ))
    
if __name__ == "__main__":
    app.run(debug=True)


################## 
# from dash import Dash, html, dcc, dash_table, Input, Output
# import pandas as pd

# # ==== EJEMPLO DE FUNCIÓN ====
# def mi_funcion(param1, param2):
#     # Ejemplo: crear un dataframe con los parámetros
#     data = {
#         "Columna1": [f"{param1}-A", f"{param1}-B", f"{param1}-C"],
#         "Columna2": [f"{param2}-1", f"{param2}-2", f"{param2}-3"]
#     }
#     return pd.DataFrame(data)


# # ==== APP DASH ====
# app = Dash(__name__)

# # Opciones de ejemplo para los dropdown
# opciones_param1 = [i for i in range(1,3)]
# opciones_param2 = ["X", "Y", "Z"]

# app.layout = html.Div([
#     html.H2("App con 2 parámetros y DataFrame resultante"),

#     html.Label("Selecciona Param1:"),
#     dcc.Dropdown(
#         id="dropdown-param1",
#         options=[{"label": i, "value": i} for i in opciones_param1],
#         value=opciones_param1[0],   # valor inicial
#         clearable=False
#     ),

#     html.Label("Selecciona Param2:"),
#     dcc.Dropdown(
#         id="dropdown-param2",
#         options=[{"label": i, "value": i} for i in opciones_param2],
#         value=opciones_param2[0],   # valor inicial
#         clearable=False
#     ),

#     html.Hr(),

#     html.Div(id="tabla-output")
# ])


# # ==== CALLBACK ====
# @app.callback(
#     Output("tabla-output", "children"),
#     Input("dropdown-param1", "value"),
#     Input("dropdown-param2", "value")
# )
# def actualizar_tabla(param1, param2):
#     df = mi_funcion(param1, param2)

#     return dash_table.DataTable(
#         data=df.to_dict("records"),
#         columns=[{"name": col, "id": col} for col in df.columns],
#         page_size=10,
#         style_table={"overflowX": "auto"},
#         style_cell={"textAlign": "center"}
#     )


# if __name__ == "__main__":
#     app.run(debug=True)

