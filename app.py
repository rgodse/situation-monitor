"""
Situation Monitoring Dashboard
A geopolitics-focused news aggregation dashboard with 3D globe visualization
"""

from flask import Flask, render_template, jsonify, request
import feedparser
import sqlite3
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
import threading
import re
import os

# Get the directory where this script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'news.db')

app = Flask(__name__)

# ============================================================================
# RSS FEED CONFIGURATION - Geopolitics & Situation Monitoring Focus
# ============================================================================

RSS_FEEDS = {
    'US Policy Watch': [
        {'url': 'https://www.whitehouse.gov/feed/', 'source': 'White House', 'location': 'United States'},
        {'url': 'https://rss.politico.com/playbook.xml', 'source': 'POLITICO Playbook', 'location': 'United States'},
        {'url': 'https://feeds.axios.com/api/feed', 'source': 'Axios', 'location': 'United States'},
        {'url': 'https://feeds.bbci.co.uk/news/world/us_and_canada/rss.xml', 'source': 'BBC US & Canada', 'location': 'United States'},
        {'url': 'https://rss.nytimes.com/services/xml/rss/nyt/Politics.xml', 'source': 'NYT Politics', 'location': 'United States'},
        {'url': 'https://www.reuters.com/arc/outboundfeeds/v3/all/rss.xml?outputType=xml', 'source': 'Reuters', 'location': 'United States'},
    ],
    'Geopolitics': [
        {'url': 'https://www.cfr.org/rss.xml', 'source': 'Council on Foreign Relations', 'location': None},
        {'url': 'https://foreignpolicy.com/feed/', 'source': 'Foreign Policy', 'location': None},
        {'url': 'https://www.aljazeera.com/xml/rss/all.xml', 'source': 'Al Jazeera', 'location': None},
        {'url': 'https://feeds.bbci.co.uk/news/world/rss.xml', 'source': 'BBC World', 'location': None},
        {'url': 'https://thediplomat.com/feed/', 'source': 'The Diplomat', 'location': 'Asia-Pacific'},
        {'url': 'https://www.scmp.com/rss/91/feed', 'source': 'South China Morning Post', 'location': 'China'},
        {'url': 'https://www.middleeasteye.net/rss', 'source': 'Middle East Eye', 'location': 'Middle East'},
        {'url': 'https://warontherocks.com/feed/', 'source': 'War on the Rocks', 'location': None},
    ],
    'Conflict Zones': [
        {'url': 'https://www.reuters.com/arc/outboundfeeds/v3/section/world/rss.xml?outputType=xml', 'source': 'Reuters World', 'location': None},
        {'url': 'https://www.aljazeera.com/xml/rss/all.xml', 'source': 'Al Jazeera', 'location': None},
        {'url': 'https://feeds.bbci.co.uk/news/world/middle_east/rss.xml', 'source': 'BBC Middle East', 'location': 'Middle East'},
        {'url': 'https://feeds.bbci.co.uk/news/world/europe/rss.xml', 'source': 'BBC Europe', 'location': 'Europe'},
        {'url': 'https://feeds.bbci.co.uk/news/world/africa/rss.xml', 'source': 'BBC Africa', 'location': 'Africa'},
        {'url': 'https://feeds.bbci.co.uk/news/world/asia/rss.xml', 'source': 'BBC Asia', 'location': 'Asia'},
        {'url': 'https://www.understandingwar.org/feed', 'source': 'Institute for Study of War', 'location': None},
    ],
    'Defence & Intel': [
        {'url': 'https://www.defensenews.com/arc/outboundfeeds/rss/?outputType=xml', 'source': 'Defense News', 'location': None},
        {'url': 'https://breakingdefense.com/feed/', 'source': 'Breaking Defense', 'location': None},
        {'url': 'https://www.thedrive.com/the-war-zone/feed', 'source': 'The War Zone', 'location': None},
        {'url': 'https://www.c4isrnet.com/arc/outboundfeeds/rss/?outputType=xml', 'source': 'C4ISRNET', 'location': None},
        {'url': 'https://www.janes.com/feeds/news', 'source': 'Janes', 'location': None},
        {'url': 'https://www.bellingcat.com/feed/', 'source': 'Bellingcat', 'location': None},
    ],
    'Economic Warfare': [
        {'url': 'https://www.reuters.com/arc/outboundfeeds/v3/section/business/rss.xml?outputType=xml', 'source': 'Reuters Business', 'location': None},
        {'url': 'https://feeds.bloomberg.com/markets/news.rss', 'source': 'Bloomberg Markets', 'location': None},
        {'url': 'https://feeds.ft.com/rss/home/uk', 'source': 'Financial Times', 'location': None},
        {'url': 'https://www.economist.com/finance-and-economics/rss.xml', 'source': 'The Economist', 'location': None},
        {'url': 'https://www.business-standard.com/rss/home_page_top_stories.rss', 'source': 'Business Standard', 'location': 'India'},
    ],
    'India': [
        {'url': 'https://www.thehindu.com/news/national/feeder/default.rss', 'source': 'The Hindu National', 'location': 'India'},
        {'url': 'https://www.thehindu.com/news/international/feeder/default.rss', 'source': 'The Hindu International', 'location': 'India'},
        {'url': 'https://timesofindia.indiatimes.com/rssfeeds/296589292.cms', 'source': 'Times of India', 'location': 'India'},
        {'url': 'https://www.hindustantimes.com/feeds/rss/india-news/rssfeed.xml', 'source': 'Hindustan Times', 'location': 'India'},
        {'url': 'https://indianexpress.com/section/india/feed/', 'source': 'Indian Express', 'location': 'India'},
        {'url': 'https://www.ndtv.com/rss/india', 'source': 'NDTV India', 'location': 'India'},
        {'url': 'https://economictimes.indiatimes.com/rssfeedstopstories.cms', 'source': 'Economic Times', 'location': 'India'},
        {'url': 'https://www.livemint.com/rss/news', 'source': 'Mint', 'location': 'India'},
    ],
    'Markets': [
        {'url': 'https://feeds.bloomberg.com/markets/news.rss', 'source': 'Bloomberg Markets', 'location': None},
        {'url': 'https://www.cnbc.com/id/10001147/device/rss/rss.html', 'source': 'CNBC Markets', 'location': None},
        {'url': 'https://feeds.marketwatch.com/marketwatch/topstories/', 'source': 'MarketWatch', 'location': None},
        {'url': 'https://www.investing.com/rss/news.rss', 'source': 'Investing.com', 'location': None},
        {'url': 'https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms', 'source': 'ET Markets', 'location': 'India'},
        {'url': 'https://www.moneycontrol.com/rss/latestnews.xml', 'source': 'Moneycontrol', 'location': 'India'},
        {'url': 'https://finance.yahoo.com/news/rssindex', 'source': 'Yahoo Finance', 'location': None},
    ],
    'Cyber & Tech': [
        {'url': 'https://www.wired.com/feed/category/security/latest/rss', 'source': 'Wired Security', 'location': None},
        {'url': 'https://krebsonsecurity.com/feed/', 'source': 'Krebs on Security', 'location': None},
        {'url': 'https://www.bleepingcomputer.com/feed/', 'source': 'BleepingComputer', 'location': None},
        {'url': 'https://thehackernews.com/feeds/posts/default', 'source': 'The Hacker News', 'location': None},
        {'url': 'https://www.darkreading.com/rss.xml', 'source': 'Dark Reading', 'location': None},
        {'url': 'https://www.theregister.com/security/headlines.atom', 'source': 'The Register', 'location': None},
        {'url': 'https://techcrunch.com/category/security/feed/', 'source': 'TechCrunch Security', 'location': None},
        {'url': 'https://www.schneier.com/feed/', 'source': 'Schneier on Security', 'location': None},
        {'url': 'https://semianalysis.com/feed/', 'source': 'SemiAnalysis', 'location': None},
    ],
}

# ============================================================================
# LOCATION EXTRACTION - For Globe Visualization
# ============================================================================

LOCATION_KEYWORDS = {
    # Countries with coordinates [lat, lng]
    'ukraine': {'name': 'Ukraine', 'lat': 48.3794, 'lng': 31.1656},
    'russia': {'name': 'Russia', 'lat': 61.5240, 'lng': 105.3188},
    'china': {'name': 'China', 'lat': 35.8617, 'lng': 104.1954},
    'taiwan': {'name': 'Taiwan', 'lat': 23.6978, 'lng': 120.9605},
    'israel': {'name': 'Israel', 'lat': 31.0461, 'lng': 34.8516},
    'gaza': {'name': 'Gaza', 'lat': 31.3547, 'lng': 34.3088},
    'palestine': {'name': 'Palestine', 'lat': 31.9522, 'lng': 35.2332},
    'iran': {'name': 'Iran', 'lat': 32.4279, 'lng': 53.6880},
    'syria': {'name': 'Syria', 'lat': 34.8021, 'lng': 38.9968},
    'yemen': {'name': 'Yemen', 'lat': 15.5527, 'lng': 48.5164},
    'north korea': {'name': 'North Korea', 'lat': 40.3399, 'lng': 127.5101},
    'south korea': {'name': 'South Korea', 'lat': 35.9078, 'lng': 127.7669},
    'japan': {'name': 'Japan', 'lat': 36.2048, 'lng': 138.2529},
    'india': {'name': 'India', 'lat': 20.5937, 'lng': 78.9629},
    'pakistan': {'name': 'Pakistan', 'lat': 30.3753, 'lng': 69.3451},
    'afghanistan': {'name': 'Afghanistan', 'lat': 33.9391, 'lng': 67.7100},
    'iraq': {'name': 'Iraq', 'lat': 33.2232, 'lng': 43.6793},
    'saudi arabia': {'name': 'Saudi Arabia', 'lat': 23.8859, 'lng': 45.0792},
    'turkey': {'name': 'Turkey', 'lat': 38.9637, 'lng': 35.2433},
    'egypt': {'name': 'Egypt', 'lat': 26.8206, 'lng': 30.8025},
    'libya': {'name': 'Libya', 'lat': 26.3351, 'lng': 17.2283},
    'sudan': {'name': 'Sudan', 'lat': 12.8628, 'lng': 30.2176},
    'ethiopia': {'name': 'Ethiopia', 'lat': 9.1450, 'lng': 40.4897},
    'somalia': {'name': 'Somalia', 'lat': 5.1521, 'lng': 46.1996},
    'nigeria': {'name': 'Nigeria', 'lat': 9.0820, 'lng': 8.6753},
    'south africa': {'name': 'South Africa', 'lat': -30.5595, 'lng': 22.9375},
    'venezuela': {'name': 'Venezuela', 'lat': 6.4238, 'lng': -66.5897},
    'brazil': {'name': 'Brazil', 'lat': -14.2350, 'lng': -51.9253},
    'mexico': {'name': 'Mexico', 'lat': 23.6345, 'lng': -102.5528},
    'canada': {'name': 'Canada', 'lat': 56.1304, 'lng': -106.3468},
    'united states': {'name': 'United States', 'lat': 37.0902, 'lng': -95.7129},
    'usa': {'name': 'United States', 'lat': 37.0902, 'lng': -95.7129},
    'america': {'name': 'United States', 'lat': 37.0902, 'lng': -95.7129},
    'trump': {'name': 'United States', 'lat': 37.0902, 'lng': -95.7129},
    'biden': {'name': 'United States', 'lat': 37.0902, 'lng': -95.7129},
    'washington': {'name': 'United States', 'lat': 38.9072, 'lng': -77.0369},
    'pentagon': {'name': 'United States', 'lat': 38.8719, 'lng': -77.0563},
    'nato': {'name': 'Europe', 'lat': 50.8503, 'lng': 4.3517},
    'european union': {'name': 'Europe', 'lat': 50.8503, 'lng': 4.3517},
    'eu': {'name': 'Europe', 'lat': 50.8503, 'lng': 4.3517},
    'brussels': {'name': 'Belgium', 'lat': 50.8503, 'lng': 4.3517},
    'london': {'name': 'United Kingdom', 'lat': 51.5074, 'lng': -0.1278},
    'uk': {'name': 'United Kingdom', 'lat': 55.3781, 'lng': -3.4360},
    'britain': {'name': 'United Kingdom', 'lat': 55.3781, 'lng': -3.4360},
    'germany': {'name': 'Germany', 'lat': 51.1657, 'lng': 10.4515},
    'france': {'name': 'France', 'lat': 46.2276, 'lng': 2.2137},
    'poland': {'name': 'Poland', 'lat': 51.9194, 'lng': 19.1451},
    'crimea': {'name': 'Crimea', 'lat': 44.9521, 'lng': 34.1024},
    'donbas': {'name': 'Donbas', 'lat': 48.0159, 'lng': 37.8028},
    'kyiv': {'name': 'Ukraine', 'lat': 50.4501, 'lng': 30.5234},
    'kiev': {'name': 'Ukraine', 'lat': 50.4501, 'lng': 30.5234},
    'moscow': {'name': 'Russia', 'lat': 55.7558, 'lng': 37.6173},
    'beijing': {'name': 'China', 'lat': 39.9042, 'lng': 116.4074},
    'taipei': {'name': 'Taiwan', 'lat': 25.0330, 'lng': 121.5654},
    'tehran': {'name': 'Iran', 'lat': 35.6892, 'lng': 51.3890},
    'pyongyang': {'name': 'North Korea', 'lat': 39.0392, 'lng': 125.7625},
    'south china sea': {'name': 'South China Sea', 'lat': 12.0, 'lng': 114.0},
    'red sea': {'name': 'Red Sea', 'lat': 20.0, 'lng': 38.0},
    'strait of hormuz': {'name': 'Strait of Hormuz', 'lat': 26.5, 'lng': 56.5},
    'arctic': {'name': 'Arctic', 'lat': 90.0, 'lng': 0.0},
    'houthi': {'name': 'Yemen', 'lat': 15.5527, 'lng': 48.5164},
    'hezbollah': {'name': 'Lebanon', 'lat': 33.8547, 'lng': 35.8623},
    'lebanon': {'name': 'Lebanon', 'lat': 33.8547, 'lng': 35.8623},
    'myanmar': {'name': 'Myanmar', 'lat': 21.9162, 'lng': 95.9560},
    'philippines': {'name': 'Philippines', 'lat': 12.8797, 'lng': 121.7740},
    'indonesia': {'name': 'Indonesia', 'lat': -0.7893, 'lng': 113.9213},
    'australia': {'name': 'Australia', 'lat': -25.2744, 'lng': 133.7751},
    'aukus': {'name': 'Australia', 'lat': -25.2744, 'lng': 133.7751},
}

def extract_location(title, description):
    """Extract location from article title and description"""
    text = f"{title} {description}".lower()

    for keyword, location in LOCATION_KEYWORDS.items():
        if keyword in text:
            return location

    return None

# ============================================================================
# DATABASE SETUP
# ============================================================================

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database schema"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            link TEXT UNIQUE NOT NULL,
            source TEXT NOT NULL,
            category TEXT NOT NULL,
            published_date TEXT,
            fetched_date TEXT NOT NULL,
            location_name TEXT,
            location_lat REAL,
            location_lng REAL
        )
    ''')

    # Create indexes for faster queries
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_category ON articles(category)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_source ON articles(source)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_fetched ON articles(fetched_date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_location ON articles(location_name)')

    conn.commit()
    conn.close()

# ============================================================================
# RSS FEED FETCHING
# ============================================================================

def fetch_feed(feed_config, category):
    """Fetch and parse a single RSS feed"""
    articles = []

    try:
        feed = feedparser.parse(feed_config['url'])

        for entry in feed.entries[:20]:  # Limit to 20 articles per feed
            title = entry.get('title', 'No Title')
            description = entry.get('summary', entry.get('description', ''))

            # Clean HTML from description
            description = re.sub('<[^<]+?>', '', description)[:500]

            link = entry.get('link', '')

            # Parse published date
            published = entry.get('published_parsed') or entry.get('updated_parsed')
            if published:
                published_date = datetime(*published[:6]).isoformat()
            else:
                published_date = None

            # Extract location
            location = extract_location(title, description)
            if not location and feed_config.get('location'):
                # Use feed's default location
                loc_key = feed_config['location'].lower()
                location = LOCATION_KEYWORDS.get(loc_key)

            articles.append({
                'title': title,
                'description': description,
                'link': link,
                'source': feed_config['source'],
                'category': category,
                'published_date': published_date,
                'location': location
            })

    except Exception as e:
        print(f"Error fetching {feed_config['source']}: {e}")

    return articles

def fetch_all_feeds():
    """Fetch all RSS feeds and store in database"""
    print(f"[{datetime.now().isoformat()}] Starting feed fetch...")

    conn = get_db()
    cursor = conn.cursor()

    total_new = 0

    for category, feeds in RSS_FEEDS.items():
        for feed_config in feeds:
            articles = fetch_feed(feed_config, category)

            for article in articles:
                try:
                    location = article.get('location')
                    cursor.execute('''
                        INSERT OR IGNORE INTO articles
                        (title, description, link, source, category, published_date, fetched_date,
                         location_name, location_lat, location_lng)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        article['title'],
                        article['description'],
                        article['link'],
                        article['source'],
                        article['category'],
                        article['published_date'],
                        datetime.now().isoformat(),
                        location['name'] if location else None,
                        location['lat'] if location else None,
                        location['lng'] if location else None
                    ))

                    if cursor.rowcount > 0:
                        total_new += 1

                except Exception as e:
                    print(f"Error inserting article: {e}")

    conn.commit()
    conn.close()

    print(f"[{datetime.now().isoformat()}] Feed fetch complete. {total_new} new articles added.")

# ============================================================================
# API ROUTES
# ============================================================================

@app.route('/')
def index():
    """Serve main dashboard"""
    return render_template('index.html', categories=list(RSS_FEEDS.keys()))

@app.route('/globe')
def globe():
    """Serve globe visualization page"""
    return render_template('globe.html')

@app.route('/api/articles')
def get_articles():
    """Get articles with optional filtering"""
    category = request.args.get('category')
    source = request.args.get('source')
    search = request.args.get('search')
    limit = request.args.get('limit', 100, type=int)

    conn = get_db()
    cursor = conn.cursor()

    query = 'SELECT * FROM articles WHERE 1=1'
    params = []

    if category:
        query += ' AND category = ?'
        params.append(category)

    if source:
        query += ' AND source = ?'
        params.append(source)

    if search:
        query += ' AND (title LIKE ? OR description LIKE ?)'
        params.extend([f'%{search}%', f'%{search}%'])

    query += ' ORDER BY fetched_date DESC LIMIT ?'
    params.append(limit)

    articles = cursor.execute(query, params).fetchall()
    conn.close()

    return jsonify([dict(row) for row in articles])

@app.route('/api/sources')
def get_sources():
    """Get list of all sources"""
    conn = get_db()
    cursor = conn.cursor()

    sources = cursor.execute(
        'SELECT DISTINCT source FROM articles ORDER BY source'
    ).fetchall()

    conn.close()

    return jsonify([row['source'] for row in sources])

@app.route('/api/globe-data')
def get_globe_data():
    """Get article data for globe visualization"""
    conn = get_db()
    cursor = conn.cursor()

    # Get articles with location data, grouped by location
    articles = cursor.execute('''
        SELECT location_name, location_lat, location_lng,
               COUNT(*) as count,
               GROUP_CONCAT(title, '|||') as titles,
               GROUP_CONCAT(category, '|||') as categories
        FROM articles
        WHERE location_name IS NOT NULL
        GROUP BY location_name
        ORDER BY count DESC
    ''').fetchall()

    conn.close()

    result = []
    for row in articles:
        titles = row['titles'].split('|||')[:5]  # Limit to 5 titles per location
        categories = list(set(row['categories'].split('|||')))

        result.append({
            'name': row['location_name'],
            'lat': row['location_lat'],
            'lng': row['location_lng'],
            'count': row['count'],
            'titles': titles,
            'categories': categories
        })

    return jsonify(result)

@app.route('/api/refresh', methods=['POST'])
def refresh_feeds():
    """Manually trigger feed refresh"""
    thread = threading.Thread(target=fetch_all_feeds)
    thread.start()
    return jsonify({'status': 'Feed refresh started'})

@app.route('/api/stats')
def get_stats():
    """Get dashboard statistics"""
    conn = get_db()
    cursor = conn.cursor()

    stats = {
        'total_articles': cursor.execute('SELECT COUNT(*) FROM articles').fetchone()[0],
        'categories': {},
        'sources_count': cursor.execute('SELECT COUNT(DISTINCT source) FROM articles').fetchone()[0],
        'locations_count': cursor.execute('SELECT COUNT(DISTINCT location_name) FROM articles WHERE location_name IS NOT NULL').fetchone()[0],
    }

    # Articles per category
    for row in cursor.execute('SELECT category, COUNT(*) as count FROM articles GROUP BY category'):
        stats['categories'][row['category']] = row['count']

    conn.close()

    return jsonify(stats)

@app.route('/api/breaking')
def get_breaking():
    """Get breaking news (articles from last 2 hours)"""
    conn = get_db()
    cursor = conn.cursor()

    # Get articles fetched in last 2 hours
    two_hours_ago = (datetime.now() - timedelta(hours=2)).isoformat()

    articles = cursor.execute('''
        SELECT * FROM articles
        WHERE fetched_date > ?
        ORDER BY fetched_date DESC
        LIMIT 10
    ''', (two_hours_ago,)).fetchall()

    conn.close()

    return jsonify([dict(row) for row in articles])

def normalize_title(title):
    """Normalize title for comparison"""
    import re
    # Remove punctuation, lowercase, remove common words
    title = title.lower()
    title = re.sub(r'[^\w\s]', '', title)
    stopwords = {'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'and', 'is', 'are', 'was', 'were'}
    words = [w for w in title.split() if w not in stopwords and len(w) > 2]
    return set(words)

def calculate_similarity(title1, title2):
    """Calculate Jaccard similarity between two titles"""
    words1 = normalize_title(title1)
    words2 = normalize_title(title2)
    if not words1 or not words2:
        return 0
    intersection = len(words1 & words2)
    union = len(words1 | words2)
    return intersection / union if union > 0 else 0

@app.route('/api/articles-grouped')
def get_articles_grouped():
    """Get articles with similar stories grouped together"""
    category = request.args.get('category')
    search = request.args.get('search')
    limit = request.args.get('limit', 100, type=int)

    conn = get_db()
    cursor = conn.cursor()

    query = 'SELECT * FROM articles WHERE 1=1'
    params = []

    if category:
        query += ' AND category = ?'
        params.append(category)

    if search:
        query += ' AND (title LIKE ? OR description LIKE ?)'
        params.extend([f'%{search}%', f'%{search}%'])

    query += ' ORDER BY fetched_date DESC LIMIT ?'
    params.append(limit * 2)  # Get more to account for grouping

    articles = [dict(row) for row in cursor.execute(query, params).fetchall()]
    conn.close()

    # Group similar articles
    grouped = []
    used = set()

    for i, article in enumerate(articles):
        if i in used:
            continue

        group = {
            'main': article,
            'related': []
        }

        for j, other in enumerate(articles[i+1:], start=i+1):
            if j in used:
                continue
            if calculate_similarity(article['title'], other['title']) > 0.4:
                group['related'].append(other)
                used.add(j)

        used.add(i)
        grouped.append(group)

        if len(grouped) >= limit:
            break

    return jsonify(grouped)

# ============================================================================
# STARTUP
# ============================================================================

# Initialize database on import (works with gunicorn)
init_db()

# Set up scheduler for periodic updates
scheduler = BackgroundScheduler()
scheduler.add_job(fetch_all_feeds, 'interval', minutes=30)

# Only start scheduler once (avoid duplicate in gunicorn workers)
import atexit
if not scheduler.running:
    # Initial feed fetch
    print("Starting initial feed fetch...")
    fetch_all_feeds()
    scheduler.start()
    print("Scheduler started - feeds will refresh every 30 minutes")
    atexit.register(lambda: scheduler.shutdown())

if __name__ == '__main__':
    # Local development
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=True, port=port, use_reloader=False)
