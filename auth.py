"""
Module d'Authentification.

Ce module contient :
1. La définition de la modale d'authentification (Login / Signup / Profile).
2. Les fonctions helpers pour la gestion des modes d'affichage.
3. Le callback principal gérant la logique de connexion et la persistance utilisateur.
"""

import re
from dash import html, dcc, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

# ============================================================
# 1. COMPOSANTS DE LA MODALE
# ============================================================

# Formulaire de Connexion
login_form = html.Div(
    id="auth-login-form",
    children=[
        dbc.Form(
            [
                dbc.Label("Adresse e-mail"),
                dbc.Input(id="auth-login-email", type="email", placeholder="ex: jean@mail.com"),
                html.Div(id="auth-login-email-error", className="field-error"),

                dbc.Label("Mot de passe", className="mt-3"),
                dbc.Input(id="auth-login-password", type="password", placeholder="•••••••"),
                html.Div(id="auth-login-password-error", className="field-error"),
            ]
        )
    ],
)

# Formulaire d'Inscription
signup_form = html.Div(
    id="auth-signup-form",
    style={"display": "none"}, # Caché par défaut
    children=[
        dbc.Form(
            [
                dbc.Label("Prénom"),
                dbc.Input(id="auth-signup-firstname", type="text", placeholder="ex: Jean"),
                html.Div(id="auth-signup-firstname-error", className="field-error"),

                dbc.Label("Nom", className="mt-3"),
                dbc.Input(id="auth-signup-lastname", type="text", placeholder="ex: Dupont"),
                html.Div(id="auth-signup-lastname-error", className="field-error"),

                dbc.Label("Adresse e-mail", className="mt-3"),
                dbc.Input(id="auth-signup-email", type="email", placeholder="ex: jean@mail.com"),
                html.Div(id="auth-signup-email-error", className="field-error"),

                dbc.Label("Mot de passe", className="mt-3"),
                dbc.Input(id="auth-signup-password", type="password", placeholder="Choisissez un mot de passe"),
                html.Div(id="auth-signup-password-error", className="field-error"),
            ]
        )
    ],
)

# Formulaire de Profil (Modification)
profile_form = html.Div(
    id="auth-profile-form",
    style={"display": "none"}, # Caché par défaut
    children=[
        html.Div(
            [
                html.H5("Mes informations personnelles", className="fw-bold mb-2"),
                html.P("Modifiez vos coordonnées ci-dessous.", className="text-muted small mb-4"),
            ]
        ),
        dbc.Form(
            [
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Prénom"),
                        dbc.Input(id="auth-profile-firstname", type="text"),
                        html.Div(id="auth-profile-firstname-error", className="field-error"),
                    ], md=6),
                    dbc.Col([
                        dbc.Label("Nom"),
                        dbc.Input(id="auth-profile-lastname", type="text"),
                        html.Div(id="auth-profile-lastname-error", className="field-error"),
                    ], md=6),
                ], className="mb-3"),

                dbc.Label("Adresse e-mail"),
                dbc.Input(id="auth-profile-email", type="email"),
                html.Div(id="auth-profile-email-error", className="field-error"),
            ]
        )
    ],
)

# Assemblage de la Modale
auth_modal = dbc.Modal(
    id="auth-modal",
    is_open=False,
    centered=True,
    backdrop="static",
    children=[
        dbc.ModalHeader(dbc.ModalTitle(id="auth-modal-title")),
        dbc.ModalBody([login_form, signup_form, profile_form]),
        dbc.ModalFooter(
            [
                dbc.Button("Annuler", id="auth-cancel-btn", outline=True, color="secondary"),
                dbc.Button("Se connecter", id="auth-submit-btn", color="dark"),
                html.Button(
                    "Pas encore de compte ? S’inscrire",
                    id="auth-switch-mode-btn",
                    className="auth-switch-link",
                ),
            ]
        ),
    ],
)

# Composant technique caché pour stocker l'état (Connecté/Déconnecté)
# Utilisé comme trigger dans d'autres callbacks
auth_status = html.Div(id="auth-status", className="d-none")


# ============================================================
# 2. HELPER FUNCTIONS
# ============================================================

def get_mode_config(mode: str):
    """
    Retourne la configuration d'affichage (Styles et Textes) selon le mode actif.
    
    Args:
        mode (str): "login", "signup" ou "profile".
        
    Returns:
        tuple: (style_login, style_signup, style_profile, titre_modal, texte_btn_submit, texte_btn_switch)
    """
    show = {"display": "block"}
    hide = {"display": "none"}
    
    if mode == "signup":
        return (
            hide, show, hide,
            "Créer un compte", "Créer mon compte", "Déjà un compte ? Se connecter"
        )
    elif mode == "profile":
        return (
            hide, hide, show,
            "Mon Profil", "Enregistrer les modifications", "Se déconnecter"
        )
    
    # Par défaut : Login
    return (
        show, hide, hide,
        "Se connecter", "Se connecter", "Pas encore de compte ? S’inscrire"
    )

def extract_name_from_email(email):
    """Extrait un nom d'affichage basique depuis l'email (ex: jean@mail.com -> Jean)."""
    if not email or "@" not in email:
        return "Utilisateur", "Utilisateur"
    local_part = email.split("@")[0]
    name = local_part.capitalize()
    return name, name


# ============================================================
# 3. CALLBACK PRINCIPAL
# ============================================================

def register_auth_callbacks(app):
    """
    Enregistre le callback principal de gestion de l'authentification.
    Doit être appelé dans app.py après l'initialisation de l'app.
    """

    @app.callback(
        [
            Output("auth-modal", "is_open"),
            Output("auth-mode", "data"),
            Output("auth-login-form", "style"),
            Output("auth-signup-form", "style"),
            Output("auth-profile-form", "style"),
            Output("auth-modal-title", "children"),
            Output("auth-submit-btn", "children"),
            Output("auth-switch-mode-btn", "children"),
            
            # Feedbacks erreurs
            Output("auth-login-email-error", "children"),
            Output("auth-login-password-error", "children"),
            Output("auth-signup-firstname-error", "children"),
            Output("auth-signup-lastname-error", "children"),
            Output("auth-signup-email-error", "children"),
            Output("auth-signup-password-error", "children"),
            Output("auth-profile-firstname-error", "children"),
            Output("auth-profile-lastname-error", "children"),
            Output("auth-profile-email-error", "children"),
            
            # État global et UI Navbar
            Output("auth-status", "children"),
            Output("navbar-auth-text", "children"),
            
            # Valeurs du formulaire Profil
            Output("auth-profile-firstname", "value"),
            Output("auth-profile-lastname", "value"),
            Output("auth-profile-email", "value"),
            
            # Persistance
            Output("auth-user-store", "data"),
        ],
        [
            Input("open-auth-modal", "n_clicks"),
            Input("auth-cancel-btn", "n_clicks"),
            Input("auth-submit-btn", "n_clicks"),
            Input("auth-switch-mode-btn", "n_clicks"),
            Input("auth-user-store", "data"), # Déclenchement au chargement page
        ],
        [
            State("auth-modal", "is_open"),
            State("auth-mode", "data"),
            # Champs formulaires
            State("auth-login-email", "value"),
            State("auth-login-password", "value"),
            State("auth-signup-firstname", "value"),
            State("auth-signup-lastname", "value"),
            State("auth-signup-email", "value"),
            State("auth-signup-password", "value"),
            State("auth-profile-firstname", "value"),
            State("auth-profile-lastname", "value"),
            State("auth-profile-email", "value"),
            State("navbar-auth-text", "children"),
            State("auth-status", "children"),
            State("auth-user-store", "data"),
        ],
    )
    def handle_auth(open_click, cancel_click, submit_click, switch_click, user_store_input,
                    is_open, mode,
                    login_email, login_password,
                    su_firstname, su_lastname, su_email, su_password,
                    prof_firstname, prof_lastname, prof_email,
                    nav_label_state, current_status_text,
                    user_store_state):
        
        ctx = callback_context
        if not ctx.triggered:
            raise PreventUpdate

        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

        # Initialisation par défaut
        mode = mode or "login"
        navbar_label = nav_label_state or "Se connecter"
        status = current_status_text or ""
        logged_in = (navbar_label != "Se connecter")

        # Récupération état utilisateur (localStorage)
        user_store = user_store_state or user_store_input or {
            "is_logged_in": logged_in,
            "firstname": prof_firstname or "",
            "lastname": prof_lastname or "",
            "email": prof_email or "",
        }

        # Reset erreurs
        login_email_err = login_pw_err = ""
        su_fn_err = su_ln_err = su_email_err = su_pw_err = ""
        prof_fn_err = prof_ln_err = prof_email_err = ""

        modal_open = is_open or False
        email_pattern = r"^[^@]+@[^@]+\.[^@]+$"

        # -------------------------------------------------
        # 1. SYNC AU CHARGEMENT (Persistence)
        # -------------------------------------------------
        if button_id == "auth-user-store":
            if user_store.get("is_logged_in"):
                mode = "profile"
                navbar_label = user_store.get("firstname") or "Compte"
                status = "Connecté"
                prof_firstname = user_store.get("firstname") or ""
                prof_lastname = user_store.get("lastname") or ""
                prof_email = user_store.get("email") or ""
            else:
                mode = "login"
                navbar_label = "Se connecter"
                status = ""
                prof_firstname = prof_lastname = prof_email = ""

            # Configuration affichage
            style_l, style_s, style_p, title, txt_sub, txt_sw = get_mode_config(mode)

            return (
                False, mode, style_l, style_s, style_p, title, txt_sub, txt_sw,
                "","","","","","","","","", # Pas d'erreurs
                status, navbar_label,
                prof_firstname, prof_lastname, prof_email,
                user_store
            )

        # -------------------------------------------------
        # 2. GESTION DES CLICS
        # -------------------------------------------------

        # Ouvrir la modal
        if button_id == "open-auth-modal":
            mode = "profile" if logged_in else "login"
            modal_open = True

        # Fermer (Annuler)
        elif button_id == "auth-cancel-btn":
            modal_open = False

        # Switch Mode / Déconnexion
        elif button_id == "auth-switch-mode-btn":
            if mode == "login":
                mode, modal_open = "signup", True
            elif mode == "signup":
                mode, modal_open = "login", True
            else:
                # DECONNEXION
                navbar_label = "Se connecter"
                status = "Déconnecté"
                mode, modal_open = "login", False
                prof_firstname = prof_lastname = prof_email = ""
                user_store = {"is_logged_in": False, "firstname": "", "lastname": "", "email": ""}

        # Soumission (Connexion / Inscription / Update)
        elif button_id == "auth-submit-btn":
            
            # --- Cas LOGIN ---
            if mode == "login":
                ok = True
                if not login_email: login_email_err, ok = "Requis.", False
                elif not re.match(email_pattern, login_email): login_email_err, ok = "Format invalide.", False
                if not login_password: login_pw_err, ok = "Requis.", False

                if ok:
                    # Simulation Connexion réussie
                    generated_first, generated_last = extract_name_from_email(login_email)
                    navbar_label = generated_first
                    status = "Connecté"
                    prof_email = login_email
                    prof_firstname, prof_lastname = generated_first, generated_last
                    
                    mode, modal_open = "profile", False
                    user_store = {"is_logged_in": True, "firstname": prof_firstname, "lastname": prof_lastname, "email": prof_email}
                else:
                    modal_open = True

            # --- Cas SIGNUP ---
            elif mode == "signup":
                ok = True
                if not su_firstname: su_fn_err, ok = "Requis.", False
                if not su_lastname: su_ln_err, ok = "Requis.", False
                if not su_email: su_email_err, ok = "Requis.", False
                elif not re.match(email_pattern, su_email): su_email_err, ok = "Invalide.", False
                if not su_password: su_pw_err, ok = "Requis.", False

                if ok:
                    # Simulation Inscription réussie
                    navbar_label = su_firstname
                    status = "Connecté"
                    prof_firstname, prof_lastname, prof_email = su_firstname, su_lastname, su_email
                    
                    mode, modal_open = "profile", False
                    user_store = {"is_logged_in": True, "firstname": prof_firstname, "lastname": prof_lastname, "email": prof_email}
                else:
                    modal_open = True

            # --- Cas PROFIL (Update) ---
            else:
                ok = True
                if not prof_firstname: prof_fn_err, ok = "Requis.", False
                if not prof_lastname: prof_ln_err, ok = "Requis.", False
                if not prof_email: prof_email_err, ok = "Requis.", False
                elif not re.match(email_pattern, prof_email): prof_email_err, ok = "Invalide.", False

                if ok:
                    # Simulation Mise à jour réussie
                    navbar_label = prof_firstname
                    status = "Connecté"
                    modal_open = False
                    user_store = {"is_logged_in": True, "firstname": prof_firstname, "lastname": prof_lastname, "email": prof_email}
                else:
                    modal_open = True

        # Configuration finale de l'affichage
        style_l, style_s, style_p, title, txt_sub, txt_sw = get_mode_config(mode)

        return (
            modal_open, mode, style_l, style_s, style_p, title, txt_sub, txt_sw,
            login_email_err, login_pw_err,
            su_fn_err, su_ln_err, su_email_err, su_pw_err,
            prof_fn_err, prof_ln_err, prof_email_err,
            status, navbar_label,
            prof_firstname, prof_lastname, prof_email,
            user_store
        )