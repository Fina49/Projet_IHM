"""
Page de Recherche.

Ce module permet de rechercher des créateurs selon plusieurs critères :
1. Filtres multiples (Plateforme, Région, Thème, Langue, etc.).
2. Tri dynamique (Vues, Likes, Partages).
3. Pagination des résultats.
"""

import dash
from dash import html, dcc, callback, Input, Output, State, callback_context
import dash_bootstrap_components as dbc

from functions import data_manager, render_creator_card_search

dash.register_page(__name__, path="/search", name="Recherche")

# Configuration
ITEMS_PER_PAGE = 4

SORT_OPTIONS = [
    {"label": "Vues ↓", "value": "views_desc"}, 
    {"label": "Vues ↑", "value": "views_asc"},
    {"label": "Likes ↓", "value": "likes_desc"}, 
    {"label": "Likes ↑", "value": "likes_asc"},
    {"label": "Partages ↓", "value": "shares_desc"},
]

# ============================================================
# 1. FONCTIONS UTILITAIRES (UI HELPERS)
# ============================================================

def make_dropdown(comp_id, options_list, placeholder_label="Toutes"):
    """
    Crée un menu déroulant standardisé avec une option par défaut 'Toutes'.
    """
    options = [{"label": placeholder_label, "value": "all"}]
    
    if options_list and isinstance(options_list[0], str):
        # Si la liste contient des chaînes simples
        options += [{"label": x, "value": x} for x in options_list]
    else:
        # Si la liste contient déjà des dicts {'label':..., 'value':...}
        options += options_list
        
    return dcc.Dropdown(
        id=comp_id, 
        options=options, 
        value="all", 
        clearable=False,
        className="favorites-dropdown" # Réutilisation de la classe existante
    )

def build_filters_section():
    """Génère la carte contenant tous les filtres de recherche."""
    return html.Div(
        className="search-filters-card", 
        children=[
            dcc.Input(
                id="search-query", 
                type="text", 
                placeholder="Rechercher par nom ou @username...", 
                className="favorites-search-input"
            ),
            dbc.Row(
                [
                    dbc.Col(make_dropdown("search-platform-dropdown", data_manager.get_unique_values("platforms")), md=4),
                    dbc.Col(make_dropdown("search-region-dropdown", data_manager.get_unique_values("region")), md=4),
                    dbc.Col(make_dropdown("search-theme-dropdown", data_manager.get_unique_values("tags")), md=4),
                ]
            ),
            dbc.Row(
                className="search-filter-row-spacer",
                children=[
                    dbc.Col(make_dropdown("search-language-dropdown", data_manager.get_unique_values("language")), md=4),
                    dbc.Col(make_dropdown("search-certified-dropdown", [{"label": "Certifiés", "value": "oui"}, {"label": "Non certifiés", "value": "non"}], placeholder_label="Tous"), md=4),
                    dbc.Col(make_dropdown("search-active-dropdown", [{"label": "Actifs", "value": "oui"}, {"label": "Inactifs", "value": "non"}], placeholder_label="Tous"), md=4),
                ]
            ),
        ]
    )

# ============================================================
# 2. LAYOUT
# ============================================================

layout = html.Div(
    className="main-container", 
    children=[
        # En-tête
        html.Div(
            className="search-header-container",
            children=[
                html.Div("Recherche de Créateurs", className="discovery-header-title"), 
                html.Div("Trouvez les créateurs correspondant à vos critères.", className="discovery-header-subtitle")
            ]
        ),
        
        # Filtres
        build_filters_section(),
        
        # Barre de tri et Titre résultats
        html.Div(
            className="search-results-header", 
            children=[
                html.Div(id="search-results-title", className="fw-bold text-secondary align-self-center"),
                dcc.Dropdown(
                    id="search-sort-dropdown", 
                    options=SORT_OPTIONS, 
                    value="views_desc", 
                    clearable=False, 
                    className="search-sort-dropdown"
                ),
            ]
        ),
        
        # Grille de résultats
        html.Div(id="search-results", className="search-results-grid"),
        
        # Pagination
        html.Div(
            id="search-pagination",
            className="search-pagination-container",
            children=[
                dbc.Button(
                    "<",
                    id="search-prev",
                    outline=True,
                    color="secondary",
                    size="sm",
                    n_clicks=0,
                ),
                html.Span(
                    "Page 1 / 1",
                    id="search-page-label",
                    className="align-self-center",
                ),
                dbc.Button(
                    ">",
                    id="search-next",
                    outline=True,
                    color="secondary",
                    size="sm",
                    n_clicks=0,
                ),
            ],
        ),
        
        # Store pour la pagination
        dcc.Store(id="search-current-page", data=1),
    ]
)

# ============================================================
# 3. CALLBACKS
# ============================================================

@callback(
    [
        Output("search-results", "children"),
        Output("search-results-title", "children"),
        Output("search-page-label", "children"),
        Output("search-prev", "disabled"),
        Output("search-next", "disabled"),
        Output("search-current-page", "data"),
    ],
    [
        Input("search-query", "value"),
        Input("search-platform-dropdown", "value"),
        Input("search-region-dropdown", "value"),
        Input("search-theme-dropdown", "value"),
        Input("search-language-dropdown", "value"),
        Input("search-certified-dropdown", "value"),
        Input("search-active-dropdown", "value"),
        Input("search-sort-dropdown", "value"),
        Input("search-prev", "n_clicks"),
        Input("search-next", "n_clicks"),
        Input("auth-status", "children"),
    ],
    [
        State("favorites-ids-store", "data"),
        State("search-current-page", "data"),
    ],
)
def update_search(
    query, platform, region, theme, lang, certif, active, sort_value, 
    prev_clicks, next_clicks, auth_status, fav_ids, current_page
):
    """
    Gère la logique complète de la recherche :
    1. Vérification de la connexion (pour marquer les favoris).
    2. Filtrage des données via DataManager.
    3. Tri des résultats.
    4. Gestion de la pagination (Précédent/Suivant).
    5. Génération des cartes HTML.
    """
    # 1. État Connexion
    is_logged_in = False
    # Vérification robuste du contenu texte du composant auth_status
    if auth_status and "connecté" in str(auth_status).lower() and "déconnecté" not in str(auth_status).lower():
        is_logged_in = True
    
    my_favs = [str(uid) for uid in (fav_ids or [])] if is_logged_in else []

    # 2. Filtrage & Tri
    filtered_list = data_manager.filter_creators(query, platform, region, theme, lang, certif, active)
    sorted_list = data_manager.sort_creators(filtered_list, sort_value)

    total = len(sorted_list)
    total_pages = max(1, (total + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE)

    # 3. Gestion de la page courante
    ctx = callback_context
    new_page = current_page or 1

    if ctx.triggered:
        trig_id = ctx.triggered[0]["prop_id"].split(".")[0]
        
        if trig_id == "search-prev":
            new_page = max(1, new_page - 1)
        elif trig_id == "search-next":
            new_page = min(total_pages, new_page + 1)
        # Si un filtre change (tout ID autre que les boutons nav), retour Page 1
        elif trig_id not in ("search-prev", "search-next"):
            new_page = 1

    # Sécurité bornes
    new_page = max(1, min(new_page, total_pages))

    # 4. Découpage des résultats (Slicing)
    start = (new_page - 1) * ITEMS_PER_PAGE
    page_items = sorted_list[start : start + ITEMS_PER_PAGE]

    # 5. Construction des cartes
    if total == 0:
        title = "Aucun créateur"
        cards = [
            html.Div(
                "Aucun résultat ne correspond à vos critères.",
                className="text-muted fst-italic p-4 text-center",
            )
        ]
    else:
        title = f"Résultats ({total})"
        # Génération des cartes avec état favori
        cards = [
            render_creator_card_search(c, is_favorite=(str(c["id"]) in my_favs)) 
            for c in page_items
        ]

    # 6. Mise à jour UI Pagination
    label = f"Page {new_page} / {total_pages}"
    prev_disabled = (new_page == 1)
    next_disabled = (new_page == total_pages)

    return cards, title, label, prev_disabled, next_disabled, new_page