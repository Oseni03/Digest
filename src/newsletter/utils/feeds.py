from django.conf import settings

from urllib.parse import urlparse
from google_alerts import GoogleAlerts

import html
import feedparser


class Feed:
    def __init__(self):
        self.email = settings.FEEDS_EMAIL
        self.password = settings.FEEDS_PASSWORD

    def create_feed(
        self,
        topic,
        delivery="RSS",
        match_type="BEST",
        alert_frequency="AS_IT_HAPPENS",
        region="US",
        language="en",
    ):
        """
        Args:
            delivery: 'RSS' or 'MAIL'
            match_type: 'ALL' or 'BEST'
            alert_frequency: 'AT_MOST_ONCE_A_DAY' or 'AS_IT_HAPPENS' or 'AT_MOST_ONCE_A_WEEK'
        """
        ga = GoogleAlerts(self.email, self.password)
        ga.authenticate()
        feed = ga.create(
            topic,
            {
                "delivery": delivery,
                "match_type": match_type,
                "alert_frequency": alert_frequency,
                "region": region,
                "language": language,
            },
        )
        return feed["rss_url"]

    def read_feeds(self, rss_url):
        results = []

        feed = feedparser.parse(rss_url)

        entries = feed.entries
        for entry in entries:
            new_entry = {}
            
            google_affiliate_url_parse = urlparse(entry.link).query.split("&")
            for url in google_affiliate_url_parse:
                if url.startswith("url"):
                    new_entry["link"] = url.split("=")[-1]
            
            new_entry["title"] = html.unescape(
                entry["title"].replace("</b>", "").replace("<b>", "")
            )
            new_entry["summary"] = html.unescape(
                entry["summary"].replace("</b>", "").replace("<b>", "")
            )
            results.append(new_entry)
        return results