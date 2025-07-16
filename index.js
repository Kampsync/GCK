import express from "express";
import axios from "axios";
import { v4 as uuidv4 } from "uuid";
import dotenv from "dotenv";

dotenv.config();

const app = express();
app.use(express.json());

const PORT = process.env.PORT || 8080;

const RENDER_CALENDAR_BASE = process.env.RENDER_CALENDAR_BASE;
const XANO_SAVE_API = process.env.XANO_SAVE_API;
const XANO_TOKEN_LOOKUP_API = process.env.XANO_TOKEN_LOOKUP_API;

app.get("/", (req, res) => {
  res.send("KampSync iCal Service is live");
});

// STEP 1: Generate unique token, save it + link in Xano
app.post("/generate-link", async (req, res) => {
  const { listing_id } = req.body;
  if (!listing_id) return res.status(400).json({ error: "Missing listing_id" });

  const token = uuidv4().replace(/-/g, "").slice(0, 10);
  const ical_url = `https://api.kampsync.com/v1/ical/${token}.ics`;

  try {
    await axios.post(XANO_SAVE_API, {
      listing_id,
      ical_token: token,
      kampsync_ical_link: ical_url
    });
  } catch (err) {
    console.error("Xano save failed:", err.message);
    return res.status(500).json({ error: "Failed to save iCal to Xano" });
  }

  res.json({ ical_url });
});

// STEP 2: Serve iCal based on token → lookup listing_id → fetch Render link
app.get("/v1/ical/:token.ics", async (req, res) => {
  const token = req.params.token;

  let listing_id;
  try {
    const lookupResponse = await axios.get(`${XANO_TOKEN_LOOKUP_API}${token}`);
    listing_id = lookupResponse.data?.listing_id;
  } catch (err) {
    console.error("Token lookup failed:", err.message);
    return res.status(404).send("Invalid iCal token");
  }

  if (!listing_id) return res.status(404).send("Invalid token");

  const url = `${RENDER_CALENDAR_BASE}${listing_id}.ics`;
  console.log("📡 Fetching from Render calendar URL:", url);  // 👈 added this log

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
