import os
import uuid
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

XANO_API_PATCH_BASE = os.environ.get("XANO_API_PATCH_BASE")

@app.route("/generate-ical", methods=["POST"])
def generate_ical_link():
    data = request.get_json()
    if not data or "listing_id" not in data:
        return jsonify({"error": "Missing 'listing_id' in request body"}), 400

    listing_id = data["listing_id"]
    ical_id = uuid.uuid4().hex
    ical_url = f"https://api.kampsync.com/v1/ical/{ical_id}"

    patch_url = f"{XANO_API_PATCH_BASE}/{listing_id}"
    payload = {
        "kampsync_ical_link": ical_url
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        xano_response = requests.patch(patch_url, json=payload, headers=headers)

        if 200 <= xano_response.status_code < 300:
            return jsonify({
                "ical_url": ical_url
            }), 200
        else:
            return jsonify({
                "error": "Xano responded with an error",
                "status_code": xano_response.status_code,
                "xano_response": xano_response.text
            }), xano_response.status_code

    except requests.RequestException as e:
        return jsonify({"error": "Failed to update Xano", "details": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
