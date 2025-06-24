@app.route("/generate-ical", methods=["POST"])
def generate_ical_link():
    data = request.get_json()
    if not data or "listing_id" not in data:
        return jsonify({"error": "Missing 'listing_id' in request body"}), 400

    listing_id = data["listing_id"]
    ical_id = uuid.uuid4().hex
    ical_url = f"https://api.kampsync.com/v1/ical/{ical_id}"

    payload = {
        "listing_id": listing_id,
        "kampsync_ical_link": ical_url
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(XANO_API_PATCH_BASE, json=payload, headers=headers)

        return jsonify({
            "ical_url": ical_url,
            "xano_status_code": response.status_code,
            "xano_response_text": response.text
        }), 200

    except requests.RequestException as e:
        return jsonify({"error": "Unable to connect to Xano", "details": str(e)}), 500
