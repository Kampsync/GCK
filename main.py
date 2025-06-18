from flask import Flask, request, Response, jsonify
import os
from utils.token import generate_token
from utils.ics_generator import create_ics
import requests

app = Flask(__name__)

XANO_API_BASE = os.getenv("XANO_API_BASE")

@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    listing_id = data.get("listing_id")

    if not listing_id:
        return jsonify({"error": "listing_id is required"}), 400

    token = generate_token()
    xano_listing_url = f"{XANO_API_BASE}/listings/{listing_id}"

    listing_resp = requests.get(xano_listing_url)
    if listing_resp.status_code != 200:
        return jsonify({"error": "Listing not found"}), 404

    listing = listing_resp.json()
    listing["ical_token"] = token

    # Save the token back to Xano
    update_resp = requests.patch(xano_listing_url, json={"ical_token": token})
    if update_resp.status_code != 200:
        return jsonify({"error": "Failed to update Xano"}), 500

    ical_link = f"https://www.kampsync.com/api/{token}.ics"
    return jsonify({"ical_link": ical_link}), 201


@app.route("/<token>.ics", methods=["GET"])
def serve_ical(token):
    query_url = f"{XANO_API_BASE}/listings"
    resp = requests.get(query_url, params={"ical_token": token})
    data = resp.json()

    if not data:
        return jsonify({"error": "Invalid token"}), 404

    listing = data[0]
    ical_data = create_ics(listing)

    return Response(ical_data, mimetype='text/calendar')


if __name__ == "__main__":
    app.run()
