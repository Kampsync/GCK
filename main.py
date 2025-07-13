import os
import uuid
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Base URLs to interact with the Xano API
XANO_API_GET_BASE = os.environ.get("XANO_API_GET_BASE")
XANO_API_PATCH_BASE = os.environ.get("XANO_API_PATCH_BASE")

@app.route("/generate-ical", methods=["POST"])
def generate_ical_link():
    """Return a stable iCal URL for the given listing.

    If the listing already has a stored `kampsync_ical_link` in Xano it is
    returned unchanged. Otherwise a new URL is generated, stored in Xano and
    returned to the caller.
    """
    data = request.get_json(silent=True) or request.form
    if not data or "listing_id" not in data:
        return jsonify({"error": "Missing 'listing_id' in request body"}), 400

    listing_id = data["listing_id"]

    # 1) Try to fetch an existing link from Xano
    try:
        get_response = requests.get(f"{XANO_API_GET_BASE}{listing_id}")
        get_response.raise_for_status()
        record = get_response.json()

        # Xano might return a list or a single object
        if isinstance(record, list):
            record = record[0] if record else {}
        if isinstance(record, dict):
            existing = record.get("kampsync_ical_link")
            if existing:
                return jsonify({"ical_url": existing}), 200
    except requests.RequestException as exc:
        app.logger.warning("Failed to fetch listing %s from Xano: %s", listing_id, exc)
        # continue to generate a new link

    # 2) Create and store a new link
    ical_id = uuid.uuid4().hex
    ical_url = f"https://api.kampsync.com/v1/ical/{ical_id}"

    payload = {
        "listing_id": listing_id,
        "kampsync_ical_link": ical_url,
    }

    try:
        patch_response = requests.post(XANO_API_PATCH_BASE, json=payload)
        patch_response.raise_for_status()
    except requests.RequestException as exc:
        app.logger.error("Failed to save iCal link to Xano: %s", exc)
        return jsonify({"error": "Failed to save ical link"}), 500

    return jsonify({"ical_url": ical_url}), 201


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
