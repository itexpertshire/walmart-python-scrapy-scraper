import json
import math, random
import scrapy
from urllib.parse import urlencode

user_agent_list = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.5 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.53 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Windows; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/603.3.8 (KHTML, like Gecko) Version/10.1.2 Safari/603.3.8",
    "Mozilla/5.0 (Windows NT 10.0; Windows; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.53 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Windows; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.53 Safari/537.36"
     ]

class WalmartSpider(scrapy.Spider):
    name = "walmart"



    #custom_settings = {
    #    'FEEDS': { 'data/%(name)s_%(time)s.csv': { 'format': 'csv',}}
    #    }

    def start_requests(self):
        keyword_list = ['laptop']
        cateory_list = ['Networking Cables & Connectors','Lenses','Routers']
        cat_param='||category:'.join(cateory_list)
        for keyword in keyword_list:
            #payload = {'q': keyword, 'sort': 'best_seller', 'page': 1, 'affinityOverride': 'default'}
            payload = {'max_price': 5, 'facet': 'exclude_oos%3AShow+available+items+only'+cat_param, 'sort': 'price_low', 'page': 1, 'affinityOverride': 'default'}
            walmart_search_url = 'https://www.walmart.com/browse/3944?' + urlencode(payload)
            #walmart_search_url = 'https://www.walmart.com/browse/3944?min_price=0&max_price=5&facet=exclude_oos%3AShow+available+items+only&sort=price_low&page=1'
            yield scrapy.Request(url=walmart_search_url, callback=self.parse_search_results, meta={'keyword': keyword, 'page': 1, 'cat_param': cat_param}, headers={"User-Agent": user_agent_list[random.randint(0, len(user_agent_list)-1)]})

    def parse_search_results(self, response):
        page = response.meta['page']
        keyword = response.meta['keyword'] 
        cat_param = response.meta['cat_param']
        script_tag  = response.xpath('//script[@id="__NEXT_DATA__"]/text()').get()
        if script_tag is not None:
            json_blob = json.loads(script_tag)

            ## Request Product Page
            product_list = json_blob["props"]["pageProps"]["initialData"]["searchResult"]["itemStacks"][0]["items"]
            for idx, product in enumerate(product_list):
                walmart_product_url = 'https://www.walmart.com' + product.get('canonicalUrl', '').split('?')[0]
                yield scrapy.Request(url=walmart_product_url, callback=self.parse_product_data, meta={'keyword': keyword,'cat_param': cat_param, 'page': page, 'position': idx + 1})
            
            ## Request Next Page
            if page == 1:
                total_product_count = json_blob["props"]["pageProps"]["initialData"]["searchResult"]["itemStacks"][0]["count"]
                max_pages = math.ceil(total_product_count / 40)
                if max_pages > 5:
                    max_pages = 1
                for p in range(2, max_pages):
                    #payload = {'q': keyword, 'sort': 'best_seller', 'page': p, 'affinityOverride': 'default'}
                    payload = {'max_price': 5, 'facet': 'exclude_oos%3AShow+available+items+only'+cat_param, 'sort': 'price_low', 'page': p, 'affinityOverride': 'default'}
                    walmart_search_url = 'https://www.walmart.com/browse/3944?' + urlencode(payload)
                    yield scrapy.Request(url=walmart_search_url, callback=self.parse_search_results, meta={'keyword': keyword,'cat_param': cat_param, 'page': p})
    

    def parse_product_data(self, response):
        script_tag  = response.xpath('//script[@id="__NEXT_DATA__"]/text()').get()
        if script_tag is not None:
            json_blob = json.loads(script_tag)
            raw_product_data = json_blob["props"]["pageProps"]["initialData"]["data"]["product"]
            #print(raw_product_data)
            if (hasattr(raw_product_data['priceInfo']['wasPrice'], 'get')):
                yield {
                    'keyword': response.meta['keyword'],
                    'page': response.meta['page'],
                    'position': response.meta['position'],
                    'id':  raw_product_data.get('id'),
                    'type':  raw_product_data.get('type'),
                    'name':  raw_product_data.get('name'),
                    'brand':  raw_product_data.get('brand'),
                    'averageRating':  raw_product_data.get('averageRating'),
                    'manufacturerName':  raw_product_data.get('manufacturerName'),
                    'shortDescription':  raw_product_data.get('shortDescription'),
                    'thumbnailUrl':  raw_product_data['imageInfo'].get('thumbnailUrl'),
                    'price':  raw_product_data['priceInfo']['currentPrice'].get('price'), 
                    'wasPrice':  raw_product_data['priceInfo']['wasPrice'].get('price'), 
                    'currencyUnit':  raw_product_data['priceInfo']['currentPrice'].get('currencyUnit'),  
                }
            else:
                yield {
                    'keyword': response.meta['keyword'],
                    'page': response.meta['page'],
                    'position': response.meta['position'],
                    'id':  raw_product_data.get('id'),
                    'type':  raw_product_data.get('type'),
                    'name':  raw_product_data.get('name'),
                    'brand':  raw_product_data.get('brand'),
                    'averageRating':  raw_product_data.get('averageRating'),
                    'manufacturerName':  raw_product_data.get('manufacturerName'),
                    'shortDescription':  raw_product_data.get('shortDescription'),
                    'thumbnailUrl':  raw_product_data['imageInfo'].get('thumbnailUrl'),
                    'price':  raw_product_data['priceInfo']['currentPrice'].get('price'), 
                    'wasPrice':  "0", 
                    'currencyUnit':  raw_product_data['priceInfo']['currentPrice'].get('currencyUnit'),  
                }



