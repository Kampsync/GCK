import os
import uuid
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

XANO_API_GET_BASE = os.environ.get("XANO_API_GET_BASE")
XANO_API_PATCH_BASE = os.environ.get("XANO_API_PATCH_BASE")

print("DEBUG ENV: XANO_API_GET_BASE =", XANO_API_GET_BASE)
print("DEBUG ENV: XANO_API_PATCH_BASE =", XANO_API_PATCH_BASE)

@app.route("/generate-ical", methods=["POST"])
def generate_ical_link():
    data = request.get_json(silent=True) or request.form
    if not data or "listing_id" not in data:
        return jsonify({"error": "Missing 'listing_id' in request body"}), 400

    listing_id = str(data["listing_id"])

    try:
        # GET the listing record
        get_url = f"{XANO_API_GET_BASE}{listing_id}"
        print("DEBUG GET URL:", get_url)
        get_response = requests.get(get_url)
        get_response.raise_for_status()
        record = get_response.json()

        if isinstance(record, list):
            record = record[0] if record else {}

        if not isinstance(record, dict):
            return jsonify({"error": "Invalid Listings record format"}), 500

        existing_link = record.get("kampsync_ical_link")

        # If already exists, return it
        if existing_link and isinstance(existing_link, str) and existing_link.strip():
            print("DEBUG Existing kampsync_ical_link found:", existing_link)
            return jsonify({"ical_url": existing_link}), 200

        # Otherwise, create new permanent link
        ical_id = uuid.uuid4().hex
        kampsync_link = f"https://api.kampsync.com/v1/ical/{ical_id}"
        print("DEBUG New kampsync_link:", kampsync_link)

        # PATCH the same listing record
        patch_url = f"{XANO_API_PATCH_BASE}{listing_id}"
        print("DEBUG PATCH URL:", patch_url)
        patch_payload = {"kampsync_ical_link": kampsync_link}

        patch_response = requests.patch(
            patch_url,
            json=patch_payload,
            headers={"Content-Type": "application/json"}
        )
        patch_response.raise_for_status()

        return jsonify({"ical_url": kampsync_link}), 201

    except requests.RequestException as e:
        print("DEBUG Exception:", str(e))
        return jsonify({"error": f"Failed to process: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
