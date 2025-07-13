 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a/main.py b/main.py
index 97e9244af2bb95c62c6d12403720b5a295c0ef59..0b751af7f816b2e8568cc89bb868fc4255cb173d 100644
--- a/main.py
+++ b/main.py
@@ -1,65 +1,63 @@
 import os
 import uuid
-import threading
 from flask import Flask, request, jsonify
 import requests
 
 app = Flask(__name__)
 
 XANO_API_GET_BASE = os.environ.get("XANO_API_GET_BASE")  # e.g. https://xfxa-cldj-sxth.n7e.xano.io/api:yHTBBmYY/booking_events_1?listing_id=
 XANO_API_PATCH_BASE = os.environ.get("XANO_API_PATCH_BASE")
 
-def async_patch(payload, headers):
-    try:
-        requests.post(XANO_API_PATCH_BASE, json=payload, headers=headers)
-    except requests.RequestException:
-        pass  # fail silently
-
 @app.route("/generate-ical", methods=["POST"])
 def generate_ical_link():
     data = request.get_json(silent=True) or request.form
     if not data or "listing_id" not in data:
         return jsonify({"error": "Missing 'listing_id' in request body"}), 400
 
     listing_id = data["listing_id"]
 
     # Check Xano if there is already a kampsync_ical_link
     try:
         get_response = requests.get(f"{XANO_API_GET_BASE}{listing_id}")
         get_response.raise_for_status()
         records = get_response.json()
 
         # If it's a list, scan each item
         if isinstance(records, list):
             for record in records:
                 existing_link = record.get("kampsync_ical_link")
                 if existing_link:
                     return jsonify({"ical_url": existing_link}), 200
         # If it's a dict (single object)
         elif isinstance(records, dict):
             existing_link = records.get("kampsync_ical_link")
             if existing_link:
                 return jsonify({"ical_url": existing_link}), 200
 
     except requests.RequestException:
         pass  # If GET fails, just proceed to create a new one
 
     # If nothing found, create new link
     ical_id = uuid.uuid4().hex
     ical_url = f"https://api.kampsync.com/v1/ical/{ical_id}"
 
     payload = {
         "listing_id": listing_id,
         "kampsync_ical_link": ical_url
     }
     headers = {
         "Content-Type": "application/json"
     }
 
-    threading.Thread(target=async_patch, args=(payload, headers)).start()
+    try:
+        patch_response = requests.post(XANO_API_PATCH_BASE, json=payload, headers=headers)
+        patch_response.raise_for_status()
+    except requests.RequestException as exc:
+        app.logger.error("Failed to save iCal link to Xano: %s", exc)
+        return jsonify({"error": "Failed to save ical link"}), 500
 
     return jsonify({"ical_url": ical_url}), 200
 
 if __name__ == "__main__":
     port = int(os.environ.get("PORT", 8080))
     app.run(host="0.0.0.0", port=port)
 
EOF
)
