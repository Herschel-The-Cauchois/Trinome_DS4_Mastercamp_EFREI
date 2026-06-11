# -*- coding: utf-8 -*-
"""
Created on Thu Jun 11 09:48:34 2026

@author: leste
"""

import feedparser as fp
import requests as rq
from time import sleep
import panda as pd
url = "https://www.cert.ssi.gouv.fr/feed/"
rss_feed = fp.parse(url)

feed_extracted = {"titles": [], "desc": [], "links": [], "published": []} # Will hold lists of retrieved links to advices and other relevant info
count = 0
for entry in rss_feed.entries:
    feed_extracted["titles"].append(entry.title)
    feed_extracted["desc"].append(entry.description)
    feed_extracted["published"].append(entry.published)
    feed_extracted["links"].append(entry.link)
    sleep(1) # Rate limit
    count += 1
print("ANSSI RSS feed extracted in {} seconds.".format(count))
    
count = 0
ref_cves = [] # Collect all CVE data / Normally should match 1:1 for each sublist RSS records
# /!\ one line per CVE corresponding to an alert in future dataframe
for link in feed_extracted["links"]:
    response = rq.get(link + "json/") 
    try:
        data = response.json()
        ref_cves.append(list(data["cves"]))
    except rq.JSONDecodeError: # Sometimes returns no decodable JSON, error handling prevents it from blocking it altogether
        print("Adress " + link + " returns malformed JSON or is not available")
    sleep(1) # Rate limit
    count += 1
print("CVE listing extracted in {} seconds.".format(count))
print("Data obtained : ", ref_cves)
    
# Objective : produce a dataframe that will be encoded as a csv file for other parts