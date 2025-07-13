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

    if (XANO_API_GET_BASE) {
      const getUrl = `${XANO_API_GET_BASE}?listing_id=${listing_id}`;
      const getResponse = await axios.get(getUrl);
      const record = Array.isArray(getResponse.data)
        ? getResponse.data[0] || {}
        : getResponse.data;
      existingLink = record.kampsync_ical_link;
    }

    if (existingLink && existingLink.trim()) {
      return res.status(200).json({ ical_url: existingLink });
    }

    const icalId = uuidv4();
    const kampsyncLink = `https://api.kampsync.com/v1/ical/${icalId}`;

    if (XANO_API_PATCH_BASE) {
      await axios.patch(
        `${XANO_API_PATCH_BASE}?listing_id=${listing_id}`,
        { kampsync_ical_link: kampsyncLink },
        { headers: { "Content-Type": "application/json" } }
      );
    }

    return res.status(201).json({ ical_url: kampsyncLink });

  } catch (err) {
    console.error("ERROR:", err.message);
    return res
      .status(500)
      .json({ ical_url: `ERROR: ${err.message || "unknown error"}` });
  }
});

const port = process.env.PORT || 8080;
app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});
