import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# ---------- DATA ----------
data = {
    "mois":   ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin"] * 3,
    "region": ["Nord"] * 6 + ["Sud"] * 6 + ["Est"] * 6,
    "ventes": [120, 150, 130, 170, 160, 180,
               100, 110, 115, 130, 140, 150,
               90, 105, 95, 120, 125, 135],
    "annee":  [2024] * 18
}

df = pd.DataFrame(data)

# ---------- APP ----------
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])

nb_regions = df["region"].nunique()

# ---------- DROPDOWN OPTIONS ----------
regions = sorted(df["region"].unique())
options_region = [{"label": "Toutes les régions", "value": "Toutes"}] + \
    [{"label": r, "value": r} for r in regions]

# ---------- LAYOUT ----------
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Dashboard de ventes",
                        className="text-center text-primary mt-4 mb-2"))
    ]),
    dbc.Row([
        dbc.Col(html.P(
            "Fil rouge : tableau de bord des ventes 2024.",
            className="text-center mb-4"
        ))
    ]),

    # KPIs
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader("Total des ventes"),
            dbc.CardBody(html.H3(id="kpi-total", className="text-success"))
        ], className="mb-3"), md=4),

        dbc.Col(dbc.Card([
            dbc.CardHeader("Nombre de régions"),
            dbc.CardBody(html.H3(f"{nb_regions}", className="text-info"))
        ], className="mb-3"), md=4),

        dbc.Col(dbc.Card([
            dbc.CardHeader("Meilleur mois"),
            dbc.CardBody(html.H3(id="kpi-meilleur-mois", className="text-warning"))
        ], className="mb-3"), md=4),
    ], className="mb-4", id="kpi-row"),

    # DROPDOWN REGION
    dbc.Row([
        dbc.Col(
            dcc.Dropdown(
                id="dropdown-region",
                options=options_region,
                value="Toutes",
                clearable=False
            ),
            md=4
        )
    ], className="mb-3"),

    # GRAPH
    dbc.Row([
        dbc.Col(dcc.Graph(id="graph-ventes"), md=12)
    ]),

    # TEXTE DE DÉTAIL DU POINT CLIQUÉ
    dbc.Row([
        dbc.Col(html.Div(
            "Cliquez sur une barre pour voir le détail.",
            id="detail-point",
            className="text-light mt-2"
        ))
    ])
], fluid=True)


# ---------- CALLBACK 1 : mettre à jour le graphique ----------
@app.callback(
    Output("graph-ventes", "figure"),
    Input("dropdown-region", "value")
)
def update_graph(region):
    if region == "Toutes":
        dff = df
        titre = "Ventes totales par mois (toutes régions)"
    else:
        dff = df[df["region"] == region]
        titre = f"Ventes par mois ({region})"

    df_mois = dff.groupby("mois", as_index=False)["ventes"].sum()
    fig = px.bar(df_mois, x="mois", y="ventes", title=titre)
    return fig


# ---------- CALLBACK 2 : KPI TOTAL ----------
@app.callback(
    Output("kpi-total", "children"),
    Input("dropdown-region", "value")
)
def update_kpi_total(region):
    if region == "Toutes":
        dff = df
    else:
        dff = df[df["region"] == region]
    return dff["ventes"].sum()


# ---------- CALLBACK 3 : KPI MEILLEUR MOIS ----------
@app.callback(
    Output("kpi-meilleur-mois", "children"),
    Input("dropdown-region", "value")
)
def update_kpi_best_month(region):
    if region == "Toutes":
        dff = df
    else:
        dff = df[df["region"] == region]
    return dff.groupby("mois")["ventes"].sum().idxmax()


# ---------- CALLBACK 4 : DÉTAIL DU POINT CLIQUÉ ----------
@app.callback(
    Output("detail-point", "children"),
    Input("graph-ventes", "clickData")
)
def update_detail(clickData):
    if clickData is None:
        return "Cliquez sur une barre pour voir le détail."

    point = clickData["points"][0]
    mois = point["x"]
    ventes = point["y"]
    return f"Vous avez cliqué sur le mois {mois} : {ventes} ventes."


# ---------- RUN ----------
if __name__ == "__main__":
    app.run(debug=True)
