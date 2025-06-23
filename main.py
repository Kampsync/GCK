import os
import uuid
import requests
from flask import Flask, request, jsonify, Response
from datetime import datetime

app = Flask(__name__)

XANO_API_GET_BASE = os.getenv("XANO_API_GET_BASE")
XANO_API_PATCH_BASE = os.getenv("XANO_API_PATCH_BASE")


def generate_token():
    return uuid.uuid4().hex[:24]


def create_ics(listing):
    title = listing.get("title", "Kampsync Listing")
    location = listing.get("location", "")
    description = listing.get("description", "")
    bookings = listing.get("bookings", [])

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Kampsync//EN",
        "CALSCALE:GREGORIAN"
    ]

    for booking in bookings:
        try:
            dtstart = datetime.fromisoformat(booking["start"].replace("Z", "+00:00")).strftime("%Y%m%dT%H%M%SZ")
            dtend = datetime.fromisoformat(booking["end"].replace("Z", "+00:00")).strftime("%Y%m%dT%H%M%SZ")
            uid = uuid.uuid4().hex
            dtstamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

            lines += [
                "BEGIN:VEVENT",
                f"UID:{uid}",
                f"SUMMARY:{title}",
                f"DESCRIPTION:{description}",
                f"LOCATION:{location}",
                f"DTSTAMP:{dtstamp}",
                f"DTSTART:{dtstart}",
                f"DTEND:{dtend}",
                "END:VEVENT"
            ]
        except Exception:
            continue

    lines.append("END:VCALENDAR")
    return "\n".join(lines)


@app.route("/generate", methods=["POST"])
def generate_ical():
    data = request.get_json()
    listing_id = data.get("listing_id")
    if not listing_id:
        return jsonify({"error": "Missing listing_id"}), 400

    try:
        query_url = f"{XANO_API_GET_BASE}?id={listing_id}"
        listing_data = requests.get(query_url).json()
        if not listing_data:
            return jsonify({"error": "Listing not found"}), 404
        listing = listing_data[0]
    except Exception as e:
        return jsonify({"error": f"Failed to fetch listing: {str(e)}"}), 500

    token = generate_token()
    ical_url = f"https://api.kampsync.com/v1/ical/{token}"

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
        response = requests.get(XANO_API_GET_BASE)
        listings = response.json()

        listing = next((l for l in listings if l.get("ical_token") == token), None)
        if not listing:
            return "Calendar not found", 404

        ical_data = create_ics(listing)
        return Response(ical_data, mimetype="text/calendar")
    except Exception as e:
        return Response(f"Error: {str(e)}", status=500)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
