# 🗓️ Kampsync iCal Generator (Google Cloud Function)

This Google Cloud Function dynamically generates iCalendar `.ics` links for listings stored in Xano.

---

## ✨ Features

- Randomized token-based links: `https://www.kampsync.com/api/<token>.ics`
- Fetch listing data from Xano using listing ID
- Generate valid `.ics` calendar files on the fly
- Save the generated token back into the Xano listings table

---

## 📤 Endpoints

### `POST /generate`

Generates a new `.ics` link for a given listing.

```json
{
  "request": {
    "listing_id": "abc123"
  },
  "response": {
    "ical_link": "https://www.kampsync.com/api/AbcD0Fic3aXjKmoo.ics"
  }
}
