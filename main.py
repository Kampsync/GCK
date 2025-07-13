import os
import uuid
import threading
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

XANO_API_GET_BASE = os.environ.get("XANO_API_GET_BASE")  # e.g. https://xfxa-cldj-sxth.n7e.xano.io/api:yHTBBmYY/booking_events_1?listing_id=
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

    # Check Xano if this listing already has a kampsync_ical_link
    try:
        get_response = requests.get(f"{XANO_API_GET_BASE}{listing_id}")
        get_response.raise_for_status()
        listing_data = get_response.json()
        existing_link = listing_data.get("kampsync_ical_link")
        if existing_link:
            return jsonify({"ical_url": existing_link}), 200
    except requests.RequestException:
        pass  # if GET fails, continue to create new

    # Create new if not exists
    ical_id = uuid.uuid4().hex
    ical_url = f"https://api.kampsync.com/v1/ical/{ical_id}"

    payload = {
        "listing_id": listing_id,
        "kampsync_ical_link": ical_url
    }

    headers = {
        "Content-Type": "application/json"
    }

    threading.Thread(target=async_patch, args=(payload, headers)).start()

    return jsonify({"ical_url": ical_url}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
