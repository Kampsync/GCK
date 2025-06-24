import os
import uuid
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Load Xano base URL from environment variable
XANO_API_PATCH_BASE = os.environ.get("XANO_API_PATCH_BASE")

@app.route("/generate-ical", methods=["POST"])
def generate_ical():
    data = request.json
    listing_id = data.get("listing_id")

    if not listing_id:
        return jsonify({"error": "listing_id is required"}), 400

    # Generate a unique iCal ID and link
    ical_id = str(uuid.uuid4())
    ical_link = f"https://api.kampsync.com/v1/ical/{ical_id}"

    # Patch it into Xano
    xano_patch_url = f"{XANO_API_PATCH_BASE}/{listing_id}"
    payload = {
        "kampsync_ical_link": ical_link
    }

    try:
        res = requests.patch(xano_patch_url, json=payload)
        res.raise_for_status()
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "listing_id": listing_id,
        "kampsync_ical_link": ical_link
    }), 200
