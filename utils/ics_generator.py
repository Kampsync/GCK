from icalendar import Calendar, Event
from datetime import datetime
import pytz

def create_ics(listing):
    cal = Calendar()
    event = Event()

    event.add("summary", listing.get("title", "Unnamed Event"))
    event.add("location", listing.get("location", ""))
    
    start = datetime.fromisoformat(listing["start_time"])
    end = datetime.fromisoformat(listing["end_time"])
    tz = pytz.timezone("UTC")

    event.add("dtstart", tz.localize(start))
    event.add("dtend", tz.localize(end))
    event.add("description", listing.get("description", ""))
    event.add("uid", listing.get("ical_token"))

    cal.add_component(event)
    return cal.to_ical()
