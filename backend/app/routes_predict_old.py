from flask import Blueprint, request, jsonify, send_file
import pandas as pd
import io

from .ml_service import predict_from_dataframe

predict_bp = Blueprint("predict", __name__)

@predict_bp.route("/predict/csv", methods=["POST"])
def predict_csv():
    if "file" not in request.files:
        return jsonify({"error": "Nessun file caricato"}), 400

    file = request.files["file"]

    if not file.filename.endswith(".csv"):
        return jsonify({"error": "Il file deve essere un CSV"}), 400

    try:
        df = pd.read_csv(file)
        df_out = predict_from_dataframe(df)

        output = io.StringIO()
        df_out.to_csv(output, index=False)
        output.seek(0)

        return send_file(
            io.BytesIO(output.getvalue().encode("utf-8")),
            mimetype="text/csv",
            as_attachment=True,
            download_name="tickets_predicted.csv"
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500
