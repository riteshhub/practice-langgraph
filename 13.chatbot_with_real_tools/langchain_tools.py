import requests
import feedparser
import pyshorteners
from langchain_core.tools import tool

def get_lat_lon(location: str):
    """
    Get latitude and longitude for a given location using OpenStreetMap Nominatim API.
    No API key required.
    """
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": location,
        "format": "json",
        "limit": 1
    }
    headers = {
        "User-Agent": "location-app/1.0"
    }
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    results = response.json()
    if results:
        lat = float(results[0]["lat"])
        lon = float(results[0]["lon"])
        return lat, lon
    return None, None

def shorten_url(url):
    s = pyshorteners.Shortener()
    try:
        short_url = s.tinyurl.short(url)
        return short_url
    except Exception as e:
        print(f"Error shortening URL: {e}")
        return url

# Cleans a news title by removing the source name
def clean_title(title):
    return title.rsplit(' - ', 1)[0].strip()

@tool
def get_current_weather(location: str) -> str:
    """Get the current weather in a given location"""
    lat, lon = get_lat_lon(location)
    if lat is None or lon is None:
        return f"Could not find coordinates for {location}."
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": True
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        return f"Failed to fetch weather data for {location}."
    data = response.json()
    if "current_weather" in data:
        temperature = data["current_weather"].get("temperature")
        return f"The current temperature in {location} is {temperature}°C."
    else:
        return f"Weather data not available for {location}."

@tool
def get_news(topic: str) -> str:
    """Get the latest news on a given topic"""
    # URL of the Google News RSS feed
    gn_url = f"https://news.google.com/rss/search?q={topic}&hl=en-US&gl=US&ceid=US:en"

    # Parse the RSS feed
    gn_feed = feedparser.parse(gn_url)

    feeds=[]

    # Iterate through each news entry in the feed
    for entry in gn_feed.entries[:10]:
        news_title = clean_title(entry.title)
        news_link = shorten_url(entry.link)
        publication_date = entry.published
        news_source = entry.source.get("title")
        source_url = entry.source.get("href")

        feeds.append(
            {
                "headline": news_title,
                "url": news_link,
                "published": publication_date,
                "source": news_source,
                "source_url": source_url
            }
        )

    return feeds

if __name__ == "__main__":
    # Example usage:
    print(get_current_weather("Pune"))
    news = get_news("AI")
    for item in news:
        print(item)