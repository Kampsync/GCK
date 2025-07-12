import os
import uuid
import threading
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

XANO_API_PATCH_BASE = os.environ.get("XANO_API_PATCH_BASE")

def async_patch(payload, headers):
    try:
        requests.post(XANO_API_PATCH_BASE, json=payload, headers=headers)
    except requests.RequestException:
        pass  # fail silently

@app.route("/generate-ical", methods=["POST"])
def generate_ical_link():
    # Accept either JSON or form data from Xano
    data = request.get_json(silent=True) or request.form

    if not data or "listing_id" not in data:
        return jsonify({"error": "Missing 'listing_id' in request body"}), 400

    listing_id = data["listing_id"]
    ical_id = uuid.uuid4().hex
    ical_url = f"https://api.kampsync.com/v1/ical/{ical_id}"

    payload = {
        "listing_id": listing_id,
        "kampsync_ical_link": ical_url
    }

    headers = {
        "Content-Type": "application/json"
    }

    # Launch patch in a separate thread so we return immediately
    threading.Thread(target=async_patch, args=(payload, headers)).start()

    return jsonify({"ical_url": ical_url}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
