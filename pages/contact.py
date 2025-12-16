"""
Page de Contact.

Ce module affiche un formulaire de contact avec :
1. Validation des champs (Email regex, longueur du message).
2. Feedback visuel des erreurs.
3. Modale de confirmation d'envoi.
"""

import re
import dash
from dash import html, callback, Input, Output, State, callback_context, no_update
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

dash.register_page(__name__, path="/contact", name="Nous Contacter")

# ============================================================
# 1. UI HELPERS
# ============================================================

def render_form_field(label, comp_id, placeholder, kind="text", margin_top=True):
    """
    Génère un bloc de formulaire standard (Label + Input/Textarea + Zone Erreur).
    """
    label_cls = "mt-3" if margin_top else ""
    
    if kind == "textarea":
        component = dbc.Textarea(
            id=comp_id, 
            placeholder=placeholder, 
            className="contact-textarea" # Style extrait
        )
    else:
        component = dbc.Input(
            id=comp_id, 
            type=kind, 
            placeholder=placeholder
        )

    return html.Div([
        dbc.Label(label, className=label_cls),
        component,
        html.Div(id=f"{comp_id}-feedback", className="field-error")
    ])

# ============================================================
# 2. LAYOUT
# ============================================================

layout = html.Div(
    className="main-container contact-page-container",
    children=[
        html.Div(
            className="contact-form-wrapper",
            children=[
                html.H2("Nous Contacter"),
                html.P("Une question, une suggestion ? N'hésitez pas à nous écrire !"),

                # ---- FORMULAIRE ----
                dbc.Card(
                    className="contact-card",
                    children=dbc.CardBody([
                        render_form_field("Adresse e-mail *", "contact-email", "vous@example.com", kind="email", margin_top=False),
                        render_form_field("Objet *", "contact-subject", "Objet de votre message", kind="text"),
                        render_form_field("Message *", "contact-message", "Décrivez votre demande en détail...", kind="textarea"),

                        dbc.Button(
                            "Envoyer le message",
                            id="contact-send-btn",
                            color="dark",
                            className="mt-3",
                        ),
                        html.Div(id="contact-status", className="mt-3"),
                    ])
                ),
            ]
        ),

        # ---- MODAL DE CONFIRMATION ----
        dbc.Modal(
            id="contact-modal",
            is_open=False,
            centered=True,
            backdrop="static",
            children=[
                dbc.ModalHeader(dbc.ModalTitle("Message envoyé")),
                dbc.ModalBody(
                    html.Div("Merci ! Votre message a bien été envoyé.", className="contact-modal-text")
                ),
                dbc.ModalFooter(
                    dbc.Button("Fermer", id="contact-close-btn", color="dark")
                ),
            ],
        ),
    ]
)

# ============================================================
# 3. CALLBACKS
# ============================================================

@callback(
    [
        Output("contact-modal", "is_open"),
        Output("contact-email-feedback", "children"),
        Output("contact-subject-feedback", "children"),
        Output("contact-message-feedback", "children"),
        # Outputs pour vider les champs après envoi
        Output("contact-email", "value"),
        Output("contact-subject", "value"),
        Output("contact-message", "value"),
    ],
    [
        Input("contact-send-btn", "n_clicks"),
        Input("contact-close-btn", "n_clicks"),
    ],
    [
        State("contact-modal", "is_open"),
        State("contact-email", "value"),
        State("contact-subject", "value"),
        State("contact-message", "value"),
    ],
)
def handle_contact_form(send_click, close_click, is_open, email, subject, message):
    """
    Gère la soumission du formulaire :
    1. Validation des entrées (Regex Email, Longueur message).
    2. Affichage des erreurs ou ouverture de la modale de succès.
    3. Réinitialisation du formulaire en cas de succès.
    """
    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate

    button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    # --- Cas 1 : Fermeture de la modal ---
    if button_id == "contact-close-btn":
        # Fermeture, pas d'erreurs, pas de changement des valeurs (no_update)
        return False, "", "", "", no_update, no_update, no_update

    # --- Cas 2 : Tentative d'envoi ---
    if button_id == "contact-send-btn":
        
        # Nettoyage des entrées
        email_val = (email or "").strip()
        subject_val = (subject or "").strip()
        message_val = (message or "").strip()

        # Regex Email standard
        email_pattern = r"^[^@]+@[^@]+\.[^@]+$"

        # Gestion des erreurs
        errs = {"email": "", "subject": "", "message": ""}

        if not email_val:
            errs["email"] = "L'adresse e-mail est requise."
        elif not re.match(email_pattern, email_val):
            errs["email"] = "Format invalide (ex: nom@domaine.com)."

        if not subject_val:
            errs["subject"] = "L'objet du message est requis."
        elif len(subject_val) < 3:
            errs["subject"] = "L'objet est trop court."

        if not message_val:
            errs["message"] = "Le message ne peut pas être vide."
        elif len(message_val) < 10:
            errs["message"] = "Votre message est trop court (min. 10 caractères)."

        # S'il y a des erreurs -> On les affiche, on garde la modal fermée
        if any(errs.values()):
            return is_open, errs["email"], errs["subject"], errs["message"], no_update, no_update, no_update

        # Succès -> On ouvre la modal, on vide les erreurs, on vide les champs
        return True, "", "", "", "", "", ""

    raise PreventUpdate