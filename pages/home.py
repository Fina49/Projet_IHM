"""
Page d'Accueil (Dashboard).

Ce module affiche :
1. Les KPIs globaux (Vues, Likes, etc.).
2. Une carte interactive du monde (Choropleth).
3. Des filtres dynamiques (Plateforme, Thématique, Pays).
4. Une logique de pondération des statistiques selon la plateforme sélectionnée.
"""

import dash
from dash import html, dcc, callback, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
from dash.dependencies import ALL
import plotly.express as px

# Imports des données et utilitaires
from constants import THEMES, COUNTRY_STATS
from functions import data_manager, render_kpi_card, short_number

dash.register_page(__name__, path="/", name="Accueil")

# Options pour le menu déroulant de la carte
MAP_DROPDOWN_OPTIONS = [
    {"label": "Nombre de vues", "value": "views"},
    {"label": "Nombre de vidéos", "value": "videos"},
    {"label": "Nombre de likes", "value": "likes"},
    {"label": "Nombre de partages", "value": "shares"},
    {"label": "Nombre de commentaires", "value": "comments"},
    {"label": "Nombre de créateurs", "value": "creators"},
]

# ============================================================
# 1. FONCTIONS UTILITAIRES (HELPERS UI)
# ============================================================

def render_platform_option(p_id, name, color, count, count_id):
    """
    Génère une ligne cliquable pour sélectionner une plateforme (TikTok/YouTube).
    """
    return html.Div(
        id=p_id,
        className="platform-option",
        n_clicks=0,
        children=dbc.Row(
            align="center",
            className="my-2",
            children=[
                dbc.Col(
                    [
                        # Carré de couleur (style inline conservé car la couleur est dynamique)
                        html.Div(
                            style={"backgroundColor": color},
                            className="platform-color-box"
                        ),
                        html.Span(name)
                    ],
                    md=6,
                    className="d-flex align-items-center"
                ),
                dbc.Col(
                    html.Span(
                        f"{short_number(count)} vidéos", 
                        id=count_id, 
                        className="text-primary fw-bold"
                    ),
                    md=6,
                    className="text-end"
                ),
            ]
        )
    )

def render_filter_pill(label_prefix, value, kind, iso_value=None):
    """
    Crée un badge (pilule) représentant un filtre actif avec un bouton de fermeture.
    Pour les pays, iso_value contient le code ISO tandis que value contient le nom affiché.
    """
    filter_value = iso_value if iso_value else value
    return html.Span(
        [
            f"{label_prefix} : {value}",
            html.Span(
                " ✕",
                id={"type": "remove-filter", "kind": kind, "value": filter_value},
                className="filter-close ms-2"
            )
        ],
        className="platform-filter-badge"
    )

def render_selectable_badge(text, type_id, id_key, is_selected):
    """
    Crée un badge cliquable (thème ou pays) avec gestion de l'état sélectionné.
    """
    css_class = "theme-badge selected" if is_selected else "theme-badge"
    return html.Span(
        text,
        id={"type": type_id, **id_key},
        className=css_class,
        n_clicks=0
    )

def render_stat_line(label, value):
    """
    Affiche une ligne de statistique simple (Label ..... Valeur).
    """
    return html.Div(
        [
            html.Span(label),
            html.Span(short_number(value), className="fw-bold")
        ],
        className="d-flex justify-content-between mb-1"
    )

def render_card_header(icon_cls, title):
    """
    Génère un en-tête de carte standardisé avec icône.
    """
    return dbc.CardHeader(
        html.Div(
            [
                html.I(className=f"{icon_cls} me-2"),
                html.Span(title, className="fw-semibold")
            ],
            className="d-flex align-items-center"
        )
    )

# ============================================================
# 2. LAYOUT DE LA PAGE
# ============================================================

layout = html.Div(
    className="main-container",
    children=[
        # --- Stores pour la gestion d'état ---
        dcc.Store(id="platform-selection", data="all"),
        dcc.Store(id="selected-theme", data=[]),
        dcc.Store(id="selected-country", data=[]),

        # --- En-tête ---
        html.Div(
            [
                html.H1(
                    ["Découvrez Vos ", html.Span("Créateurs", className="text-primary")],
                    className="display-4 text-center"
                ),
                html.P(
                    "Explorez le monde des créateurs de contenu.",
                    className="lead text-center"
                )
            ],
            className="my-4"
        ),
        
        # --- Cartes KPIs (remplies par callback) ---
        dbc.Row(id="stats-cards", className="g-3 my-3"),
        
        html.P(
            ["Bienvenue dans votre espace d’exploration !", html.Br(), "Utilisez les filtres pour mettre à jour la carte."],
            className="lead text-center"
        ),

        # --- Barre des Filtres Actifs ---
        dbc.Card(
            className="filters-active-card mb-4",
            children=[
                dbc.Row(
                    [
                        dbc.Col(
                            html.Div(
                                [
                                    html.Span("Filtres actifs :", className="fw-semibold me-2"),
                                    html.Span(id="active-filters", className="d-inline-flex flex-wrap gap-2")
                                ]
                            ),
                            md=10
                        ),
                        dbc.Col(
                            html.Div(
                                dbc.Button("Tout effacer", id="clear-filters", size="sm", color="light"),
                                className="text-end"
                            ),
                            md=2
                        ),
                    ],
                    className="align-items-center py-2 px-3"
                )
            ]
        ),

        # --- Sélecteur de Plateforme ---
        dbc.Card(
            className="p-3 mb-4 shadow-sm border",
            children=[
                html.Div(
                    [
                        html.I(className="bi bi-pie-chart-fill me-2"),
                        html.Span("Répartition par Plateforme", className="fw-semibold")
                    ],
                    className="mb-3"
                ),
                render_platform_option(
                    "select-tiktok", "TikTok", "#ff1493", 
                    data_manager.global_platforms["tiktok"], "count-tiktok"
                ),
                render_platform_option(
                    "select-youtube", "YouTube", "#ff0000", 
                    data_manager.global_platforms["youtube"], "count-youtube"
                ),
            ]
        ),

        # --- Contenu Principal (Infos + Carte) ---
        dbc.Row(
            className="my-4",
            children=[
                # Colonne Gauche : Informations Textuelles
                dbc.Col(
                    dbc.Card(
                        [
                            render_card_header("bi bi-info-circle-fill", "Informations complémentaires"),
                            dbc.CardBody(
                                [
                                    html.H6("Top catégories", className="fw-bold mb-2"), 
                                    html.Div(id="theme-badge-container", className="d-flex flex-wrap gap-2 mb-3"),
                                    
                                    html.H6("Top 10 pays", className="fw-bold mb-2"), 
                                    html.Div(id="country-badge-container", className="d-flex flex-wrap gap-2 mb-3"),
                                    
                                    html.H6("Stats filtrées", className="fw-bold mb-2"), 
                                    html.Div(id="filtered-key-stats", className="small"),
                                ]
                            )
                        ],
                        className="h-100 shadow-sm"
                    ),
                    lg=6
                ),
                # Colonne Droite : Carte du Monde
                dbc.Col(
                    dbc.Card(
                        [
                            render_card_header("bi bi-geo-alt-fill", "Répartition Géographique"),
                            dbc.CardBody(
                                [
                                    dbc.Row(
                                        [
                                           dbc.Col(html.Label("Indicateur de la carte :", className="fw-bold mt-1"), width="auto"),
                                           dbc.Col(dcc.Dropdown(id="map-indicator", options=MAP_DROPDOWN_OPTIONS, value="views", clearable=False, className="w-100")) 
                                        ],
                                        className="mb-3 align-items-center"
                                    ),
                                    html.Div(
                                        dcc.Graph(
                                            id="world-map",
                                            config={"displayModeBar": False},
                                            className="map-graph"
                                        ),
                                        className="map-container-div"
                                    )
                                ]
                            )
                        ],
                        className="h-100 shadow-sm"
                    ),
                    lg=6
                ),
            ]
        ),
    ]
)

# ============================================================
# 3. CALLBACKS (LOGIQUE D'INTERACTION)
# ============================================================

@callback(
    [Output("select-tiktok", "className"), Output("select-youtube", "className")],
    Input("platform-selection", "data")
)
def update_platform_style(platform):
    """Met à jour le style visuel (sélectionné/non sélectionné) des boutons plateforme."""
    base = "platform-option"
    if platform == "TikTok":
        return f"{base} selected", base
    if platform == "YouTube":
        return base, f"{base} selected"
    return base, base

@callback(
    Output("theme-badge-container", "children"),
    Input("selected-theme", "data")
)
def render_theme_badges(selected_list):
    """Génère les badges de thématiques."""
    selected_list = selected_list or []
    return [render_selectable_badge(t, "theme-badge", {"name": t}, t in selected_list) for t in THEMES]

@callback(
    Output("country-badge-container", "children"),
    Input("selected-country", "data")
)
def render_country_badges(selected_iso_list):
    """Génère les badges des pays (Top 10)."""
    selected_iso_list = selected_iso_list or []
    top_countries = data_manager.df_initial.sort_values("views", ascending=False).head(10)
    return [
        render_selectable_badge(row['name'], "country-badge", {"iso": row['iso_alpha']}, row['iso_alpha'] in selected_iso_list)
        for _, row in top_countries.iterrows()
    ]

@callback(
    Output("active-filters", "children"),
    [Input("platform-selection", "data"), Input("selected-theme", "data"), Input("selected-country", "data")]
)
def update_active_filters_display(platform, themes, countries):
    """Affiche les pilules de filtres actifs en haut de page."""
    pills = []
    if platform and platform != "all":
        pills.append(render_filter_pill("Plateforme", platform, "platform"))
    
    country_map = {iso: data['name'] for iso, data in COUNTRY_STATS.items()}
    
    for t in (themes or []):
        pills.append(render_filter_pill("Thème", t, "theme"))
    for iso in (countries or []):
        # Utiliser l'ISO comme valeur pour permettre la suppression correcte
        pills.append(render_filter_pill("Pays", country_map.get(iso, iso), "country", iso_value=iso))
        
    return pills if pills else html.Span("Aucun filtre appliqué", className="text-muted small")

@callback(
    [Output("platform-selection", "data"), Output("selected-theme", "data"), Output("selected-country", "data")],
    [
        Input("select-tiktok", "n_clicks"),
        Input("select-youtube", "n_clicks"),
        Input("clear-filters", "n_clicks"),
        Input({"type": "remove-filter", "kind": ALL, "value": ALL}, "n_clicks"),
        Input({"type": "theme-badge", "name": ALL}, "n_clicks"),
        Input({"type": "country-badge", "iso": ALL}, "n_clicks"),
        Input("world-map", "clickData")
    ],
    [State("platform-selection", "data"), State("selected-theme", "data"), State("selected-country", "data")]
)
def manage_all_filters(tk_click, yt_click, clear_click, rm_click, theme_click, country_click, map_click, 
                      platform, themes, countries):
    """Gestion centralisée de tous les clics modifiant les filtres."""
    ctx = callback_context
    if not ctx.triggered:
        return "all", [], []
    
    trig_id = ctx.triggered_id
    themes = themes or []
    countries = countries or []
    platform = platform or "all"

    # Reset global
    if trig_id == "clear-filters":
        return "all", [], []

    # Sélection plateforme
    if trig_id == "select-tiktok":
        return ("TikTok" if platform != "TikTok" else "all"), themes, countries
    if trig_id == "select-youtube":
        return ("YouTube" if platform != "YouTube" else "all"), themes, countries
    
    # Clic sur la carte
    if trig_id == "world-map" and map_click:
        iso = map_click["points"][0]["location"]
        if iso in countries:
            new_countries = [c for c in countries if c != iso]
        else:
            new_countries = countries + [iso]
        return platform, themes, new_countries

    # Pattern matching pour suppression ou toggle de badges
    if isinstance(trig_id, dict):
        kind = trig_id.get("type")
        # Suppression via la croix
        if kind == "remove-filter":
            k_filter = trig_id.get("kind")
            val = trig_id.get("value")
            if k_filter == "platform": platform = "all"
            elif k_filter == "theme": themes = [t for t in themes if t != val]
            elif k_filter == "country": countries = [c for c in countries if c != val]
        
        # Toggle Badges
        elif kind == "theme-badge":
            val = trig_id.get("name")
            themes = [t for t in themes if t != val] if val in themes else themes + [val]
        elif kind == "country-badge":
            val = trig_id.get("iso")
            countries = [c for c in countries if c != val] if val in countries else countries + [val]
            
    return platform, themes, countries

@callback(
    [
        Output("stats-cards", "children"), 
        Output("filtered-key-stats", "children"),
        Output("world-map", "figure"),
        Output("count-tiktok", "children"),
        Output("count-youtube", "children")
    ],
    [
        Input("platform-selection", "data"),
        Input("selected-theme", "data"),
        Input("selected-country", "data"),
        Input("map-indicator", "value")
    ]
)
def update_visualizations(platform, themes, countries, indicator):
    """
    Met à jour tous les graphiques et KPIs.
    Calcul dynamiquement les volumes TikTok vs YouTube selon les constantes.
    """
    # 1. Données filtrées pour les KPI (tient compte du filtre plateforme)
    dff = data_manager.get_filtered_df(platform, themes, countries)
    agg = data_manager.get_kpi_stats(dff)

    # 2. Calcul du contexte global (TikTok vs YouTube)
    # On recalcule sur le set "toutes plateformes" pour afficher les volumes à côté des boutons
    dff_context = data_manager.get_filtered_df("all", themes, countries)
    
    tik_videos = 0
    yt_videos = 0
    
    for _, row in dff_context.iterrows():
        iso = row['iso_alpha']
        raw_stats = COUNTRY_STATS.get(iso, {})
        split = raw_stats.get("platform_split", {"TikTok": 0.5, "YouTube": 0.5})
        
        vid = row['videos']
        tik_videos += vid * split.get("TikTok", 0)
        yt_videos += vid * split.get("YouTube", 0)

    # 3. Création des cartes KPI
    kpi_definitions = [
        ("Total vidéos", "videos"), ("Total vues", "views"), 
        ("Likes", "likes"), ("Partages", "shares"), 
        ("Commentaires", "comments"), ("Créateurs", "creators")
    ]
    
    kpi_cards = [
        dbc.Col(render_kpi_card(label, short_number(agg.get(key, 0))), xs=6, md=4, lg=2)
        for label, key in kpi_definitions
    ]

    # 4. Stats latérales (format texte)
    filtered_stats = [
        render_stat_line(l, agg.get(k, 0)) 
        for l, k in [("Vues", "views"), ("Likes", "likes"), ("Partages", "shares"), ("Créateurs", "creators")]
    ]

    # 5. Carte du Monde
    label_map = {item["value"]: item["label"] for item in MAP_DROPDOWN_OPTIONS}
    legend_title = label_map.get(indicator, indicator)
    
    if dff.empty:
        fig = px.choropleth(locations=[], locationmode="ISO-3")
        fig.update_layout(template="plotly_white")
    else:
        dff['formatted_value'] = dff[indicator].apply(lambda x: short_number(x))
        fig = px.choropleth(
            dff, 
            locations="iso_alpha", 
            color=indicator, 
            scope="world", 
            hover_name="name",
            hover_data=["rank_label", "formatted_value"],
            color_continuous_scale=px.colors.sequential.Blues
        )
        fig.update_traces(
            hovertemplate="<b>%{hovertext}</b><br>Rang: %{customdata[0]}<br>Valeur: %{customdata[1]}<extra></extra>"
        )

    fig.update_layout(
        coloraxis_colorbar=dict(title=legend_title, tickformat=".2s"),
        margin=dict(l=0, r=0, t=0, b=0),
        geo=dict(
            bgcolor="rgba(0,0,0,0)", 
            showcountries=True, 
            showframe=False, 
            showcoastlines=False,
            projection_type="natural earth"
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )

    return (
        kpi_cards, 
        filtered_stats, 
        fig, 
        f"{short_number(tik_videos)} vidéos", 
        f"{short_number(yt_videos)} vidéos"
    )