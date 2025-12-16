"""
Page Mes Favoris.

Ce module gère :
1. L'affichage paginé des créateurs favoris de l'utilisateur.
2. Un système de recommandations basées sur les tags des favoris.
3. La suppression dynamique des favoris.
4. La gestion de l'état "Non connecté" via une alerte.
"""

import json
import dash
from dash import html, dcc, callback, Input, Output, State, callback_context, no_update
import dash_bootstrap_components as dbc
from dash.dependencies import ALL

# Imports des données et composants
from constants import ALL_CREATORS
from functions import render_creator_card_compact

dash.register_page(__name__, path="/favorites", name="Mes Favoris")

# ============================================================
# 1. LOGIQUE MÉTIER
# ============================================================

def get_creators_from_ids(ids_list):
    """Récupère les objets créateurs complets à partir d'une liste d'IDs."""
    if not ids_list: 
        return []
    str_ids = [str(i) for i in ids_list]
    return [c for c in ALL_CREATORS if str(c["id"]) in str_ids]

def get_recommendations(current_favorites_ids):
    """
    Génère des recommandations simples.
    Logique : Trouve des créateurs non-favoris qui partagent au moins un tag
    avec les favoris actuels.
    """
    if not current_favorites_ids: 
        return []
    
    current_favs = get_creators_from_ids(current_favorites_ids)
    fav_tags = set()
    for c in current_favs:
        fav_tags.update(c.get("tags", []))
    
    recommendations = []
    str_fav_ids = [str(i) for i in current_favorites_ids]
    
    for c in ALL_CREATORS:
        # On exclut ceux déjà favoris
        if str(c["id"]) in str_fav_ids: 
            continue
        
        # On vérifie l'intersection des tags
        c_tags = set(c.get("tags", []))
        if c_tags.intersection(fav_tags):
            recommendations.append(c)
            
    # On limite à 4 recommandations arbitrairement
    return recommendations[:4]

# ============================================================
# 2. UI HELPERS (Locaux)
# ============================================================

def render_favorite_item(creator):
    """
    Affiche une carte créateur avec un bouton de suppression (cœur brisé/rouge) flottant.
    """
    # La carte de base
    card = render_creator_card_compact(creator, is_favorite=True)
    
    return dbc.Col(
        md=6, lg=6,
        children=html.Div(
            className="fav-item-wrapper",
            children=[
                card,
                html.Button(
                    html.I(className="bi bi-heart-fill text-danger", style={"fontSize": "1.2rem"}),
                    id={"type": "fav-remove-btn", "id": creator["id"]},
                    className="fav-floating-remove-btn shadow-sm",
                    title="Retirer des favoris"
                )
            ]
        )
    )

def make_pagination_controls(section_id, current_page, total_pages):
    """Génère les boutons Précédent/Suivant et le compteur de pages."""
    if total_pages <= 1:
        # Espace vide pour garder l'alignement
        return html.Div(className="pagination-spacer") 

    return html.Div(
        className="d-flex justify-content-center align-items-center mt-3 gap-3",
        children=[
            dbc.Button(
                "<", 
                id={"type": "pagination-btn", "section": section_id, "action": "prev"}, 
                outline=True, color="secondary", size="sm", 
                disabled=(current_page == 1)
            ),
            html.Span(
                f"Page {current_page} / {total_pages}", 
                className="text-muted small"
            ),
            dbc.Button(
                ">", 
                id={"type": "pagination-btn", "section": section_id, "action": "next"}, 
                outline=True, color="secondary", size="sm", 
                disabled=(current_page == total_pages)
            ),
        ]
    )

# ============================================================
# 3. LAYOUT
# ============================================================

layout = html.Div(
    className="main-container",
    children=[
        # Stores locaux pour gérer la pagination de cette page uniquement
        dcc.Store(id="fav-page-num", data=1),
        dcc.Store(id="rec-page-num", data=1),
        
        # En-tête
        html.Div(
            className="favorites-header-container",
            children=[
                html.H1("Mes Favoris & Recommandations", className="discovery-header-title display-5 fw-bold"),
                html.P("Gérez vos abonnements et découvrez de nouveaux talents.", className="lead text-muted"),
            ]
        ),

        # Zone de contenu dynamique (Liste ou Alerte connexion)
        html.Div(id="favorites-page-content"),
    ],
)

# ============================================================
# 4. CALLBACKS
# ============================================================

@callback(
    Output("favorites-ids-store", "data"),
    Input({"type": "fav-remove-btn", "id": ALL}, "n_clicks"),
    State("favorites-ids-store", "data"),
    prevent_initial_call=True
)
def remove_favorite(n_clicks, current_ids):
    """Gère le clic sur le bouton flottant pour supprimer un favori."""
    if not n_clicks or not any(n_clicks): 
        return no_update
    
    ctx = callback_context
    if not ctx.triggered: 
        return no_update
        
    try:
        clicked_prop = ctx.triggered[0]["prop_id"]
        btn_data = json.loads(clicked_prop.split(".")[0])
        id_to_remove = btn_data["id"]
        # Filtrage de l'ID à supprimer
        return [uid for uid in current_ids if str(uid) != str(id_to_remove)]
    except Exception:
        return no_update

@callback(
    [Output("fav-page-num", "data"), Output("rec-page-num", "data")],
    Input({"type": "pagination-btn", "section": ALL, "action": ALL}, "n_clicks"),
    [State("fav-page-num", "data"), State("rec-page-num", "data")],
    prevent_initial_call=True
)
def update_pagination(n_clicks, fav_p, rec_p):
    """Gère la navigation (page suivante/précédente) pour les deux sections."""
    ctx = callback_context
    if not ctx.triggered: 
        return no_update, no_update
    
    fav_p = fav_p or 1
    rec_p = rec_p or 1
    
    button_id = json.loads(ctx.triggered[0]["prop_id"].split(".")[0])
    section = button_id["section"]
    action = button_id["action"]

    if section == "favorites":
        if action == "prev": fav_p = max(1, fav_p - 1)
        elif action == "next": fav_p += 1
        return fav_p, no_update
        
    elif section == "recommendations":
        if action == "prev": rec_p = max(1, rec_p - 1)
        elif action == "next": rec_p += 1
        return no_update, rec_p
        
    return no_update, no_update

@callback(
    Output("favorites-page-content", "children"),
    [
        Input("favorites-ids-store", "data"), 
        Input("auth-mode", "data"), 
        Input("fav-page-num", "data"),
        Input("rec-page-num", "data")
    ]
)
def render_favorites_page(fav_ids, auth_mode, fav_page, rec_page):
    """Construit le contenu principal de la page."""
    
    # 1. Vérification Connexion
    is_logged_in = (auth_mode == "profile")

    if not is_logged_in:
        return html.Div(
            dbc.Alert(
                [
                    html.H4("🔒 Accès restreint", className="alert-heading"),
                    html.P("Vous devez être connecté pour gérer vos favoris."),
                ],
                color="warning",
            ),
            className="favorites-login-alert"
        )

    content = []

    # 2. Gestion Section Favoris
    all_favorites = get_creators_from_ids(fav_ids)
    
    # Pagination Favoris
    fav_per_page = 4
    fav_total_pages = max(1, (len(all_favorites) + fav_per_page - 1) // fav_per_page)
    fav_page = min(max(1, fav_page or 1), fav_total_pages)
    
    fav_start = (fav_page - 1) * fav_per_page
    current_favorites = all_favorites[fav_start : fav_start + fav_per_page]

    # Rendu Favoris
    if current_favorites:
        fav_display = dbc.Row([render_favorite_item(c) for c in current_favorites], className="g-3")
    else:
        fav_display = html.Div(
            [
                html.I(className="bi bi-heartbreak text-muted mb-2", style={"fontSize": "2rem"}), 
                html.Div("Vous n'avez aucun favori pour le moment.")
            ], 
            className="favorites-empty-state"
        )

    content.append(html.Div([
        html.Div(
            className="section-header h5 fw-bold mb-3 d-flex align-items-center", 
            children=[html.Span("❤️", className="me-2"), f"Mes Favoris ({len(all_favorites)})"]
        ),
        html.Div(fav_display, className="favorites-list-container"),
        make_pagination_controls("favorites", fav_page, fav_total_pages)
    ], className="section-card mb-4 p-4 rounded bg-white border"))

    # 3. Gestion Section Recommandations
    all_recommendations = get_recommendations(fav_ids)
    
    # Pagination Recommandations
    rec_per_page = 2
    rec_total_pages = max(1, (len(all_recommendations) + rec_per_page - 1) // rec_per_page)
    rec_page = min(max(1, rec_page or 1), rec_total_pages)
    
    rec_start = (rec_page - 1) * rec_per_page
    current_recommendations = all_recommendations[rec_start : rec_start + rec_per_page]

    # Rendu Recommandations
    if not all_recommendations:
        rec_display = html.Div("Aucune recommandation disponible.", className="favorites-empty-state")
    else:
        rec_display = dbc.Row(
            [dbc.Col(render_creator_card_compact(c), md=6) for c in current_recommendations], 
            className="g-3"
        )

    content.append(html.Div([
        html.Div(
            className="section-header h5 fw-bold mb-2 d-flex align-items-center", 
            children=[html.Span("✨", className="me-2"), "Recommandé pour vous"]
        ),
        html.P("Basé sur les thématiques de vos favoris.", className="text-muted small mb-3"),
        html.Div(rec_display, className="favorites-list-container"),
        make_pagination_controls("recommendations", rec_page, rec_total_pages)
    ], className="section-card-secondary p-4 rounded bg-light border"))
    
    return content