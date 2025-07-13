import os
import uuid
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

XANO_API_GET_BASE = os.environ.get("XANO_API_GET_BASE")
XANO_API_PATCH_BASE = os.environ.get("XANO_API_PATCH_BASE")

@app.route("/generate-ical", methods=["POST"])
def generate_ical_link():
    data = request.get_json(silent=True) or request.form
    if not data or "listing_id" not in data:
        return jsonify({"error": "Missing 'listing_id' in request body"}), 400

    listing_id = data["listing_id"]

    try:
        get_response = requests.get(f"{XANO_API_GET_BASE}{listing_id}")
        get_response.raise_for_status()
        record = get_response.json()

        if isinstance(record, list):
            record = record[0] if record else {}

        existing = record.get("kampsync_ical_link") if isinstance(record, dict) else None

        if existing and isinstance(existing, str) and existing.strip():
            return jsonify({"ical_url": existing}), 200

        ical_id = uuid.uuid4().hex
        ical_url = f"https://api.kampsync.com/v1/ical/{ical_id}"

        patch_payload = {
            "listing_id": listing_id,
            "kampsync_ical_link": ical_url
        }

        patch_response = requests.post(
            f"{XANO_API_PATCH_BASE}{listing_id}",
            json=patch_payload,
            headers={"Content-Type": "application/json"}
        )
        patch_response.raise_for_status()

        # Fetch again to verify it saved
        verify_response = requests.get(f"{XANO_API_GET_BASE}{listing_id}")
        verify_response.raise_for_status()
        updated_record = verify_response.json()
        saved_url = updated_record.get("kampsync_ical_link") if isinstance(updated_record, dict) else ical_url

        return jsonify({"ical_url": saved_url}), 201

    except requests.RequestException as e:
        return jsonify({"error": f"Failed to process listing: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
