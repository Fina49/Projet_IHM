"""
Page Découverte.

Ce module affiche les tendances et nouveautés :
1. Créateurs (cartes compactes).
2. Hashtags/Tags (cartes simples).
3. Vidéos (cartes vidéos).
Le contenu change dynamiquement via des onglets (Tabs).
"""

import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc

# Import des données et composants réutilisables
from constants import (
    TRENDING_CREATORS, NEW_CREATORS, 
    TRENDING_TOPICS, NEW_TAGS, 
    TRENDING_VIDEOS, NEW_VIDEOS
)
from functions import (
    render_creator_card_compact, 
    render_topic_card, 
    render_video_card
)

dash.register_page(__name__, path="/discover", name="Découverte")

# ============================================================
# 1. FONCTIONS UTILITAIRES (HELPERS UI LOCAUX)
# ============================================================

def build_grid(data, card_func, grid_type="creators", fav_list=None):
    """
    Construit une grille Bootstrap (Row > Col) contenant les cartes.
    
    Args:
        data: Liste de données (dicts).
        card_func: Fonction de rendu de carte (importée de functions.py).
        grid_type: Type de grille pour ajuster la largeur des colonnes.
        fav_list: Liste des IDs favoris pour marquer les cœurs (créateurs uniquement).
    """
    if grid_type == "tags":
        # Les tags ont un layout CSS spécifique (Grid CSS)
        return html.Div(className="topics-grid", children=[card_func(x) for x in data])
    
    # Ajustement de la largeur : 3 cartes par ligne pour vidéos, 2 pour créateurs
    col_width = 4 if grid_type == "videos" else 6
    
    items = []
    for x in data:
        # Injection dynamique de l'état "is_favorite" si c'est un créateur
        if grid_type == "creators":
            is_fav = str(x['id']) in (fav_list or [])
            comp = card_func(x, is_favorite=is_fav)
        else:
            comp = card_func(x)
            
        items.append(dbc.Col(comp, md=col_width))

    return dbc.Row(className="g-3", children=items)

def make_section(title, icon, data, card_func, grid_type="creators", is_secondary=False, add_margin=True, fav_list=None):
    """
    Génère une section complète avec titre, icône et contenu.
    """
    content = build_grid(data, card_func, grid_type, fav_list)
    
    # Classes CSS dynamiques
    container_cls = "section-card-secondary" if is_secondary else "section-card"
    if add_margin:
        container_cls += " section-spacer" # Ajout de la marge via CSS
        
    # Combinaison des classes existantes dans styles.css
    final_class = f"{container_cls} p-4 rounded-3 border"

    return html.Div(
        className=final_class,
        children=[
            html.Div(
                className="section-header h5 fw-bold mb-3 d-flex align-items-center", 
                children=[html.Span(icon, className="me-2"), title]
            ),
            content
        ]
    )

# ============================================================
# 2. LAYOUT DE LA PAGE
# ============================================================

layout = html.Div(
    className="main-container",
    children=[
        # En-tête
        html.Div(
            className="discovery-header-container",
            children=[
                html.H1("Découverte", className="discovery-header-title display-5 fw-bold"),
                html.P("Explorez les dernières tendances.", className="lead text-muted")
            ]
        ),

        # Onglets de navigation
        dcc.Tabs(
            id="discover-tabs",
            value="trending",
            className="dash-tabs mb-4",
            children=[
                dcc.Tab(label="Tendances", value="trending"),
                dcc.Tab(label="Nouveaux", value="new")
            ]
        ),

        # Conteneur du contenu dynamique
        html.Div(id="discover-tab-content", className="trending-section"),
    ]
)

# ============================================================
# 3. CALLBACKS
# ============================================================

@callback(
    Output("discover-tab-content", "children"),
    [Input("discover-tabs", "value"), Input("auth-mode", "data")],
    State("favorites-ids-store", "data")
)
def render_discover_tab(tab_value, auth_mode, fav_ids):
    """
    Met à jour le contenu principal selon l'onglet choisi (Tendances vs Nouveaux).
    Vérifie l'état des favoris pour afficher les cœurs correctement.
    """
    # Vérification si l'utilisateur est connecté pour afficher ses favoris
    is_logged_in = (auth_mode == "profile")
    my_favs = [str(uid) for uid in (fav_ids or [])] if is_logged_in else []
    
    # Configuration des sections : (Titre, Icône, Données, Fonction Rendu, Type Grille, Secondaire?)
    # Note : On limite l'affichage aux premiers éléments ([:2], [:3]) pour ne pas surcharger la page
    
    if tab_value == "trending":
        sections_config = [
            ("Créateurs en Tendance", "↗", TRENDING_CREATORS[:2], render_creator_card_compact, "creators", False),
            ("Tags en Tendance", "🔥", TRENDING_TOPICS, render_topic_card, "tags", True),
            ("Vidéos en Tendance", "▶️", TRENDING_VIDEOS[:3], render_video_card, "videos", False),
        ]
    else: # tab == "new"
        sections_config = [
            ("Nouveaux Créateurs", "✨", NEW_CREATORS[:2], render_creator_card_compact, "creators", False),
            ("Nouveaux Tags", "🏷️", NEW_TAGS, render_topic_card, "tags", True),
            ("Nouvelles Vidéos", "🆕", NEW_VIDEOS[:3], render_video_card, "videos", False),
        ]

    # Génération du HTML
    html_sections = []
    for i, (title, icon, data, func, gtype, is_sec) in enumerate(sections_config):
        # On ajoute une marge supérieure à toutes les sections sauf la première (i > 0)
        html_sections.append(
            make_section(title, icon, data, func, gtype, is_sec, add_margin=(i > 0), fav_list=my_favs)
        )

    return html_sections