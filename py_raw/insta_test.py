import logging.config
import yaml
import random

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from time import sleep

from moduls import get_clear_number
from moduls import push_to_yaml
from moduls import get_from_yaml
from moduls import get_login_password

# чтение ymal-файла с настройками логирования, создание логгера
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)
logger = logging.getLogger(__name__)

# Получение логина/паролия из файла:
# TODO в файле с логином-паролем может быть несколько значений -> make system for switch users
login = (get_login_password())['login']
password = (get_login_password())['password']

# # Открытие браузера и задание времени ожидания элемента на странице
browser = webdriver.Chrome()
browser.implicitly_wait(6)


def login_page(login, password):
    """
    Получает логин, пароль для захода. Захожит в инсту, закрывает всплывающее окно о получении уведомлений:
    :param login: глобальная переменная
    :param password: глобальная переменная
    :return: None
    """

    link_for_login = 'https://www.instagram.com/accounts/login/?source=auth_switcher'
    try:
        browser.get(link_for_login)
        login_inputs = browser.find_elements_by_tag_name('input')
        login_inputs[0].clear()
        login_inputs[1].clear()
        login_inputs[0].send_keys(login)
        login_inputs[1].send_keys(password)
        submit_btn = browser.find_element_by_css_selector('button > div')
        submit_btn.click()
        not_now_btn = browser.find_elements_by_tag_name('div [role = "dialog"] > div > div > button')
        not_now_btn[-1].click()
    except:  # TODO нормально прописать разные варианты ексепшенов
        logger.exception('ERROR on logging form')
        browser.close()
        raise SystemExit


def get_list_of_followers_links(group_link, browser):
    """
    Get list of all followers in account
    :param group_link: link to the page in instagram, that we want to parse
    :return: List of links
    """
    list_of_followers = []  # list of all web-elements about follower
    list_of_links_to_followers = []  # list of clear links addresses

    try:
        browser.get(group_link)
        followers_count_button = browser.find_element_by_css_selector(
            '#react-root > section > main > div > header > section > ul > li:nth-child(2) > a > span'
        )
        followers_count_button.click()
        number_of_followers = get_clear_number(browser.find_element_by_css_selector(
            '#react-root > section > main > div > header > section > ul > li:nth-child(2) > a > span').text.strip()
        )  # Clearing out the signs of a space in number of followers

        while len(list_of_followers) < number_of_followers:
            list_of_followers = browser.find_elements_by_css_selector('div [role = "dialog"] li a:nth-child(1)')
            last_of_followers = list_of_followers[-1]
            # scroll to the bottom of followers list
            browser.execute_script("arguments[0].scrollIntoView();", last_of_followers)
            sleep(1)
            check_for_len_of_followers_list = len(list_of_followers) # save number of followers to the temp-var
            # checking numbers of followers again after scrolling down
            list_of_followers = browser.find_elements_by_css_selector('div [role = "dialog"] li a:nth-child(1)')
            if check_for_len_of_followers_list == len(list_of_followers):  # there are NO new records
                break

        for i in list_of_followers:  # TODO если у человека 0 фоловеров, забажит?
            list_of_links_to_followers.append(i.get_attribute('href'))

        logger.debug(f'value_of_followers: {number_of_followers}, '
                     f'len of list_of_links_to_followers: {len(list_of_links_to_followers)}')
    except IndexError:
        logger.exception('НЕ ПОЛУЧИЛОСЬ СОБРАТЬ НИ ОДНОГО ФОЛОВЕРА')
    except:  # TODO прописать правильно все ексепшены
        logger.exception('ERROR on group page')
        return list_of_links_to_followers
        # return list anyway, it can contain less number of followers, than user have

    return list_of_links_to_followers


def update_followers_links_file(list_of_links_to_followers: list):
    """
    На вход список, открываем проверочный ямл, сравниваем список со списком из ямла, и если во входном списке
    есть отличия — пушим их в ямл
    :param list_of_links_to_followers:
    :return:
    """
    try:  # пытаемся открыть словарь ссылок, если он есть
        list_for_compare = get_from_yaml('svetlana_fominykh')
        for item in list_of_links_to_followers:
            if item not in list_for_compare:
                list_for_compare.append(item)
        push_to_yaml('svetlana_fominykh', list_for_compare)
    except FileNotFoundError:
        push_to_yaml('svetlana_fominykh', list_of_links_to_followers)


def filter_followers_links_file():
    """
    Get list of followers from file, iter it, and check, if user have less than ___ subscribes - add him to outputlist
    else, ignore him
    :return:
    """
    filtered_output_list = []
    browser.implicitly_wait(5)
    try:
        list_for_filter = get_from_yaml('svetlana_fominykh')  # TODO запушить светлану фоминых в какой-то датник и брать оттуда
        print('len of input list:', len(list_for_filter))
        for link in list_for_filter:
            browser.get(link)
            numbers_of_following = get_clear_number(browser.find_element_by_css_selector(
                '#react-root > section > main > div > header > section > ul > li:nth-child(3) > a > span').text.strip()
                                                    )
            if numbers_of_following < 700:
                filtered_output_list.append(link)
                print(link)

            if len(filtered_output_list) % 50 == 0:
                push_to_yaml('svetlana_fominykh_filtered', filtered_output_list)
        print('len of output list:', len(filtered_output_list))
        push_to_yaml('svetlana_fominykh_filtered', filtered_output_list)
        browser.close()
    except NoSuchElementException:
        logger.exception('ERROR on filter_followers_step')
    finally:
        push_to_yaml('svetlana_fominykh_filtered', filtered_output_list)



def like_first_post_of_every_follower():
    list_of_links_followers = get_from_yaml('svetlana_fominykh_filtered')
    random.shuffle(list_of_links_followers)
    for link_to_the_follower_page in list_of_links_followers:
        browser.get(link_to_the_follower_page)

        try:
            browser.implicitly_wait(0.5)
            # здесь пытается поймать элмемент, которого нет, если страница пустая или закрытая
            link_to_latest_post_of_follower = browser.find_element_by_css_selector(
                '#react-root > section > main > div > div> article > '
                'div:nth-child(1) > div > div:nth-child(1) > div:nth-child(1) > a').get_attribute('href')
            browser.get(link_to_latest_post_of_follower)
            sleep(0.5)
            like_button = browser.find_element_by_css_selector('span [aria-label="Нравится"]')
            like_button.click()
            sleep(0.5)

        except NoSuchElementException:
            logger.debug(f'{link_to_the_follower_page} is close, or follower have no posts')





def browser_close():
    browser.close()
    raise SystemExit





if __name__ == '__main__':

    # login_page(login, password)
    # group_link = 'https://www.instagram.com/svetlana_fominykh/'
    # list_of_links_followers = get_list_of_followers_links(group_link)
    # update_followers_links_file(list_of_links_followers)
    # filter_followers_links_file()
    # like_first_post_of_every_follower()
    browser_close()
