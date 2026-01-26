from flask import Blueprint, render_template, request, redirect, url_for, send_file
import pandas as pd
import io

from .ml_service import predict_from_dataframe

ui_bp = Blueprint("ui", __name__)

@ui_bp.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        role = request.form["role"]
        return redirect(url_for("ui.dashboard", role=role))

    return render_template("login.html")

@ui_bp.route("/dashboard/<role>", methods=["GET", "POST"])
def dashboard(role):
    if request.method == "POST":
        file = request.files["file"]
        df = pd.read_csv(file)

        df_out = predict_from_dataframe(df)

        output = io.StringIO()
        df_out.to_csv(output, index=False)
        output.seek(0)

        return send_file(
            io.BytesIO(output.getvalue().encode()),
            as_attachment=True,
            download_name="tickets_predicted.csv",
            mimetype="text/csv"
        )

    return render_template("dashboard.html", role=role)
