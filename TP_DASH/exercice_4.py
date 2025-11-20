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

total_ventes = df["ventes"].sum()
nb_regions = df["region"].nunique()
meilleur_mois = df.groupby("mois")["ventes"].sum().idxmax()

# options du dropdown de région
regions = sorted(df["region"].unique())
options_region = [{"label": "Toutes les régions", "value": "Toutes"}] + \
    [{"label": r, "value": r} for r in regions]

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
            dbc.CardBody(html.H3(f"{total_ventes}", className="text-success"))
        ], className="mb-3"), md=4),
        dbc.Col(dbc.Card([
            dbc.CardHeader("Nombre de régions"),
            dbc.CardBody(html.H3(f"{nb_regions}", className="text-info"))
        ], className="mb-3"), md=4),
        dbc.Col(dbc.Card([
            dbc.CardHeader("Meilleur mois (global)"),
            dbc.CardBody(html.H3(meilleur_mois, className="text-warning"))
        ], className="mb-3"), md=4),
    ], className="mb-4", id="kpi-row"),

    # DROPDOWN DE REGION
    dbc.Row([
        dbc.Col(
            dcc.Dropdown(
                id="dropdown-region",
                options=options_region,
                value="Toutes",      # valeur initiale
                clearable=False
            ),
            md=4
        )
    ], className="mb-3"),

    # GRAPH
    dbc.Row([
        dbc.Col(dcc.Graph(id="graph-ventes"), md=12)
    ], id="graph-row")
], fluid=True)


# ---------- CALLBACK : met à jour le graph selon la région ----------
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

    df_mois_region = dff.groupby("mois", as_index=False)["ventes"].sum()

    fig = px.bar(
        df_mois_region,
        x="mois",
        y="ventes",
        title=titre
    )
    return fig


if __name__ == "__main__":
    app.run(debug=True)
