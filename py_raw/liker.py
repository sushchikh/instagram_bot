import logging.config
import yaml
import random

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from time import sleep

from moduls import get_from_yaml


# чтение ymal-файла с настройками логирования, создание логгера
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)
logger = logging.getLogger(__name__)

# # Открытие браузера и задание времени ожидания элемента на странице
browser = webdriver.Chrome()
browser.implicitly_wait(6)


def like_first_post_of_every_follower():
    list_of_links_followers = get_from_yaml('svetlana_fominykh_filtered')
    random.shuffle(list_of_links_followers)
    for link_to_the_follower_page in list_of_links_followers[:50]:
        browser.get(link_to_the_follower_page)

        try:
            browser.implicitly_wait(0.5)
            # здесь пытается поймать элмемент, которого нет, если страница пустая или закрытая
            link_to_latest_post_of_follower = browser.find_element_by_css_selector(
                '#react-root > section > main > div > div> article > '
                'div:nth-child(1) > div > div:nth-child(1) > div:nth-child(1) > a').get_attribute('href')

            browser.get(link_to_latest_post_of_follower)
            # sleep(0.5)
            like_button = browser.find_element_by_css_selector('span [aria-label="Нравится"]')
            like_button.click()

            alternative_like_button = browser.find_element_by_css_selector('span.glyphsSpriteHeart__outline__24__grey_9')
            print(alternative_like_button)
            alternative_like_button.click()
            sleep(2)

        except NoSuchElementException:
            logger.debug(f'{link_to_the_follower_page} is close, or follower have no posts')





def browser_close():
    browser.close()
    raise SystemExit





if __name__ == '__main__':
    like_first_post_of_every_follower()
    browser_close()
