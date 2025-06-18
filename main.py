# main.py

import os
import uuid
import requests
from flask import Flask, request, jsonify, Response
from datetime import datetime, timedelta

app = Flask(__name__)

XANO_API_BASE = os.getenv("XANO_API_BASE")


def generate_token():
    return uuid.uuid4().hex[:24]


def create_ics(listing):
    now = datetime.utcnow()
    end = now + timedelta(hours=1)

    uid = listing.get("ical_token", generate_token())
    summary = listing.get("title", "Booking")
    location = listing.get("location", "")
    description = listing.get("description", "")
    dtstamp = now.strftime("%Y%m%dT%H%M%SZ")
    dtstart = now.strftime("%Y%m%dT%H%M%SZ")
    dtend = end.strftime("%Y%m%dT%H%M%SZ")

    ical = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Kampsync//EN
CALSCALE:GREGORIAN
BEGIN:VEVENT
UID:{uid}
SUMMARY:{summary}
DESCRIPTION:{description}
LOCATION:{location}
DTSTAMP:{dtstamp}
DTSTART:{dtstart}
DTEND:{dtend}
END:VEVENT
END:VCALENDAR
"""
    return ical


@app.route("/generate", methods=["POST"])
def generate_ical():
    data = request.get_json()
    listing_id = data.get("listing_id")

    if not listing_id:
        return jsonify({"error": "Missing listing_id"}), 400

    # Fetch listing data
    try:
        listing = requests.get(f"{XANO_API_BASE}/listings/{listing_id}").json()
    except Exception as e:
        return jsonify({"error": f"Failed to fetch listing: {str(e)}"}), 500

    # Generate and assign token
    token = generate_token()

    # Save token to listing
    try:
        requests.patch(f"{XANO_API_BASE}/listings/{listing_id}", json={"ical_token": token})
    except Exception as e:
        return jsonify({"error": f"Failed to update Xano: {str(e)}"}), 500

    # Return permanent URL
    ical_url = f"https://www.kampsync.com/api/{token}.ics"
    return jsonify({"ical_link": ical_url})


@app.route("/api/<token>.ics", methods=["GET"])
def get_ical(token):
    try:
        response = requests.get(f"{XANO_API_BASE}/listings", params={"ical_token": token})
        listings = response.json()

        if not listings:
            return "Calendar not found", 404

        ical_data = create_ics(listings[0])
        return Response(ical_data, mimetype="text/calendar")
    except Exception as e:
        return f"Error: {str(e)}", 500


# Required for Cloud Run
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
