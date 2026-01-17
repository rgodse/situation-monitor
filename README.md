# Situation Monitor Dashboard

A geopolitics-focused news aggregation dashboard with 3D globe visualization, designed for monitoring global situations, US policy changes, and conflict zones.

## Features

- **5 Geopolitics-focused categories**: US Policy Watch, Geopolitics, Conflict Zones, Defence & Intel, Economic Warfare
- **3D Interactive Globe**: Globe.gl visualization showing news by location
- **Twitter/X Integration**: Embedded OSINT feed panel (free, no API needed)
- **Quick Filters**: One-click filters for Trump, Ukraine, China, Israel, Russia, NATO, Taiwan, Iran
- **Real-time Search**: Filter articles by keywords
- **Dark "Situation Room" Theme**: Professional monitoring interface
- **Auto-refresh**: Feeds update every 30 minutes

## Screenshots

- **Dashboard**: Category tabs, search, source filtering, article cards
- **Globe View**: Interactive 3D globe with clickable location markers

## Quick Start

```bash
cd /Users/rohangodse/dev/Newstracker

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py

# Open in browser
open http://localhost:5001
```

## RSS Sources

### US Policy Watch
- White House, POLITICO Playbook, Axios, BBC US & Canada, NYT Politics, Reuters

### Geopolitics
- Council on Foreign Relations, Foreign Policy, Al Jazeera, BBC World, The Diplomat, South China Morning Post, Middle East Eye, War on the Rocks

### Conflict Zones
- Reuters World, Al Jazeera, BBC (Middle East, Europe, Africa, Asia), Institute for Study of War

### Defence & Intel
- Defense News, Breaking Defense, The War Zone, C4ISRNET, Janes, Bellingcat

### Economic Warfare
- Reuters Business, Bloomberg Markets, Financial Times, The Economist, Business Standard

## Project Structure

```
Newstracker/
├── app.py              # Flask backend, RSS fetcher, API routes
├── templates/
│   ├── index.html     # Main dashboard
│   └── globe.html     # 3D globe visualization
├── static/
│   └── style.css      # Dark theme styling
├── news.db            # SQLite database (auto-created)
├── requirements.txt   # Python dependencies
└── README.md
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main dashboard |
| `/globe` | GET | Globe visualization |
| `/api/articles` | GET | Get articles (supports `?category=`, `?source=`, `?search=`) |
| `/api/sources` | GET | List all sources |
| `/api/globe-data` | GET | Location-aggregated data for globe |
| `/api/stats` | GET | Dashboard statistics |
| `/api/refresh` | POST | Manually trigger feed refresh |

## Customizing Twitter Feed

The sidebar includes an embedded X (Twitter) list. To use your own OSINT list:

1. Create a public List on X with accounts you follow
2. Go to https://publish.twitter.com
3. Enter your list URL and get the embed code
4. Replace the embed code in `templates/index.html`

Suggested OSINT accounts:
- @sentdefender
- @TheStudyofWar
- @RALee85
- @Tom_ftr
- @ABORbureau

## Tech Stack

- **Backend**: Flask, feedparser, APScheduler, SQLite
- **Frontend**: Vanilla JS, CSS3
- **Globe**: Globe.gl (WebGL)
- **Fonts**: JetBrains Mono, Inter

## Notes

- Port 5001 is used (5000 conflicts with AirPlay on macOS)
- First startup fetches all feeds (~30-60 seconds)
- Database auto-created on first run
- Feeds refresh every 30 minutes automatically
