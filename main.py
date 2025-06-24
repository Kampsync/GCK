import os
import uuid
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

XANO_API_PATCH_BASE = os.environ.get("XANO_API_PATCH_BASE")

@app.route("/generate", methods=["POST"])
def generate_ical_link():
    data = request.get_json()
    if not data or "listing_id" not in data:
        return jsonify({"error": "Missing 'listing_id' in request body"}), 400

    listing_id = data["listing_id"]

    # ✅ Step 1: Generate a random token
    ical_id = uuid.uuid4().hex

    # ✅ Step 2: Build the final iCal URL
    ical_url = f"https://api.kampsync.com/v1/ical/{ical_id}"

    # ✅ Step 3: Send to Xano
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
