import express from "express";
import axios from "axios";
import { v4 as uuidv4 } from "uuid";

const app = express();
app.use(express.json());

const XANO_API_GET_BASE = process.env.XANO_API_GET_BASE;
const XANO_API_PATCH_BASE = process.env.XANO_API_PATCH_BASE;

app.post("/generate-ical", async (req, res) => {
  const listing_id = req.query.listing_id;

  if (!listing_id) {
    return res.status(400).json({ ical_url: "ERROR: Missing 'listing_id'" });
  }

  try {
    let existingLink = null;

    // GET existing kampsync_ical_link from Xano
    if (XANO_API_GET_BASE) {
      const getUrl = `${XANO_API_GET_BASE}?listing_id=${listing_id}`;
      const getResponse = await axios.get(getUrl);

      if (Array.isArray(getResponse.data)) {
        existingLink = getResponse.data[0]?.kampsync_ical_link || null;
      } else if (typeof getResponse.data === "object") {
        existingLink = getResponse.data.kampsync_ical_link || null;
      }
    }

    // If link already exists, return it
    if (existingLink && typeof existingLink === "string" && existingLink.trim()) {
      return res.status(200).json({ ical_url: existingLink });
    }

    // Otherwise create new link
    const icalId = uuidv4();
    const kampsyncLink = `https://api.kampsync.com/v1/ical/${icalId}`;

    // PATCH new link into Xano
    if (XANO_API_PATCH_BASE) {
      await axios.patch(
        `${XANO_API_PATCH_BASE}?listing_id=${listing_id}`,
        { kampsync_ical_link: kampsyncLink },
        { headers: { "Content-Type": "application/json" } }
      );
    }

    return res.status(201).json({ ical_url: kampsyncLink });

  } catch (err) {
    console.error("SERVER ERROR:", err);
    return res.status(500).json({ ical_url: `ERROR: ${err.message || "unknown error"}` });
  }
});

const port = process.env.PORT || 8080;
app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});
