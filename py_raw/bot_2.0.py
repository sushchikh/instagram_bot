from selenium import webdriver

from moduls import get_logger
from moduls import get_login_password
from moduls import logging_in
from moduls import get_links_to_groups
from moduls import get_full_list_of_followers_links
from moduls import get_dict_of_filtered_followers
from moduls import like_last_users_post

if __name__ == "__main__":
    # user_name = 'animation'
    user_name = 'belka_color'
    # user_name = 'a.sushchikh@gmail.com'
    logger = get_logger()  # create logger
    login, password = get_login_password(user_name, logger)

    browser = webdriver.Chrome()
    browser.implicitly_wait(5)

    logging_in(browser, login, password, logger)
    list_of_group_links = get_links_to_groups(logger, user_name)
    get_full_list_of_followers_links(browser, logger, list_of_group_links, user_name)  # отключаемый модуль
    get_dict_of_filtered_followers(browser, logger, user_name)
    like_last_users_post(browser, logger, user_name)

    browser.close()
