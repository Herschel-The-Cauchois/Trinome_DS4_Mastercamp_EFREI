# -*- coding: utf-8 -*-
"""
Created on Thu Jun 11 09:48:34 2026

@author: leste
"""

# possible improvement : using time modules to time properly the processes ?
import re as re
import feedparser as fp
import requests as rq
from time import sleep
import pandas as pd
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

cve_pattern = r"CVE-\d{4}-\d{4,7}"
cve_list = []
for elem in ref_cves: # Should follow same pattern as above ? only changes what's inside the list
    cve_list.append(list(set(re.findall(cve_pattern, str(data)))))
print("Obtained CVEs of length {} : ".format(len(cve_list)), cve_list)

unique_cves = []
for elem in cve_list:
    unique_cves += elem
unique_cves = list(set(unique_cves)) # Conversion to only retrieve unique ids, better for discussing with CVE API

counter = 0
cve_data = {"id":[], "description":[], "cvss":[], "cwe":[], "cwe_desc":[], "affected":[], "epss": []} # All info about the CVEs we want to have it handy
# /!\ affected will contain list of dictionaries with vendor, product name and versions keys, datatype to manage in df creation
for elem in unique_cves:
    response = rq.get(f"https://cveawg.mitre.org/api/cve/{elem}")
    try:
        data = response.json()
        try:
            cve_data["description"].append(data["containers"]["cna"]["descriptions"][0]["value"])
            cve_data["id"].append(elem) # This is done here to prevent phantom ids without any attached data to create an offset in the records
            cvss_flag = False # Signals if the value was found in any retrieval attempt
            try:
                cve_data["cvss"].append(data["containers"]["cna"]["metrics"][0]["cvssV3_0"]["baseScore"])
                cvss_flag = True
            except KeyError:
                print("CVSS for " + elem + " could not be retrieved at _0, trying at _1")
            if not cvss_flag:
                try:
                    cve_data["cvss"].append(data["containers"]["cna"]["metrics"][0]["cvssV3_1"]["baseScore"])
                    cvss_flag = True
                except KeyError:
                    print("CVSS for " + elem + " could not be retrieved at _1, putting empty value")
                    cve_data["cvss"].append("Unavailable")
            problemtype = data["containers"]["cna"].get("problemTypes", {})
            if problemtype and "descriptions" in problemtype[0]:
                cve_data["cwe"].append(problemtype[0]["descriptions"][0].get("cweId", "Unavailable"))
                cve_data["cwe_desc"].append(problemtype[0]["descriptions"][0].get("description", "Unavailable"))
            else:
                cve_data["cwe"].append("Unavailable")
                cve_data["cwe_desc"].append("Unavailable")
            try:
                affected = data["containers"]["cna"]["affected"]
                dict_affect = {"vendors": [], "product_names": [], "versions": []}
                for product in affected:
                    dict_affect["vendors"].append(product["vendor"])
                    dict_affect["product_names"].append(product["product"])
                    versions = [v["version"] for v in product["versions"] if v["status"] == "affected"]
                    dict_affect["versions"].append(', '.join(versions))
                cve_data["affected"].append(dict_affect)
            except KeyError:
                cve_data["affected"].append("Unavailable")
        except KeyError:
            print("No data for " + elem)
    except rq.JSONDecodeError:
        print("Adress " + f"https://cveawg.mitre.org/api/cve/{elem}" + " returns malformed JSON or is not available")
    sleep(1)
    count += 1
print("Final dic obtained in {} seconds: ".format(count), cve_data)
        
    
# Objective : produce a dataframe that will be encoded as a csv file for other parts