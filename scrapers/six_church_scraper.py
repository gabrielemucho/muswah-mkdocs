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

    def getlinks_uk(self, q):
        link_count = 0
        query = q
        links = []
        for j in search(query, lang="uk", tld="ua", num=10, stop=20, pause=30):
            print("GETTING LINK UK: ", link_count)
            new_link = self.resolve_redirects(j)
            links.append(new_link)
            link_count += 1
        return links

    def set_start_urls(self):
        print("inside start URLs")
        en_query_list = ["tserkva+'sv'+'pokrovy'+iz+sela+kanora",
                         "'wooden'+church+of+'transfiguration'",
                         "st+paraskeva+church",
                         "st+michael+church+kyiv",
                         "st+michael+church+kiev",
                         "saint+mykolai+church",
                         "saint+nicholas+church+kyiv",
                         "saint+nicholas+church+kiev",
                         "'tserkva'+'svyatoyi'+triytsi",
                         "khram+svyatoho+oleksandra+nevs'koho"
                        ]
        uk_query_list = ["Церква+Покрови+Пресвятої+Богородиці",
                         "Церква+святої+Параскеви",
                         "Церква+святого+архангела+Михайла",
                         "Церква+святого+Миколи",
                         "Церква+святої+Трійці",
                         "Церква+Олександра+Невського",
                         "Церква+Покрови+Пресвятої+Богородиці+1792",
                         "Церква+святої+Параскеви+1742",
                         "Церква+святого+архангела+Михайла+1600",
                         "Церква+святого+Миколи+1817",
                         "Церква+святої+Трійці+1739",
                         "Церква+Олександра+Невського+1900",
                         "Церква+Покрови+Пресвятої+Богородиці+Київська",
                         "Церква+святої+Параскеви+Київська",
                         "Церква+святого+архангела+Михайла+Київська",
                         "Церква+святого+Миколи+Київська",
                         "Церква+святої+Трійці+Чернігівська",
                         "Церква+Олександра+Невського+Харківська",
                         "Церква+Покрови+Пресвятої+Богородиці+Київ",
                         "Церква+святої+Параскеви+Київ",
                         "Церква+святого+архангела+Михайла+Київ",
                         "Церква+святого+Миколи+Київ",
                         "Церква+святої+Трійці+Новий+Білоус",
                         "Церква+Олександра+Невського+Токарівка",
                         "Церква+Божої+Матері+Покрови",
                         "Церква+Святої+Великомучениці+Параскеви",
                         "Храм+Святого+Архистратига+Михаїла"
                        ]
        link_list = []
        # for q in en_query_list:
        #     links = self.getlinks_en(q)
        #     link_list += links
        for q in uk_query_list:
            links = self.getlinks_uk(q)
            link_list += links
        return link_list


class ChurchSpider(scrapy.Spider):
    coordinates  = [
        "50.43531161436375,30.42985391903462",
        "50.35341452161582,30.51012399154406",
        "50.355861,30.507611",
        "50.357240,30.514905",
        "51.538776,31.188884",
        "50.077255,36.190166"
    ]
    name = "ChurchSpider"
    helpers = Helpers()
    # starts = helpers.set_start_urls()
    # print(starts)
    # start_urls = list(set(starts))

    def construct_coordinate_starts(coordinates):
        map_links = []
        for c in coordinates:
            map_links.append("https://www.google.com/maps?q=" + c)
        return map_links

    start_urls = construct_coordinate_starts(coordinates)
    print(start_urls)

    def parse(self, response): 
        for d in response.css('div'):
            print("------------------------------------")
            print("photos div: ", d.xpath("//div[@class='d6JfQc']/@src").extract())
            print("------------------------------------")
            # link_text = image.xpath("//a/text()").extract()
            for img in d.css('img'): # d6JfQc
                img_url = img.xpath('@src').get()
                desc = img.xpath('@alt').extract()
                print("img_url: ", img_url)
                print("desc: ", desc)
                yield {
                    'img_url': img_url,
                    'description': desc
                }
            # for e in link_text:
            #     elem = str(e)
            #     if "church" in elem.lower() or "cherche" in elem.lower() or "hutsul church" in elem.lower() or "bukovina church" in elem.lower() or "lemko church" in elem.lower() or "boyko church" in elem.lower() or "ternopil church" in elem.lower() or "wooden tserkva" in elem.lower() or "wooden" in elem.lower() or "wood" in elem.lower():
            #         desc.append(re.sub(' +', ' ', elem.replace("\n", "").replace("\t", "")))
            # print("DESCRIPTION: ", desc)
            # desc_string = " ".join(e for e in desc)
            # if ("avatar" not in img_url and "logo" not in img_url and "wikimedia-button" not in img_url) and (("ukraine" in desc_string.lower() or "oblast" in desc_string.lower()) and ("church" in desc_string.lower() or "cherche" in desc_string.lower() or "hutsul church" in desc_string.lower() or "bukovina church" in elem.lower() or "lemko church" in elem.lower() or "boyko church" in elem.lower() or "ternopil church" in elem.lower() or "wooden tserkva" in desc_string.lower() or "wooden" in desc_string.lower() or "wood" in desc_string.lower())):
            # yield {
            #     'img_url': img_url,
            #     'description': desc
            # }

        next_page = response.css('li.next a::attr("href")').get()
        if next_page is not None:
            yield response.follow(next_page, self.parse)