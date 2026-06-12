# -*- coding: utf-8 -*-
"""
Created on Thu Jun 11 09:48:34 2026

@author: leste
"""

# possible improvement : using time modules to time properly the processes ?
import re as re
import feedparser as fp
import requests as rq
from time import sleep, time
import pandas as pd
url = "https://www.cert.ssi.gouv.fr/feed/"
rss_feed = fp.parse(url)

feed_extracted = {"id":[], "titles": [], "desc": [], "links": [], "published": []} # Will hold lists of retrieved links to advices and other relevant info
global_clock = time()
for entry in rss_feed.entries:
    feed_extracted["id"].append(entry.id)
    feed_extracted["titles"].append(entry.title)
    feed_extracted["desc"].append(entry.description)
    feed_extracted["published"].append(entry.published)
    feed_extracted["links"].append(entry.link)
    sleep(0.1) # Rate limit, short due to 40 element limit in those feeds
rss_clock_out = time()
print("ANSSI RSS feed extracted in {} seconds.".format(rss_clock_out - global_clock))
    
cve_collect_clock_in = time()
ref_cves = [] # Collect all CVE data / Normally should match 1:1 for each sublist RSS records
# /!\ one line per CVE corresponding to an alert in future dataframe
for link in feed_extracted["links"]:
    response = rq.get(link + "json/") 
    try:
        data = response.json()
        ref_cves.append(list(data["cves"]))
    except rq.JSONDecodeError: # Sometimes returns no decodable JSON, error handling prevents it from blocking it altogether
        print("Adress " + link + " returns malformed JSON or is not available")
    sleep(0.1) # Rate limit
cve_collect_clock_out = time()
print("CVE listing extracted in {} seconds.".format(cve_collect_clock_out - cve_collect_clock_in))

cve_unicity_clock_in = time()
cve_pattern = r"CVE-\d{4}-\d{4,7}"
cve_list = []
for elem in ref_cves: # Should follow same pattern as above ? only changes what's inside the list
    cve_list.append(list(set(re.findall(cve_pattern, str(elem)))))

unique_cves = []
for elem in cve_list:
    unique_cves += elem
unique_cves = list(set(unique_cves)) # Conversion to only retrieve unique ids, better for discussing with CVE API
cve_unicity_clock_out = time()
print("Obtained unique CVEs of length {} in {} seconds.".format(len(unique_cves), cve_unicity_clock_out - cve_unicity_clock_in))

cve_data_clock_in = time()
cve_data = {"id":[], "description":[], "cvss":[], "cwe":[], "cwe_desc":[], "affected":[], "epss": []} # All info about the CVEs we want to have it handy
# /!\ affected will contain list of dictionaries with vendor, product name and versions keys, datatype to manage in df creation
for idx, elem in enumerate(unique_cves):
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
                    print("CVSS for " + elem + " could not be retrieved at _1, putting empty value [{}/{}]".format(idx, len(unique_cves)))
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
    sleep(0.3) # Rate Limiting increased a little to prevent server closure but still small due to massive amounts of CVEs
cve_data_clock_out = time()
print("CVE dic obtained in {} seconds.".format(cve_data_clock_out - cve_data_clock_in))

# Connecting to that sweet EPSS API time
epss_clock_in = time()
for elem in unique_cves:
    response = rq.get(f"https://api.first.org/data/v1/epss?cve={elem}")
    try:
        data = response.json()
        epss_data = data.get("data", [])
        if epss_data:
            cve_data["epss"].append(epss_data[0]["epss"])
        else:
            cve_data["epss"].append("Unavailable")
    except rq.JSONDecodeError:
        cve_data["epss"].append("Unavailable")
    sleep(0.3)
epss_clock_out = time()
print("Final dic obtained in {} seconds.".format(epss_clock_out - epss_clock_in))

convertible_clock_in = time()
convertible = {"ANSSI ID":[], "Title": [], "Description": [], "Bulletin Link": [], "Published": [], "CVE":[], "CVE Description":[], "CVSS":[], "Severity": [], "CWE":[], "CWE Description":[], "EPSS": [], "Vendors": [], "Products": [], "Versions": []} # Behold, the adhoc dictionary merger
for i in range(len(feed_extracted["titles"])):
    for j in range(len(cve_list[i])):
        convertible["ANSSI ID"].append(feed_extracted["id"][i])
        convertible["Title"].append(feed_extracted["titles"][i])
        convertible["Description"].append(feed_extracted["desc"][i])
        convertible["Bulletin Link"].append(feed_extracted["links"][i])
        convertible["Published"].append(feed_extracted["published"][i])
        for k in range(len(cve_data["id"])):
            if cve_data["id"][k] == cve_list[i][j]:
                convertible["CVE"].append(cve_data["id"][k])
                convertible["CVE Description"].append(cve_data["description"][k])
                convertible["CVSS"].append(cve_data["cvss"][k])
                try:
                    if cve_data["cvss"][k] <= 3:
                        convertible["Severity"].append("Weak")
                    elif cve_data["cvss"][k] <= 6:
                        convertible["Severity"].append("Average")
                    elif cve_data["cvss"][k] <= 8:
                        convertible["Severity"].append("Severe")
                    else:
                        convertible["Severity"].append("Critical")
                except TypeError:
                    convertible["Severity"].append("Unavailable")
                convertible["CWE"].append(cve_data["cwe"][k])
                convertible["CWE Description"].append(cve_data["cwe_desc"][k])
                convertible["EPSS"].append(cve_data["epss"][k])
# dinner time, so basically for all cve_list sublist element create new entry with alert info corresponding to ith element of cve_list + info about jth contained CVE
convertible_clock_out = time()
print("Convertible dictionary obtained in {} seconds".format(convertible_clock_out - convertible_clock_in))
for key in convertible.keys():
    print("Length of {} : {}".format(key,len(convertible[key])))
final_df = pd.DataFrame(convertible) # Don't forget to replace Unavailable by NaNs !!
print(final_df)
global_clock_out = time()
print("Program execution completed in {} seconds.".format(global_clock_out - global_clock))
# Objective : produce a dataframe that will be encoded as a csv file for other parts
# at the end prints should only keep time information and confirmation of file creation, data display is only for debugging