from datetime import datetime
from pathlib import Path
from unittest import mock

import pytest
from scrapy import Spider, signals
from scrapy.crawler import Crawler, CrawlerProcess
from scrapy.http import HtmlResponse
from scrapy.signalmanager import dispatcher
from scrapy.utils.project import get_project_settings

from slugify import slugify

from passbot.crawlers.items import EmailHistoryItem
from passbot.crawlers.spiders.vitemonpasseport import ViteMonPasseport44Spider

from tests import BASE_SAMPLES


class TestSpiderViteMonPasseport44:

    @classmethod
    def setup_class(cls):
        cls.crawler: Crawler = Crawler(
            spidercls=ViteMonPasseport44Spider,
            settings={
                'REQUEST_FINGERPRINTER_IMPLEMENTATION': '2.7',
            },
        )
        cls.spider: Spider = ViteMonPasseport44Spider.from_crawler(cls.crawler)

    def test_parse(self):
        content = (Path(BASE_SAMPLES) / 'vitemonpasseport' / 'p1.html').read_text()
        scrapy_response = HtmlResponse(
            ViteMonPasseport44Spider.start_urls[0],
            body=content,
            encoding='utf-8',
        )

        items = list((self.spider.parse(scrapy_response)))
        assert len(items) == 21

        item = items[0]
        assert isinstance(item, EmailHistoryItem)
        assert item['spider'] == self.spider.name
        assert item['place'] == slugify('Mairie de NANTES')
        assert item['zipcode'] == '44000'
        assert item['link'] == 'https://www.vitemonpasseport.fr/demande-passeport-mairie-de-nantes-44000'
        assert item['date_slot']

        item = items[1]
        assert item['date_slot'].strftime('%Y-%m-%d %H:%M') == datetime(2023, 4, 5, 15, 0).strftime('%Y-%m-%d %H:%M')

    @pytest.mark.skip("@TODO")
    def test_pagination(self):
        pass  # @todo play with scraper + mock for html response?


class TestCrawlerViteMonPasseport44:

    # @classmethod
    # def setup_class(cls):
    #     settings = get_project_settings()
    #     settings.set('TWISTED_REACTOR', 'twisted.internet.epollreactor.EPollReactor')
    #
    #     # 'twisted.internet.asyncioreactor.AsyncioSelectorReactor'
    #     cls.crawler: Crawler = Crawler(
    #         spidercls=ViteMonPasseport44Spider,
    #         settings=settings,
    #         # init_reactor=True,
    #     )
    #     cls.spider: Spider = ViteMonPasseport44Spider.from_crawler(cls.crawler)

    # @mock.patch('passbot.crawlers.spiders.vitemonpasseport')
    def test_crawl(self):
        # for foo in iter(self.crawler.crawl()):
        #     pass

        # process = CrawlerProcess(get_project_settings())
        #
        # # 'followall' is the name of one of the spiders of the project.
        # process.crawl('followall', domain='scrapy.org')
        # process.start()  # the script will block here until the crawling is finished
        results = []

        def crawler_results(signal, sender, item, response, spider):
            results.append(item)

        dispatcher.connect(crawler_results, signal=signals.item_passed)

        runner = CrawlerProcess(settings=get_project_settings())
        runner.crawl(ViteMonPasseport44Spider)
        runner.start()

        return results
