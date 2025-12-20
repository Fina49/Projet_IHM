"""
Page de Profil Créateur.

Ce module gère l'affichage détaillé d'un créateur :
1. En-tête dynamique (Avatar, infos, bouton favori).
2. KPIs globaux ou par plateforme.
3. Onglets de contenu :
   - Vue générale (Graphique de progression).
   - Top Vidéos (Liste paginée et triable).
   - Analytique Avancée (Outils de comparaison et d'analyse fine).
"""

import json
import dash
from dash import html, dcc, callback, Input, Output, State, callback_context, no_update
import dash_bootstrap_components as dbc
from dash.dependencies import ALL

from functions import (
    get_creator_by_id, 
    render_creator_card_search, 
    short_number, 
    render_top_video_card,
    analytics_engine,
    get_platform_stats,
    render_kpi_card
)
from constants import TOP_VIDEOS

dash.register_page(__name__, path_template="/profile/<id>", name="Profil créateur")

# Constantes locales pour les labels et options
METRICS_LABELS = {
    "views": "Vues", "likes": "Likes", "shares": "Partages", 
    "comments": "Commentaires", "followers": "Abonnés"
}

SORT_OPTIONS_VIDEOS = [
    {"label": "Vues ↓", "value": "views_desc"}, 
    {"label": "Vues ↑", "value": "views_asc"}, 
    {"label": "Likes ↓", "value": "likes_desc"}, 
    {"label": "Likes ↑", "value": "likes_asc"}
]

# ============================================================
# 1. LAYOUT PRINCIPAL
# ============================================================

def layout(id=None, **kwargs):
    """
    Génère la structure de la page profil.
    L'ID du créateur est passé via l'URL (path_template).
    """
    creator = get_creator_by_id(id)
    if not creator:
        return html.Div(
            "Créateur introuvable.",
            className="alert alert-danger m-4"
        )

    return html.Div(
        className="main-container",
        children=[
            # 1. EN-TÊTE (Carte créateur avec bouton favori géré par callback)
            html.Div(id="profile-header-card"), 
            
            # 2. SÉLECTEUR DE PLATEFORME (Global)
            html.Div(
                [
                    html.Label("Sélectionner la plateforme", className="fw-bold mb-2"), 
                    dcc.Dropdown(
                        id="profile-platform-global", 
                        clearable=False, 
                        className="profile-platform-dropdown"
                    )
                ],
                className="mb-4"
            ),
            
            # 3. CONTENEUR KPI (Cartes de statistiques)
            html.Div(id="profile-kpi-container", className="mb-4"),
            
            # 4. ONGLETS DE NAVIGATION
            dcc.Tabs(
                id="profile-tabs", 
                value="general", 
                className="dash-tabs profile-tabs", 
                children=[
                    dcc.Tab(label="Général", value="general"), 
                    dcc.Tab(label="Top Vidéos", value="top"), 
                    dcc.Tab(label="Analytique Avancée", value="analytics")
                ]
            ),
            
            # 5. CONTENU DES ONGLETS
            html.Div(
                id="profile-tab-content", 
                className="profile-content-area", 
                children=[
                    # --- Onglet A : Général ---
                    html.Div(
                        id="profile-general-container", 
                        children=[
                            dbc.Card(
                                dbc.CardBody(
                                    [
                                        html.H5("Vue d'ensemble", className="mb-3"), 
                                        dcc.Graph(id="general-graph")
                                    ]
                                ),
                                className="shadow-sm border-0"
                            )
                        ]
                    ),
                    
                    # --- Onglet B : Top Vidéos ---
                    html.Div(
                        id="profile-top-container", 
                        style={"display": "none"}, # Caché par défaut
                        children=[
                            html.Div(
                                className="d-flex justify-content-between mb-3 align-items-center", 
                                children=[
                                    html.Div("TOP Vidéos", className="h5 fw-bold mb-0"), 
                                    dcc.Dropdown(
                                        id="profile-sort-videos", 
                                        options=SORT_OPTIONS_VIDEOS, 
                                        value="views_desc", 
                                        clearable=False, 
                                        className="profile-sort-dropdown"
                                    )
                                ]
                            ), 
                            html.Div(id="profile-top-videos-list", className="top-videos-list mb-3"), 
                            html.Div(
                                className="search-pagination-container", 
                                children=[
                                    dbc.Button(
                                        "<",
                                        id="vid-prev",
                                        outline=True,
                                        color="secondary",
                                        size="sm",
                                        n_clicks=0,
                                    ),
                                    html.Span(
                                        id="vid-page-label",
                                        className="align-self-center",
                                    ),
                                    dbc.Button(
                                        ">",
                                        id="vid-next",
                                        outline=True,
                                        color="secondary",
                                        size="sm",
                                        n_clicks=0,
                                    )
                                ]
                            )
                        ]
                    ),
                    
                    # --- Onglet C : Analytique Avancée ---
                    html.Div(
                        id="profile-analytics-container", 
                        style={"display": "none"}, # Caché par défaut
                        children=[
                            dbc.Row(
                                [
                                    # Panneau de configuration (Gauche)
                                    dbc.Col(
                                        md=4, 
                                        children=[
                                            dbc.Card(
                                                dbc.CardBody(
                                                    [
                                                        html.Div("Configuration", className="analytics-section-title"),
                                                        
                                                        html.Label("Mode d'affichage", className="fw-bold mt-2"), 
                                                        dcc.RadioItems(
                                                            id="an-mode", 
                                                            options=[
                                                                {"label": "Valeurs brutes", "value": "values"}, 
                                                                {"label": "Progression (%)", "value": "progression"}, 
                                                                {"label": "Ratios (KPI/KPI)", "value": "ratio"}
                                                            ], 
                                                            value="values", 
                                                            labelStyle={"display": "block", "marginBottom": "5px"},
                                                            inputStyle={"marginRight": "8px"}
                                                        ), 
                                                        html.Hr(), 
                                                        
                                                        html.Label("Axe X (Temps)", className="fw-bold"), 
                                                        dcc.Dropdown(
                                                            id="an-x", 
                                                            options=[{"label": "Temps (Mois)", "value": "time"}], 
                                                            value="time", 
                                                            clearable=False
                                                        ), 
                                                        
                                                        html.Label("Métrique(s) Axe Y", className="fw-bold mt-3"), 
                                                        
                                                        # Sélecteur Multiple (Mode normal)
                                                        html.Div(
                                                            id="an-multi-ui", 
                                                            children=[
                                                                dcc.Dropdown(
                                                                    id="an-y-multi", 
                                                                    options=[{"label": l, "value": k} for k,l in METRICS_LABELS.items()], 
                                                                    value=["views"], 
                                                                    multi=True
                                                                )
                                                            ]
                                                        ), 
                                                        
                                                        # Sélecteurs Ratio (Mode Ratio)
                                                        html.Div(
                                                            id="an-ratio-ui", 
                                                            style={"display": "none"}, 
                                                            children=[
                                                                html.Div("Numérateur", className="small text-muted mt-2"), 
                                                                dcc.Dropdown(
                                                                    id="an-num", 
                                                                    options=[{"label": l, "value": k} for k,l in METRICS_LABELS.items()], 
                                                                    value="likes", 
                                                                    clearable=False
                                                                ), 
                                                                html.Div("Dénominateur", className="small text-muted mt-2"), 
                                                                dcc.Dropdown(
                                                                    id="an-den", 
                                                                    options=[{"label": l, "value": k} for k,l in METRICS_LABELS.items()], 
                                                                    value="views", 
                                                                    clearable=False
                                                                )
                                                            ]
                                                        ), 
                                                        html.Hr(), 
                                                        
                                                        html.Label("Filtre Plateforme", className="fw-bold"), 
                                                        dcc.Dropdown(
                                                            id="analytics-platform-filter", 
                                                            options=[
                                                                {"label": "Combiné (Global)", "value": "combined"}, 
                                                                {"label": "Séparés (Comparatif)", "value": "both"}, 
                                                                {"label": "TikTok uniquement", "value": "TikTok"}, 
                                                                {"label": "YouTube uniquement", "value": "YouTube"}
                                                            ], 
                                                            value="combined", 
                                                            clearable=False
                                                        ), 
                                                        
                                                        dcc.Checklist(
                                                            id="an-advanced", 
                                                            options=[
                                                                {"label": " Afficher Tendance", "value": "reg"}, 
                                                                {"label": " Afficher Prévision (+3 mois)", "value": "forecast"}
                                                            ], 
                                                            value=[], 
                                                            style={"marginTop": "15px"},
                                                            inputStyle={"marginRight": "8px"}
                                                        ),

                                                        # SECTION COMPARAISON
                                                        html.Label("Comparer avec...", className="fw-bold mt-4"),
                                                        dcc.Dropdown(
                                                            id="an-compare",
                                                            options=[
                                                                {"label": "Aucune comparaison", "value": "none"},
                                                                {"label": "Moyenne du Pays", "value": "country"},
                                                                {"label": "Moyenne de la Catégorie", "value": "tag"}
                                                            ],
                                                            value="none",
                                                            clearable=False
                                                        ),

                                                    ]
                                                ), 
                                                className="analytics-panel-card h-100"
                                            )
                                        ]
                                    ), 
                                    
                                    # Graphique Principal (Droite)
                                    dbc.Col(
                                        md=8, 
                                        children=[
                                            dbc.Card(
                                                dbc.CardBody(
                                                    [dcc.Graph(id="an-graph", className="analytics-graph-container")]
                                                ), 
                                                className="analytics-graph-card h-100"
                                            )
                                        ]
                                    )
                                ]
                            )
                        ]
                    ),
                ]
            ),
            
            # Stores de gestion d'état
            dcc.Store(id="profile-current-id", data=id),
            dcc.Store(id="video-pagination-page", data=1)
        ]
    )

# ============================================================
# 2. CALLBACKS
# ============================================================

@callback(
    Output("profile-header-card", "children"),
    [Input("profile-current-id", "data"), Input("auth-mode", "data"), Input("favorites-ids-store", "data")]
)
def render_profile_header(cid, auth_mode, fav_ids):
    """Met à jour la carte d'en-tête (Avatar, Nom) et l'état du bouton favori."""
    creator = get_creator_by_id(cid)
    if not creator: 
        return None
    
    is_logged_in = (auth_mode == "profile")
    is_fav = str(cid) in [str(x) for x in (fav_ids or [])] if is_logged_in else False
    
    return render_creator_card_search(creator, is_favorite=is_fav, mode="profile")

@callback(
    Output("favorites-ids-store", "data", allow_duplicate=True),
    Input({"type": "profile-fav-btn", "id": ALL}, "n_clicks"),
    [State("favorites-ids-store", "data"), State("auth-mode", "data")],
    prevent_initial_call=True
)
def toggle_favorite(n_clicks, current_ids, auth_mode):
    """Gère l'ajout/retrait des favoris depuis le bouton profil."""
    if not n_clicks or not any(n_clicks) or auth_mode != "profile": 
        return no_update
    
    ctx = callback_context
    if not ctx.triggered: 
        return no_update
    
    try:
        # Récupération de l'ID depuis le pattern matching du bouton
        cid = str(json.loads(ctx.triggered[0]["prop_id"].split(".")[0])["id"])
        current_ids = [str(x) for x in (current_ids or [])]
        
        if cid in current_ids:
            return [x for x in current_ids if x != cid]
        else:
            return current_ids + [cid]
    except Exception:
        return no_update

@callback(
    [Output("profile-platform-global", "options"), Output("profile-platform-global", "value")], 
    Input("profile-current-id", "data")
)
def init_platform_selector(cid):
    """Initialise le dropdown plateforme (Combiné si possible, sinon la seule dispo)."""
    creator = get_creator_by_id(cid)
    if not creator: 
        return [], None
    
    platforms = list(creator.get("platforms", {}).keys())
    opts = [{"label": "Combiné (Global)", "value": "combined"}] if len(platforms) > 1 else []
    
    for p in platforms: 
        opts.append({"label": p, "value": p})
        
    return opts, "combined" if len(platforms) > 1 else platforms[0]

@callback(
    Output("profile-kpi-container", "children"), 
    [Input("profile-platform-global", "value"), Input("profile-current-id", "data")]
)
def update_kpi_cards(platform, cid):
    """Met à jour les cartes KPI en fonction de la plateforme sélectionnée."""
    creator = get_creator_by_id(cid)
    if not creator or not platform: 
        return []
    
    stats = get_platform_stats(creator, platform)
    
    kpi_config = [
        ("Abonnés", "followers"), ("Vues", "views"), ("Likes", "likes"),
        ("Partages", "shares"), ("Vidéos", "videos"), ("Commentaires", "comments")
    ]
    
    cards = []
    for label, key in kpi_config:
        val = short_number(stats.get(key, 0))
        cards.append(dbc.Col(render_kpi_card(label, val), xs=6, md=4, lg=2))
        
    return dbc.Row(cards, className="g-3")

@callback(
    [
        Output("profile-general-container", "style"), 
        Output("profile-top-container", "style"), 
        Output("profile-analytics-container", "style")
    ], 
    Input("profile-tabs", "value")
)
def switch_tabs(tab):
    """Gère la visibilité des sections (Général / Top Vidéos / Analytique)."""
    show = {"display": "block"}
    hide = {"display": "none"}
    
    return (
        show if tab == "general" else hide,
        show if tab == "top" else hide,
        show if tab == "analytics" else hide
    )

@callback(
    Output("general-graph", "figure"), 
    [Input("profile-platform-global", "value"), Input("profile-current-id", "data")]
)
def update_general_graph(platform, cid):
    """Génère le graphique de progression global (Vue générale)."""
    creator = get_creator_by_id(cid)
    if not creator or not platform: 
        return {}
        
    metrics_to_show = ["views", "likes", "shares", "followers", "comments"]
    # Utilisation du moteur analytique avec des paramètres par défaut
    return analytics_engine.build_figure(
        creator, "progression", "time", metrics_to_show, None, None, platform, []
    )

@callback(
    [
        Output("profile-top-videos-list", "children"), 
        Output("video-pagination-page", "data"), 
        Output("vid-page-label", "children")
    ], 
    [
        Input("profile-platform-global", "value"), 
        Input("profile-sort-videos", "value"), 
        Input("vid-prev", "n_clicks"), 
        Input("vid-next", "n_clicks"), 
        Input("profile-current-id", "data")
    ], 
    State("video-pagination-page", "data")
)
def update_top_videos(platform, sort_val, prev, next, cid, current_page):
    """Gère l'affichage, le tri et la pagination de la liste des Top Vidéos."""
    creator = get_creator_by_id(cid)
    if not creator: 
        return [], 1, ""
        
    # 1. Agrégation des vidéos
    videos = []
    platforms_needed = ["TikTok", "YouTube"] if platform == "combined" else [platform]
    for p in platforms_needed: 
        videos.extend(TOP_VIDEOS.get(p, []))
    
    # 2. Tri
    metric, order = sort_val.split("_")
    videos = sorted(videos, key=lambda x: x.get(metric, 0), reverse=(order == "desc"))
    
    # 3. Pagination
    per_page = 3
    max_page = max(1, (len(videos) + per_page - 1) // per_page)
    
    ctx = callback_context
    if ctx.triggered and "vid-" in ctx.triggered[0]["prop_id"]:
        trig = ctx.triggered[0]["prop_id"]
        if "next" in trig: 
            current_page = min(current_page + 1, max_page)
        elif "prev" in trig: 
            current_page = max(1, current_page - 1)
    else: 
        current_page = 1
        
    start = (current_page - 1) * per_page
    page_items = videos[start : start + per_page]
    
    # 4. Rendu
    cards = [render_top_video_card(v, start + i + 1) for i, v in enumerate(page_items)]
    if not cards: 
        cards = [html.Div("Aucune vidéo disponible pour cette sélection.", className="text-muted fst-italic")]
        
    return cards, current_page, f"Page {current_page} / {max_page}"

@callback(
    [Output("an-multi-ui", "style"), Output("an-ratio-ui", "style")], 
    Input("an-mode", "value")
)
def toggle_analytics_controls(mode):
    """Affiche les contrôles adaptés au mode choisi (Sélecteur multiple vs Numérateur/Dénominateur)."""
    if mode == "ratio":
        return {"display": "none"}, {"display": "block"}
    return {"display": "block"}, {"display": "none"}

@callback(
    Output("an-graph", "figure"),
    [
        Input("an-mode", "value"), 
        Input("an-x", "value"), 
        Input("an-y-multi", "value"), 
        Input("an-num", "value"), 
        Input("an-den", "value"), 
        Input("analytics-platform-filter", "value"), 
        Input("an-advanced", "value"),
        Input("an-compare", "value"), 
        Input("profile-current-id", "data")
    ]
)
def update_analytics_chart(mode, x, ym, rn, rd, platform, adv, compare_val, cid):
    """
    Callback central du graphique analytique.
    Délègue la construction du graphique complexe à `analytics_engine`.
    """
    creator = get_creator_by_id(cid)
    return analytics_engine.build_figure(
        creator, mode, x, ym, rn, rd, platform, adv, compare_mode=compare_val
    )