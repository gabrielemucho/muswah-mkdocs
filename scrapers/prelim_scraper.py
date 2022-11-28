import scrapy
from urllib.error import HTTPError
import re
import time
from googlesearch import search  

class Helpers():
    def resolve_redirects(self, url):
        try:
            return url
        except HTTPError as e:
            if e.code == 429:
                time.sleep(15)
                self.resolve_redirects(url)

    def getlinks_en(self, q):
        link_count = 0
        query = q
        links = []
        for j in search(query, lang="en", tld="com", num=10, stop=40, pause=30):
            print("GETTING LINK EN: ", link_count)
            new_link = self.resolve_redirects(j)
            links.append(new_link)
            link_count += 1
        return links

    def set_start_urls(self):
        print("inside start URLs")
        en_query_list = ["wood+'church'+ukraine",
                         "tserkva+'church'+ukraine",
                         "wood+'church'+carpathian+ukraine",
                         "hutsul+'church'+ukraine",
                         "ukraine+wooden+'church'",
                         "oblast+wooden+'church'",
                         "oblast+tserkva+'church",
                         "ukraine+heritage+'church'",
                        ]
        link_list = []
        for q in en_query_list:
            links = self.getlinks_en(q)
            link_list += links
        return link_list


class ChurchSpider(scrapy.Spider):
    name = "ChurchSpider"
    helpers = Helpers()
    starts = helpers.set_start_urls()
    print(starts)
    start_urls = list(set(starts))

    def parse(self, response):
        for image in response.css('img'):
            link_text = image.xpath("//a/text()").extract()
            img_url = image.xpath('@src').get()
            desc = image.xpath('@alt').extract()
            for e in link_text:
                elem = str(e)
                if "church" in elem.lower() or "cherche" in elem.lower() or "hutsul church" in elem.lower() or "bukovina church" in elem.lower() or "lemko church" in elem.lower() or "boyko church" in elem.lower() or "ternopil church" in elem.lower() or "wooden tserkva" in elem.lower() or "wooden" in elem.lower() or "wood" in elem.lower():
                    desc.append(re.sub(' +', ' ', elem.replace("\n", "").replace("\t", "")))
            print("DESCRIPTION: ", desc)
            desc_string = " ".join(e for e in desc)
            if ("avatar" not in img_url and "logo" not in img_url and "wikimedia-button" not in img_url) and (("ukraine" in desc_string.lower() or "oblast" in desc_string.lower()) and ("church" in desc_string.lower() or "cherche" in desc_string.lower() or "hutsul church" in desc_string.lower() or "bukovina church" in elem.lower() or "lemko church" in elem.lower() or "boyko church" in elem.lower() or "ternopil church" in elem.lower() or "wooden tserkva" in desc_string.lower() or "wooden" in desc_string.lower() or "wood" in desc_string.lower())):
                yield {
                    'img_url': img_url,
                    'description': desc
                }

        next_page = response.css('li.next a::attr("href")').get()
        if next_page is not None:
            yield response.follow(next_page, self.parse)