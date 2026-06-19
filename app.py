from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

IBM_API_KEY = os.environ.get("IBM_API_KEY")
SIMPLE_SCORING_URL = os.environ.get("SIMPLE_SCORING_URL")
ADVANCED_SCORING_URL = os.environ.get("ADVANCED_SCORING_URL")


def get_iam_token():
    response = requests.post(
        "https://iam.cloud.ibm.com/identity/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
            "apikey": IBM_API_KEY
        },
        timeout=20
    )
    response.raise_for_status()
    return response.json()["access_token"]


def call_watson_model(scoring_url, fields, values):
    token = get_iam_token()

    payload = {
        "input_data": [
            {
                "fields": fields,
                "values": [values]
            }
        ]
    }

    response = requests.post(
        scoring_url,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        },
        json=payload,
        timeout=30
    )

    response.raise_for_status()
    result = response.json()

    prediction = result["predictions"][0]["values"][0][0]

    return prediction


@app.route("/", methods=["GET"])
def home():
    return "Energy Prediction API is running"


@app.route("/predict-energy-simple", methods=["POST"])
def predict_energy_simple():
    data = request.json

    fields = [
        "Batch",
        "Production Quantity",
        "Screw Speed",
        "Melt Pressure",
        "Cooling Time"
    ]

    values = [
        "BATCH_001",
        data["Production_Quantity"],
        data["Screw_Speed"],
        data["Melt_Pressure"],
        data["Cooling_Time"]
    ]

    prediction = call_watson_model(
        SIMPLE_SCORING_URL,
        fields,
        values
    )

    return jsonify({
        "prediction_type": "simple",
        "predicted_energy": prediction
    })


@app.route("/predict-energy-advanced", methods=["POST"])
def predict_energy_advanced():
    data = request.json

    fields = [
        "Batch",
        "Production Quantity",
        "Screw Speed",
        "Melt Pressure",
        "Cooling Time",
        "Seal Temperature",
        "Barrel Temperature",
        "Fill Speed"
    ]

    values = [
        "BATCH_001",
        data["Production_Quantity"],
        data["Screw_Speed"],
        data["Melt_Pressure"],
        data["Cooling_Time"],
        data["Seal_Temperature"],
        data["Barrel_Temperature"],
        data["Fill_Speed"]
    ]

    prediction = call_watson_model(
        ADVANCED_SCORING_URL,
        fields,
        values
    )

    return jsonify({
        "prediction_type": "advanced",
        "predicted_energy": prediction
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
