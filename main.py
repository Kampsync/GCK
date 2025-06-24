import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

XANO_API_PATCH_BASE = os.environ.get("XANO_API_PATCH_BASE")

@app.route("/create-kampsync-ical", methods=["POST"])
def create_kampsync_ical():
    data = request.get_json()
    if not data or "listing_id" not in data or "ical_id" not in data:
        return jsonify({"error": "Missing 'listing_id' or 'ical_id' in request body"}), 400

    listing_id = data["listing_id"]
    ical_id = data["ical_id"]

    ical_url = f"https://api.kampsync.com/v1/ical/{ical_id}"

    payload = {
        "listing_id": listing_id,
        "kampsync_ical_link": ical_url
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        xano_response = requests.post(XANO_API_PATCH_BASE, json=payload, headers=headers)
        xano_response.raise_for_status()
        return jsonify({"message": "Successfully updated listing in Xano", "ical_url": ical_url}), 200
    except requests.RequestException as e:
        return jsonify({"error": "Failed to update Xano", "details": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
