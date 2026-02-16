from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    send_file
)
import pandas as pd
import tempfile
from werkzeug.security import check_password_hash

from app.models.user import User
from app.services.ticket_service import save_ticket
from app.ml_service import predict_single_ticket
from app.models.ticket import Ticket
from sqlalchemy import func
from datetime import datetime, timedelta

ui_bp = Blueprint("ui", __name__)
ROLE_CATEGORY_MAP = {
    "assistenza": "Tecnico",
    "commerciale": "Commerciale",
    "contabile": "Contabile"
}

# ======================
# Helper login/admin
# ======================
def login_required():
    return "user_id" in session


def admin_required():
    return login_required() and session.get("role") == "admin"


# ======================
# LOGIN
# ======================
@ui_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        if not user or not check_password_hash(user.password_hash, password):
            flash("Credenziali non valide", "danger")
            return redirect(url_for("ui.login"))

        session.clear()
        session["user_id"] = user.id
        session["username"] = user.username
        session["role"] = user.role

        return redirect(url_for("ui.dashboard"))

    return render_template("login.html")


# ======================
# DASHBOARD
# ======================
@ui_bp.route("/", methods=["GET"])
def dashboard():
    if not login_required():
        return redirect(url_for("ui.login"))

    return render_template(
        "dashboard.html",
        user=session.get("username"),
        role=session.get("role")
    )


# ======================
# UPLOAD CSV (ADMIN)
# ======================
@ui_bp.route("/ticket/upload", methods=["POST"])
def upload_csv():
    if not admin_required():
        return redirect(url_for("ui.dashboard"))

    file = request.files.get("file")
    if not file:
        return render_template(
            "dashboard.html",
            message="Nessun file selezionato",
            user=session.get("username"),
            role=session.get("role")
        )

    # Lettura CSV robusta
    df = pd.read_csv(
        file,
        sep=",",
        quotechar='"',
        engine="python"
    )

    # Normalizza colonne
    df.columns = [c.strip().lower() for c in df.columns]

    # subject -> title
    if "subject" in df.columns and "title" not in df.columns:
        df = df.rename(columns={"subject": "title"})

    required = {"title", "body"}
    if not required.issubset(df.columns):
        raise ValueError(
            f"Il CSV deve contenere le colonne: title, body (trovate: {df.columns})"
        )

    results = []

    for _, row in df.iterrows():
        title = "" if pd.isna(row.get("title")) else str(row.get("title"))
        body = "" if pd.isna(row.get("body")) else str(row.get("body"))

        pred = predict_single_ticket(title, body)

        # salva nel DB DOPO classificazione
        save_ticket(
            prediction=pred,
            source="csv",
            username=session.get("username")
        )

        results.append(pred)

    out_df = pd.DataFrame(results)

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
    out_df.to_csv(tmp.name, index=False)

    return send_file(
        tmp.name,
        as_attachment=True,
        download_name="ticket_classificati.csv"
    )


# ======================
# NUOVO TICKET
# ======================
@ui_bp.route("/ticket/new", methods=["GET"])
def new_ticket():
    if not admin_required():
        return redirect(url_for("ui.dashboard"))

    return render_template("ticket_form.html")


# ======================
# PREDIZIONE SINGOLA
# ======================
@ui_bp.route("/ticket/predict", methods=["POST"])
def predict_ticket():
    if not admin_required():
        return redirect(url_for("ui.dashboard"))

    title = request.form.get("title", "")
    body = request.form.get("body", "")

    result = predict_single_ticket(title, body)

    # salva nel DB
    save_ticket(
        prediction=result,
        source="manual",
        username=session.get("username")
    )

    df = pd.DataFrame([result])

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
    df.to_csv(tmp.name, index=False)

    return send_file(
        tmp.name,
        as_attachment=True,
        download_name="ticket_classificato.csv"
    )
# ======================
# STORICO TICKET
# ======================



from app.models.ticket import Ticket



@ui_bp.route("/tickets", methods=["GET"])
def ticket_history():
    if not login_required():
        return redirect(url_for("ui.login"))

    role = session.get("role")

    # filtri da querystring
    category_f = request.args.get("category")
    priority_f = request.args.get("priority")
    source_f = request.args.get("source")
    date_from = request.args.get("date_from")
    date_to = request.args.get("date_to")

    query = Ticket.query

    # filtro per ruolo
    if role != "admin":
        category = ROLE_CATEGORY_MAP.get(role)
        if category:
            query = query.filter(Ticket.category == category)
        else:
            query = query.filter(False)

    # filtri opzionali
    if category_f:
        query = query.filter(Ticket.category == category_f)

    if priority_f:
        query = query.filter(Ticket.priority == priority_f)

    if source_f:
        query = query.filter(Ticket.source == source_f)

    if date_from:
        query = query.filter(Ticket.created_at >= date_from)

    if date_to:
        query = query.filter(Ticket.created_at <= date_to)

    tickets = query.order_by(Ticket.created_at.desc()).all()

    return render_template(
        "ticket_history.html",
        tickets=tickets,
        role=role,
        filters={
            "category": category_f,
            "priority": priority_f,
            "source": source_f,
            "date_from": date_from,
            "date_to": date_to
        }
    )

@ui_bp.route("/dashboard/stats", methods=["GET"])
def dashboard_stats():
    if not login_required():
        return redirect(url_for("ui.login"))

    role = session.get("role")
    period = request.args.get("period", "all")

    query = Ticket.query

    # filtro per ruolo
    if role != "admin":
        category = ROLE_CATEGORY_MAP.get(role)
        if category:
            query = query.filter(Ticket.category == category)
        else:
            query = query.filter(False)

    # filtro temporale
    if period in {"7", "30", "90"}:
        days = int(period)
        date_from = datetime.utcnow() - timedelta(days=days)
        query = query.filter(Ticket.created_at >= date_from)

    # ======================
    # KPI BASE
    # ======================
    total = query.count()

    avg_cat_conf = query.with_entities(
        func.avg(Ticket.category_confidence)
    ).scalar() or 0

    avg_prio_conf = query.with_entities(
        func.avg(Ticket.priority_confidence)
    ).scalar() or 0

    # ======================
    # KPI AVANZATI
    # ======================
    high_priority_count = query.filter(
        Ticket.priority == "alta"
    ).count()

    percentuale_alta_priorita = (
        round((high_priority_count / total) * 100, 1)
        if total > 0 else 0
    )

    ticket_critici = query.filter(
        Ticket.category_confidence < 0.6
    ).count()

    top_category = (
        query.with_entities(
            Ticket.category,
            func.count(Ticket.id).label("cnt")
        )
        .group_by(Ticket.category)
        .order_by(func.count(Ticket.id).desc())
        .first()
    )

    categoria_dominante = top_category[0] if top_category else "N/A"

    last_7_days = datetime.utcnow() - timedelta(days=7)
    nuovi_ticket_7_giorni = query.filter(
        Ticket.created_at >= last_7_days
    ).count()

    # ======================
    # GRAFICI
    # ======================
    by_category = (
        query.with_entities(Ticket.category, func.count(Ticket.id))
        .group_by(Ticket.category)
        .all()
    )

    by_priority = (
        query.with_entities(Ticket.priority, func.count(Ticket.id))
        .group_by(Ticket.priority)
        .all()
    )

    by_source = (
        query.with_entities(Ticket.source, func.count(Ticket.id))
        .group_by(Ticket.source)
        .all()
    )

    daily = (
        query.with_entities(
            func.date_trunc("day", Ticket.created_at).label("day"),
            func.count(Ticket.id)
        )
        .group_by("day")
        .order_by("day")
        .all()
    )

    # ======================
    # DATA PER TEMPLATE
    # ======================
    data = {
        "totale_ticket": total,
        "conf_categoria_media": round(float(avg_cat_conf), 3),
        "conf_priorita_media": round(float(avg_prio_conf), 3),

        "percentuale_alta_priorita": percentuale_alta_priorita,
        "ticket_critici": ticket_critici,
        "categoria_dominante": categoria_dominante,
        "nuovi_ticket_7_giorni": nuovi_ticket_7_giorni,

        "by_category": [{"label": k, "value": v} for k, v in by_category],
        "by_priority": [{"label": k, "value": v} for k, v in by_priority],
        "by_source": [{"label": k, "value": v} for k, v in by_source],
        "daily": [{"label": d.strftime("%Y-%m-%d"), "value": c} for d, c in daily],

        "period": period
    }

    return render_template(
        "dashboard_stats.html",
        role=role,
        data=data
    )



# ======================
# LOGOUT
# ======================
@ui_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("ui.login"))
