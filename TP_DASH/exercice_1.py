import dash
from dash import html
import dash_bootstrap_components as dbc

# Création de l'application avec un thème Bootstrap
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Dashboard de ventes",
                        className="text-center text-primary mt-4 mb-2"))
    ]),
    dbc.Row([
        dbc.Col(html.P(
            "Fil rouge : nous allons enrichir ce dashboard étape par étape.",
            className="text-center mb-4"
        ))
    ]),
    # Zone principale (que l'on remplira dans les exercices suivants)
    dbc.Row([
        dbc.Col(html.Div("Contenu à venir...", id="main-content"))
    ])
], fluid=True)

if __name__ == "__main__":
    app.run(debug=True)
