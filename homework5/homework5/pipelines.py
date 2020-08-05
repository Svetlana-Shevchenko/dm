# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient


class Homework5Pipeline:

    def __init__(self):
        self.mongo = MongoClient('172.22.200.92', 27017).habr

    def get_prop(self, doc_type):
        return 'post_url' if doc_type == 'post' else 'author_url'

    def check_doc_exist(self, doc_type, val):
        return bool(self.mongo[doc_type].count_documents(
            {self.get_prop(doc_type): val}
        ))

    def add_author_id(self, item):
        return self.mongo.author.find_one({'author_url': item.get('author_id')[0]})['_id']

    def process_item(self, item, spider):
        doc_type = type(item).__name__[:-4]

        if doc_type == 'post':
            item['author_id'] = self.add_author_id(item)

        if not self.check_doc_exist(doc_type, item.get(self.get_prop(doc_type))):
            self.mongo[doc_type].insert_one(item)
        else:
            self.mongo[doc_type].find_and_modify({
                self.get_prop(doc_type): item.get(self.get_prop(doc_type))
            }, item)

        return item
