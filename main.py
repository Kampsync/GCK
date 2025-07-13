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

    listing_id = str(data["listing_id"])

    # GET the listing record
    get_url = f"{XANO_API_GET_BASE}{listing_id}"
    get_response = requests.get(get_url)
    get_response.raise_for_status()
    record = get_response.json()
    if isinstance(record, list):
        record = record[0] if record else {}

    # If it already has a link, return it
    existing_link = record.get("kampsync_ical_link")
    if existing_link and isinstance(existing_link, str) and existing_link.strip():
        return jsonify({"ical_url": existing_link}), 200

    # Otherwise, create a new permanent link and patch it
    ical_id = uuid.uuid4().hex
    kampsync_link = f"https://api.kampsync.com/v1/ical/{ical_id}"

    patch_url = f"{XANO_API_PATCH_BASE}{listing_id}"
    patch_payload = {"kampsync_ical_link": kampsync_link}
    requests.patch(
        patch_url,
        json=patch_payload,
        headers={"Content-Type": "application/json"}
    )

    return jsonify({"ical_url": kampsync_link}), 201

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
