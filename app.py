"""
Module principal de l'application Dash "Find Your Creator".

Ce module gère :
1. L'initialisation de l'application.
2. La structure globale (Layout) incluant la barre de navigation et le pied de page.
3. La gestion des Stores (mémoire locale) pour l'authentification et les favoris.
"""

import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

# Import des données
from constants import ALL_CREATORS

# Import du module d’authentification
# On importe auth_status pour l'utiliser directement dans le layout
from auth import (
    auth_modal,
    auth_status,
    register_auth_callbacks,
)

# ============================================================
# 1. INITIALISATION
# ============================================================

# Récupération des favoris initiaux depuis la base de données simulée
initial_fav_ids = [c["id"] for c in ALL_CREATORS if c.get("is_favorite")]

app = dash.Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP],
    suppress_callback_exceptions=True
)

# ============================================================
# 2. COMPOSANTS D'INTERFACE (UI)
# ============================================================

def create_navbar():
    """
    Génère la barre de navigation supérieure.
    Utilise les classes définies dans styles.css (.navbar-main, .navbar-link, etc.)
    """
    return dbc.Navbar(
        class_name="navbar-main",
        color="white",
        dark=False,
        children=dbc.Container(
            fluid=False,
            children=[
                # --- Logo & Titre ---
                dbc.NavbarBrand(
                    dcc.Link(
                        html.Div(
                            # "d-flex align-items-center" est une classe utilitaire Bootstrap standard
                            className="d-flex align-items-center",
                            children=[
                                # Le style de ce cercle est ajouté dans le CSS manquant (voir plus bas)
                                html.Div("Q", className="navbar-logo-circle"),
                                html.Span("Find Your Creator", className="navbar-brand-text"),
                            ],
                        ),
                        href="/",
                        # Classe ajoutée pour retirer le soulignement du lien (voir CSS manquant)
                        className="navbar-brand-link"
                    )
                ),

                # --- Menu Central ---
                dbc.Nav(
                    [
                        # On applique la classe .navbar-link définie dans votre CSS
                        dbc.NavLink("Accueil", href="/", active="exact", class_name="navbar-link"),
                        dbc.NavLink("Recherche", href="/search", active="exact", class_name="navbar-link"),
                        dbc.NavLink("Découverte", href="/discover", active="exact", class_name="navbar-link"),
                        dbc.NavLink("Mes Favoris", href="/favorites", active="exact", class_name="navbar-link"),
                    ],
                    navbar=True,
                    className="navbar-center",
                ),

                # --- Bouton Connexion (Droite) ---
                dbc.Nav(
                    [
                        dbc.NavItem(
                            html.Button(
                                children=[
                                    html.Div(className="navbar-profile-icon"),
                                    html.Span("Se connecter", id="navbar-auth-text", className="navbar-auth-text"),
                                ],
                                id="open-auth-modal",
                                className="navbar-auth-button",
                            )
                        )
                    ],
                    navbar=True,
                    className="ms-auto",
                ),
            ],
        ),
    )

def create_footer():
    """
    Génère le pied de page (Footer).
    Utilise les classes .footer-main, .footer-title, etc.
    """
    return html.Div(
        className="footer-main",
        children=dbc.Row(
            className="main-container",
            children=[
                dbc.Col(md=4, className="footer-column", children=[
                    html.Div("Find Your Creator", className="footer-title"),
                    html.Div("Découvrez et analysez les meilleurs créateurs de contenu sur TikTok et YouTube."),
                ]),
                dbc.Col(md=4, className="footer-column", children=[
                    html.Div("Contact", className="footer-title"),
                    dcc.Link(
                        "✉️ Nous contacter", 
                        href="/contact", 
                        className="contact-link-button"
                    ),
                ]),
                dbc.Col(md=4, className="footer-column", children=[
                    html.Div("Suivez-nous", className="footer-title"),
                    html.Div("Instagram · TikTok · YouTube · LinkedIn"),
                ]),
            ],
        ),
    )

# ============================================================
# 3. LAYOUT GLOBAL
# ============================================================

app.layout = html.Div(
    [
        # --- Gestion des Données (Stores) ---
        dcc.Store(id="favorites-ids-store", data=initial_fav_ids, storage_type="local"),
        dcc.Store(id="auth-mode", data="login"), 
        
        # Store persistant pour l'utilisateur connecté
        dcc.Store(
            id="auth-user-store",
            storage_type="local",
            data={
                "is_logged_in": False,
                "firstname": "",
                "lastname": "",
                "email": "",
            },
        ),

        # Composant technique d'authentification (importé depuis auth.py)
        # Il sert de trigger pour certains callbacks et contient l'état caché
        auth_status,

        # --- Structure Visuelle ---
        create_navbar(),
        auth_modal,          # La modale (cachée par défaut)
        dash.page_container, # Contenu des pages chargé dynamiquement
        create_footer(), 
    ]
)

# ============================================================
# 4. ENREGISTREMENT DES CALLBACKS
# ============================================================

register_auth_callbacks(app)

if __name__ == "__main__":
    app.run(debug=True)