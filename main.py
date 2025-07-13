import os
import uuid
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

XANO_API_GET_BASE = os.environ.get("XANO_API_GET_BASE")   # e.g. https://xano/api:booking_events_1
XANO_API_PATCH_BASE = os.environ.get("XANO_API_PATCH_BASE")  # same style

@app.route("/generate-ical", methods=["POST"])
def generate_ical_link():
    data = request.get_json(silent=True) or request.form
    if not data or "listing_id" not in data:
        return jsonify({"ical_url": "ERROR: Missing 'listing_id'"}), 400

    listing_id = str(data["listing_id"])

    try:
        existing_link = None

        # GET with ?listing_id= param
        if XANO_API_GET_BASE:
            get_url = f"{XANO_API_GET_BASE}?listing_id={listing_id}"
            get_response = requests.get(get_url)
            get_response.raise_for_status()
            record = get_response.json()
            if isinstance(record, list):
                record = record[0] if record else {}
            existing_link = record.get("kampsync_ical_link")

        # If it already has a link, return it
        if existing_link and isinstance(existing_link, str) and existing_link.strip():
            return jsonify({"ical_url": existing_link}), 200

        # Otherwise, create a new permanent link
        ical_id = uuid.uuid4().hex
        kampsync_link = f"https://api.kampsync.com/v1/ical/{ical_id}"

        # PATCH with ?listing_id= param
        if XANO_API_PATCH_BASE:
            patch_url = f"{XANO_API_PATCH_BASE}?listing_id={listing_id}"
            patch_payload = {"kampsync_ical_link": kampsync_link}
            requests.patch(
                patch_url,
                json=patch_payload,
                headers={"Content-Type": "application/json"}
            )

        return jsonify({"ical_url": kampsync_link}), 201

    except Exception as e:
        return jsonify({"ical_url": f"ERROR: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
