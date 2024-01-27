# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import sqlite3
from datetime import datetime

class WalmartScraperPipeline:
    def __init__(self):
        ## Create/Connect to database
        self.con = sqlite3.connect('price.db')

        ## Create cursor, used to execute commands
        self.cur = self.con.cursor()
        
        ## Create quotes table if none exists
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS price(
            keyword TEXT,
            page INTEGER,
            position TEXT,
            id       TEXT,
            type      TEXT,
            name   TEXT,
            brand   TEXT,
            average_rating  REAL,
            manufacturer  TEXT,
            short_description  TEXT,
            url  TEXT,
            current_price REAL,
            original_price REAL,
            currency_unit TEXT,
            image_url TEXT,
            created DATE,
            updated DATE             
        )
        """)

    def process_item(self, item, spider):
        ## Check to see if text is already in database 
        self.cur.execute("select * from price where id = ?", (item['id'],))
        result = self.cur.fetchone()
        dateValue = datetime.now()

        ## If it is in DB, create log message
        if result:
            spider.logger.warn("Item already in database: %s" % item['id'])
            ## Update with current price statement
            self.cur.execute("""
                UPDATE price SET current_price = ?, created = ?,updated = ? WHERE id = ?
            """,
            (
                str(item['price']),
                dateValue,
                dateValue,
                str(item['id'])
            ))

            ## Execute insert of data into database
            self.con.commit()
        
        ## If text isn't in the DB, insert data
        else:

            ## Define insert statement
            self.cur.execute("""
                INSERT INTO price (keyword, page, position,id , type, name, brand, average_rating, manufacturer, short_description, url, current_price, original_price, currency_unit,image_url,created,updated) VALUES (?, ?, ?,?, ?, ?,?, ?, ?,?, ?, ?,?,?,?,?,?)
            """,
            (
                str(item['keyword']),
                str(item['page']),
                str(item['position']),
                str(item['id']),
                str(item['type']),
                str(item['name']),
                str(item['brand']),
                str(item['averageRating']),
                str(item['manufacturerName']),
                str(item['shortDescription']),
                str(item['thumbnailUrl']),
                str(item['price']),
                 str(item['wasPrice']),
                str(item['currencyUnit']),
                str(item['imageUrl']),
                dateValue,
                dateValue
            ))

            ## Execute insert of data into database
            self.con.commit()

        return item
