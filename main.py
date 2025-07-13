import os
import uuid
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

XANO_API_GET_LISTING_BASE = os.environ.get("XANO_API_GET_LISTING_BASE")  # your Listings DB endpoint base
XANO_API_PATCH_EVENTS_URL = os.environ.get("XANO_API_PATCH_EVENTS_URL")  # static booking_events_1 URL

@app.route("/generate-ical", methods=["POST"])
def generate_ical_link():
    data = request.get_json(silent=True) or request.form
    if not data or "listing_id" not in data:
        return jsonify({"error": "Missing 'listing_id' in request body"}), 400

    listing_id = str(data["listing_id"])

    try:
        # Always pull the record from Listings table
        get_url = f"{XANO_API_GET_LISTING_BASE}{listing_id}"
        get_response = requests.get(get_url)
        get_response.raise_for_status()
        record = get_response.json()

        if isinstance(record, list):
            record = record[0] if record else {}

        if not isinstance(record, dict):
            return jsonify({"error": "Invalid Listings record format"}), 500

        existing_link = record.get("kampsync_ical_link")
        render_link = record.get("ical_data_render")

        if not render_link or not render_link.strip():
            return jsonify({"error": "Missing 'ical_data_render' in Listings record"}), 400

        if existing_link and isinstance(existing_link, str) and existing_link.strip():
            return jsonify({
                "ical_url": existing_link,
                "backing_render_link": render_link
            }), 200

        # Generate new KampSync style link
        ical_id = uuid.uuid4().hex
        kampsync_link = f"https://api.kampsync.com/v1/ical/{ical_id}"

        # Patch to static booking_events_1
        patch_payload = {
            "kampsync_ical_link": kampsync_link
        }

        patch_response = requests.patch(
            XANO_API_PATCH_EVENTS_URL,
            json=patch_payload,
            headers={"Content-Type": "application/json"}
        )
        patch_response.raise_for_status()

        return jsonify({
            "ical_url": kampsync_link,
            "backing_render_link": render_link
        }), 201

    except requests.RequestException as e:
        return jsonify({"error": f"Failed to process: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
