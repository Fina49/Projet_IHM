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

# options pour le dropdown des régions
regions = sorted(df["region"].unique())
options_region = [{"label": "Toutes les régions", "value": "Toutes"}] + [
    {"label": r, "value": r} for r in regions
]

# ---------- LAYOUT ----------
app.layout = dbc.Container(

    children=[

        # TITRE
        dbc.Row([
            dbc.Col(
                html.H1("Dashboard de ventes",
                        className="text-center text-primary page-title"),
                md=12
            )
        ]),
        dbc.Row([
            dbc.Col(html.P(
                "Fil rouge : tableau de bord des ventes 2024.",
                className="text-center text-muted page-subtitle"
            ))
        ]),

        # KPIs
        dbc.Row([
            dbc.Col(
                dbc.Card(
                    [
                        dbc.CardHeader("Total des ventes",
                                       className="kpi-header"),
                        dbc.CardBody(
                            html.H3(id="kpi-total",
                                    className="kpi-value text-success")
                        )
                    ],
                    color="dark",
                    inverse=True,
                    className="kpi-card"
                ),
                md=4
            ),
            dbc.Col(
                dbc.Card(
                    [
                        dbc.CardHeader("Nombre de régions",
                                       className="kpi-header"),
                        dbc.CardBody(
                            html.H3(f"{nb_regions}",
                                    className="kpi-value text-info")
                        )
                    ],
                    color="dark",
                    inverse=True,
                    className="kpi-card"
                ),
                md=4
            ),
            dbc.Col(
                dbc.Card(
                    [
                        dbc.CardHeader("Meilleur mois",
                                       className="kpi-header"),
                        dbc.CardBody(
                            html.H3(id="kpi-meilleur-mois",
                                    className="kpi-value text-warning")
                        )
                    ],
                    color="dark",
                    inverse=True,
                    className="kpi-card"
                ),
                md=4
            ),
        ], className="mb-4"),

        # CONTROLES (dropdown + radio)
        dbc.Row([
            dbc.Col(
                dbc.Card(
                    [
                        dbc.CardHeader("Filtres",
                                       className="controls-header"),
                        dbc.CardBody([
                            html.Div("Région :", className="control-label"),
                            dcc.Dropdown(
                                id="dropdown-region",
                                options=options_region,
                                value="Toutes",
                                clearable=False,
                                className="mb-3"
                            ),
                            html.Div("Type de graphique :",
                                     className="control-label"),
                            dcc.RadioItems(
                                id="choix-type-graph",
                                options=[
                                    {"label": "Barres", "value": "bar"},
                                    {"label": "Courbe", "value": "line"}
                                ],
                                value="bar",
                                inline=True,
                                className="text-light"
                            )
                        ])
                    ],
                    color="dark",
                    inverse=True,
                    className="controls-card"
                ),
                md=6
            )
        ], className="mb-4 justify-content-center"),

        # SECTION GRAPHIQUE
        dbc.Row([
            dbc.Col(
                html.H4("Ventes par mois",
                        className="section-title text-light"),
                md=12
            )
        ], className="mb-2"),

        dbc.Row([
            dbc.Col(
                dcc.Graph(id="graph-ventes",
                          config={"displayModeBar": True}),
                md=12
            )
        ]),

        # DÉTAIL DU POINT CLIQUÉ
        dbc.Row([
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        html.Div(
                            "Cliquez sur une barre ou un point pour voir le détail.",
                            id="detail-point",
                            className="detail-text"
                        )
                    ),
                    className="detail-card",
                    color="dark",
                    inverse=True
                ),
                md=6
            )
        ], className="mt-4 mb-4 justify-content-center")

    ],
    fluid=True,
    className="page-container"
)

# ---------- CALLBACK 1 : graphique ----------
@app.callback(
    Output("graph-ventes", "figure"),
    Input("dropdown-region", "value"),
    Input("choix-type-graph", "value")
)
def update_graph(region, graph_type):
    if region == "Toutes":
        dff = df
        titre = "Ventes par mois (toutes régions)"
    else:
        dff = df[df["region"] == region]
        titre = f"Ventes par mois ({region})"

    df_mois = dff.groupby("mois", as_index=False)["ventes"].sum()

    if graph_type == "line":
        fig = px.line(df_mois, x="mois", y="ventes", title=titre)
    else:
        fig = px.bar(df_mois, x="mois", y="ventes", title=titre)

    fig.update_layout(
        margin=dict(l=40, r=20, t=60, b=40),
        plot_bgcolor="#111111",
        paper_bgcolor="#111111",
        font_color="#E0E0E0"
    )
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


# ---------- CALLBACK 4 : DÉTAIL POINT CLIQUÉ ----------
@app.callback(
    Output("detail-point", "children"),
    Input("graph-ventes", "clickData")
)
def update_detail(clickData):
    if clickData is None:
        return "Cliquez sur une barre ou un point pour voir le détail."

    point = clickData["points"][0]
    mois = point["x"]
    ventes = point["y"]
    return f"Vous avez cliqué sur le mois {mois} : {ventes} ventes."


# ---------- RUN ----------
if __name__ == "__main__":
    app.run(debug=True)
