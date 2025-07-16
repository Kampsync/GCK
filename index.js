import express from "express";
import axios from "axios";
import { v4 as uuidv4 } from "uuid";
import dotenv from "dotenv";

dotenv.config();

const app = express();
app.use(express.json());

const PORT = process.env.PORT || 3000;
const RENDER_CALENDAR_BASE = process.env.RENDER_CALENDAR_BASE; // must end with /
const XANO_SAVE_API = process.env.XANO_SAVE_API;

const tokenMap = {}; // Replace with database later

app.post("/generate-link", async (req, res) => {
  const { listing_id } = req.body;
  if (!listing_id) return res.status(400).json({ error: "Missing listing_id" });

  const token = uuidv4().replace(/-/g, "").slice(0, 10);
  const ical_url = `https://api.kampsync.com/v1/ical/${token}.ics`;
  tokenMap[token] = listing_id;

  try {
    await axios.post(XANO_SAVE_API, {
      listing_id,
      kampsync_ical_link: ical_url
    });
  } catch (err) {
    console.error("Xano save failed:", err.message);
    return res.status(500).json({ error: "Failed to save iCal to Xano" });
  }

  res.json({ ical_url });
});

app.get("/v1/ical/:token.ics", async (req, res) => {
  const token = req.params.token;
  const listing_id = tokenMap[token];
  if (!listing_id) return res.status(404).send("Invalid iCal token");

  const url = `${RENDER_CALENDAR_BASE}${listing_id}.ics`;

  try {
    const response = await axios.get(url);
    res.set("Content-Type", "text/calendar");
    res.send(response.data);
  } catch (err) {
    console.error("Calendar fetch failed:", err.message);
    res.status(502).send("Failed to fetch calendar");
  }
});

app.listen(PORT, () => console.log(`iCal server running on port ${PORT}`));
