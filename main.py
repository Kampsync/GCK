import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

XANO_API_PATCH_BASE = os.environ.get("XANO_API_PATCH_BASE")
ICAL_ID_SERVICE_URL = "https://gck-497309858592.europe-west1.run.app"

@app.route("/generate", methods=["POST"])
def generate_ical_link():
    data = request.get_json()
    if not data or "listing_id" not in data:
        return jsonify({"error": "Missing 'listing_id' in request body"}), 400

    listing_id = data["listing_id"]

    # Step 1: Call the ical ID generation service
    try:
        response = requests.post(ICAL_ID_SERVICE_URL, headers={"Content-Type": "application/json"}, json={})
        response.raise_for_status()
        ical_data = response.json()
        ical_id = ical_data.get("ical_id")
        if not ical_id:
            return jsonify({"error": "No 'ical_id' returned from generator service"}), 500
    except requests.RequestException as e:
        return jsonify({"error": "Failed to generate iCal ID", "details": str(e)}), 500

    # Step 2: Build the final iCal URL
    ical_url = f"https://api.kampsync.com/v1/ical/{ical_id}"

    # Step 3: Send to Xano
    payload = {
        "listing_id": listing_id,
        "kampsync_ical_link": ical_url
    }

    try:
        xano_response = requests.post(XANO_API_PATCH_BASE, json=payload, headers={"Content-Type": "application/json"})
        xano_response.raise_for_status()
        return jsonify({"message": "Successfully updated listing in Xano", "ical_url": ical_url}), 200
    except requests.RequestException as e:
        return jsonify({"error": "Failed to update Xano", "details": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
