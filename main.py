import os
import uuid
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

XANO_API_PATCH_BASE = os.getenv("XANO_API_PATCH_BASE")

def generate_token():
    return uuid.uuid4().hex[:24]

@app.route("/generate", methods=["POST"])
def generate_ical():
    data = request.get_json()
    listing_id = data.get("listing_id")
    if not listing_id:
        return jsonify({"error": "Missing listing_id"}), 400

    token = generate_token()
    ical_url = f"https://api.kampsync.com/v1/ical/{token}"

    try:
        payload = {
            "listing_id": listing_id,
            "kampsync_ical_link": ical_url,
            "ical_token": token
        }
        response = requests.post(XANO_API_PATCH_BASE, json=payload)
        response.raise_for_status()
    except Exception as e:
        return jsonify({"error": f"Failed to save iCal link: {str(e)}"}), 500

    return jsonify({"ical_link": ical_url})
