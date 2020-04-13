#!/usr/bin/env python3

from min_rss_gen.generator import start_rss, gen_item

import xml.etree.ElementTree
from glob import glob
from pathlib import PurePath

SITE = "https://nwalsh1995.github.io"
RSS_FILENAME = "rss.xml"
rss_items = []

for f in glob("**/*.html", recursive=True):
    path = PurePath(f)
    title = path.with_suffix("").name.replace("-", " ").title()
    rss_items.append(gen_item(title=title, link=f"{SITE}/{str(path)}"))

rss_xml_element = start_rss(title="nwalsh1995.github.io", link="nwalsh1995.github.io", description="A collection of thoughts.", items=rss_items)

with open(RSS_FILENAME, "wb") as f:
    f.write(xml.etree.ElementTree.tostring(rss_xml_element))
