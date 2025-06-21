import os
import uuid
import requests
from flask import Flask, request, jsonify, Response
from ics import Calendar
from datetime import datetime

app = Flask(__name__)

XANO_API_GET_BASE = os.getenv("XANO_API_GET_BASE")
XANO_API_PATCH_BASE = os.getenv("XANO_API_PATCH_BASE")


def generate_token():
    return uuid.uuid4().hex[:24]


def fetch_calendar(url: str):
    try:
        res = requests.get(url)
        if res.status_code == 200:
            return Calendar(res.text)
    except Exception:
        pass
    return None


@app.route("/generate", methods=["POST"])
def generate_ical():
    data = request.get_json()
    listing_id = data.get("listing_id")
    if not listing_id:
        return jsonify({"error": "Missing listing_id"}), 400

    try:
        listing_url = f"{XANO_API_GET_BASE}/{listing_id}"
        listing = requests.get(listing_url).json()
    except Exception as e:
        return jsonify({"error": f"Failed to fetch listing: {str(e)}"}), 500

    token = generate_token()
    ical_url = f"https://api.kampsync.com/v1/ical/{token}"

    # Save link to Xano
    try:
        payload = {
            "listing_id": listing_id,
            "kampsync_ical_link": ical_url,
            "ical_token": token
        }
        requests.post(XANO_API_PATCH_BASE, json=payload)
    except Exception as e:
        return jsonify({"error": f"Failed to save iCal link: {str(e)}"}), 500

    return jsonify({"ical_link": ical_url})


@app.route("/v1/ical/<token>", methods=["GET"])
def get_ical(token):
    try:
        query_url = f"{XANO_API_GET_BASE}?ical_token={token}"
        response = requests.get(query_url)
        listings = response.json()
        if not listings:
            return "Calendar not found", 404

        listing = listings[0]
        ical_sources = [
            listing.get("rvshare_ical_link"),
            listing.get("outdoorsy_ical_link"),
            listing.get("airbnb_ical_link"),
            listing.get("rvezy_ical_link"),
            listing.get("hipcamp_ical_link"),
            listing.get("camplify_ical_link"),
            listing.get("yescapa_ical_link")
        ]

        calendar = Calendar()
        for url in filter(None, ical_sources):
            fetched = fetch_calendar(url)
            if fetched:
                for event in fetched.events:
                    calendar.events.add(event)

        return Response(str(calendar), mimetype="text/calendar")

    except Exception as e:
        return f"Error: {str(e)}", 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
