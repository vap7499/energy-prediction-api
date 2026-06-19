from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

IBM_API_KEY = os.environ.get("IBM_API_KEY")
SCORING_URL = os.environ.get("SCORING_URL")

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

@app.route("/predict-energy", methods=["POST"])
def predict_energy():
    data = request.json

    fields = [
        "Production_Quantity",
        "Barrel_Temperature_Zone3_C",
        "Screw_Speed_RPM",
        "Melt_Pressure_bar",
        "Air_Pressure_bar",
        "Cooling_Time_sec",
        "Seal_Temperature_C",
        "Relative_Humidity_percent",
        "Melt_Flow_Index"
    ]

    values = [[
        data["Production_Quantity"],
        data["Barrel_Temperature_Zone3_C"],
        data["Screw_Speed_RPM"],
        data["Melt_Pressure_bar"],
        data["Air_Pressure_bar"],
        data["Cooling_Time_sec"],
        data["Seal_Temperature_C"],
        data["Relative_Humidity_percent"],
        data["Melt_Flow_Index"]
    ]]

    token = get_iam_token()

    payload = {
        "input_data": [
            {
                "fields": fields,
                "values": values
            }
        ]
    }

    response = requests.post(
        SCORING_URL,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json=payload,
        timeout=30
    )

    response.raise_for_status()
    result = response.json()

    prediction = result["predictions"][0]["values"][0][0]

    return jsonify({
        "predicted_energy": prediction
    })

@app.route("/", methods=["GET"])
def home():
    return "Energy Prediction API is running"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)