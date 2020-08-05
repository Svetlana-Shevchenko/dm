import scrapy
from scrapy.loader import ItemLoader
from homework5.items import authorItem, postItem


class HabrSpider(scrapy.Spider):
    name = 'habr'
    allowed_domains = ['habr.com']
    start_urls = ['https://habr.com/ru/']

    author_css_selectors = {
        'author_name': 'span.user-info__nickname::text',
        'author_url': 'a.post__user-info::attr("href")'
    }

    line_post_css_selectors = {
        'title': 'a.post__title_link::text',
        'post_url': 'a.post__title_link::attr("href")'
    }

    post_css_selectors = {
        'title': 'span.post__title-text::text',
        'comments': 'span.post-stats__comments-count::text',
        'images': 'div.post__text.post__text-html img::attr("src")',
        'author_id': 'a.post__user-info.user-info::attr("href")'
    }

    def parse(self, response):
        base_post = response.css('article.post_preview')

        for post in base_post:
            item = ItemLoader(authorItem(), response)
            for key, value in self.author_css_selectors.items():
                item.add_value(key, post.css(value).extract())

            yield item.load_item()
            yield response.follow(item.get_collected_values('author_url')[0]
                                  + 'posts/',
                                  callback=self.parse_author)

        yield response.follow(response.css(self.line_post_css_selectors['post_url']).extract()[0],
                              callback=self.parse_post)

    def parse_post(self, response):
        base_post = response.css('div.content_left.js-content_left')
        item = ItemLoader(postItem(), response)

        for key, value in self.post_css_selectors.items():
            item.add_value(key, base_post.css(value).extract())

        item.add_value('post_url', response.url)

        yield item.load_item()


    def parse_author(self, response):
        for post in response.css('li.content-list__item.content-list__item_post.shortcuts_item'):
            yield response.follow(post.css('a.post__title_link::attr("href")').extract()[0],
                                  callback=self.parse_post)
