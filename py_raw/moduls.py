import pickle
import yaml
import random
import logging.config
from time import sleep
from selenium.common.exceptions import NoSuchElementException


def get_clear_number(text:any) -> int:
    """
    Получает текст или число, посимвольно по нему проходит и возвращает только цифры из строки
    :param text:
    :return:
    """
    output_number: int = ''
    for i in str(text):
        if i.isdigit():
            output_number += i
    return int(output_number)



# --------------------------------------------------------------------------------------------
# ПУШИМ СПИСОК В БИНАРНИК
def push_to_dat(name, list):
    name = '../dats/' + name
    f = open(name, 'wb')
    pickle.dump(list, f)
    f.close()


# --------------------------------------------------------------------------------------------
# ПУШИМ В YAML
def push_to_yaml(name_of_file: str, list: "list or dict"):
    to_yaml = list
    with open(f'../dats/{name_of_file}.yaml', 'w') as f:
        yaml.dump(to_yaml, f)




# --------------------------------------------------------------------------------------------
# ДОСТАЕМ ИЗ YAML
def get_from_yaml(name_of_file: str):
    with open(f'../dats/{name_of_file}.yaml') as f:
        dict_from_yaml = yaml.safe_load(f)
    return dict_from_yaml



# --------------------------------------------------------------------------------------------
# ЛОГИН и ПАРОЛЬ из ЯМЛА
def get_login_password(user_name, logger):
    """
        :param user_name: получает строку с именем пользователя
        :return: логин и пароль из списка в ямле с логином и паролем указанного пользователя
        """
    with open('./../dats/lpt.yaml') as f:
        dict_from_yaml = yaml.safe_load(f)
    login = dict_from_yaml[user_name][0]
    password = dict_from_yaml[user_name][1]
    if login and password:
        # print(f'Успешно достал логин {login} и пароль {password} из файла')
        logger.debug(f'Достал логин {login} и пароль {password} из файла')
    return login, password


# --------------------------------------------------------------------------------------------
# проходим страницу логина
def logging_in(browser, login, password, logger):
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
        sleep(3)
        not_now_btn = browser.find_elements_by_tag_name('div [role = "dialog"] > div > div > button')
        not_now_btn[-1].click()
        # print('Успешно залогинился')
        logger.debug('Успешно залогинился')
    except Exception as e:  # TODO нормально прописать разные варианты ексепшенов
        logger.exception('ERROR on logging form', e)
        browser.close()
        raise SystemExit


# --------------------------------------------------------------------------------------------
# достаем из ямла список ссылок на группы, пользователей которых мы хотим съесть
def get_links_to_groups(logger, user_name):
    """
    :param user_name: имя пользователя, для которого мы будем искать интересные группы
    :return: список с сылками на групппы, интересные для этого пользователя
    """
    try:
        with open('./../dats/group_links.yaml', 'r') as f:
            dict_from_yaml = yaml.safe_load(f)
        groups_links_list = dict_from_yaml[user_name]
        if len(groups_links_list) > 0:
            logger.debug(f'Достал список ссылок на группы, у которых будем брать фоловеров')
            # print(f'Успешно достал список ссылок на группы, у которых будем брать фоловеров')
            return groups_links_list
    except Exception as e:
        logger.error(e)


# --------------------------------------------------------------------------------------------
# получаем полный список пользователей, интересующих этого юзер-нейма
def get_full_list_of_followers_links(browser, logger, list_of_links_to_group, user_name):
    list_of_followers = []
    dict_of_all_followers = {}
    dict_of_all_followers['all_followers'] = []
    try:
        with open(f'../dats/{user_name}_full_followers.yaml', 'r') as full_followers_file_name:
            dict_of_all_followers = yaml.safe_load(full_followers_file_name)
    except (FileExistsError, FileNotFoundError):
        logger.debug(f'для группы {user_name} пользователей еще не искали')

    for link_to_group in list_of_links_to_group:
        logger.debug(f'Cобираю подписчиков у группы: {link_to_group}')
        try:
            browser.get(link_to_group)
            followers_count_button = browser.find_element_by_css_selector(
                '#react-root > section > main > div > header > section > ul > li:nth-child(2) > a > span'
            )  # находим кнопку с фоловерами
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
                check_for_len_of_followers_list = len(list_of_followers)  # save number of followers to the temp-var
                # checking numbers of followers again after scrolling down
                list_of_followers = browser.find_elements_by_css_selector('div [role = "dialog"] li a:nth-child(1)')
                if check_for_len_of_followers_list == len(list_of_followers):  # there are NO new records
                    break
            for i in list_of_followers:  # TODO если у человека 0 фоловеров, забажит?
                print(i.get_attribute('href'))
                if i.get_attribute('href') in dict_of_all_followers['all_followers']:
                    print('этого фоловера у этой группы мы уже находили')
                    continue
                dict_of_all_followers['all_followers'].append(i.get_attribute('href'))
            logger.debug(f'Собрал {number_of_followers} фоловеров')

        except Exception as e:
            logger.error('Ошибка на странице:', link_to_group)
            logger.error(e)

    with open(f'../dats/{user_name}_full_followers.yaml', 'w') as full_followers_file_name:
        yaml.dump(dict_of_all_followers, full_followers_file_name)

    # блок ниже создает также файл с фильтрованными фоловерами и пихает туда один адрес
    # сделано это, чтобы следующий модуль не глючил по пустому словарю
    empty_dict_of_filtered_followers = {'active_followers': [link_to_group]}
    empty_dict_of_bad_followers = {'bad_followers': [link_to_group]}

    try:
        with open(f'../dats/{user_name}_filtered_followers.yaml', 'r') as file_of_filtered_followers:
            pass
    except (FileNotFoundError, FileExistsError):
        with open(f'../dats/{user_name}_filtered_followers.yaml', 'w') as filtered_followers_file_name:
            yaml.dump(empty_dict_of_filtered_followers, filtered_followers_file_name)
            yaml.dump(empty_dict_of_bad_followers, filtered_followers_file_name)

    if len(['all_followers']) > 0:
        logger.debug(f'Собрал список фоловеров, их: {len(dict_of_all_followers["all_followers"])}, засунул их в файл')
        # print('Собрал список фоловеров, их:' + len(dict_of_links_to_folowers[user_name]) + ', засунул их в файл')


# --------------------------------------------------------------------------------------------
# ЧИСТИМ СЛОВАРЬ ССЫЛОК НА ПОЛЬЗОВАТЕЛЕЙ
def get_dict_of_filtered_followers(browser, logger, user_name):
    """
    получает на вход большой словарь с ключем-юзернеймом, и проходит по всем ссылкам внутри, проверяя их на
    количество подписчиков
    """
    # получаем словарь всех пользователей из файла
    with open(f'../dats/{user_name}_full_followers.yaml', 'r') as file_of_all_followers:
        dict_of_all_followers = yaml.safe_load(file_of_all_followers)
    logger.debug(f'общее количество фоловеров: {len(dict_of_all_followers["all_followers"])}')
    # получаем словарь всех чистых пользователей из файла
    with open(f'../dats/{user_name}_filtered_followers.yaml', 'r') as file_of_filtered_followers:
        dict_of_filtered_followers = yaml.safe_load(file_of_filtered_followers)
    for key, value in dict_of_filtered_followers.items():
        print(key, value)
    i = 1
    for follower_link in dict_of_all_followers['all_followers']:
        print(f'проверяю {i} фоловера из {len(dict_of_all_followers["all_followers"])}', end=' — ')
        i += 1
        try:
            if (follower_link in dict_of_filtered_followers['active_followers'] or
                    follower_link in dict_of_filtered_followers['bad_followers']):
                print('этого уже проверяли')
                continue
            browser.get(follower_link)
            numbers_of_following = get_clear_number(browser.find_element_by_css_selector(
                '#react-root > section > main > div > header > section > ul > li:nth-child(3)').text.strip()
                                                    )
            # react-root > section > main > div > header > section > ul > li:nth-child(3) > a
            if numbers_of_following < 500:  # (если количество подписчиков у пользователя меньше 500 то норм)
                dict_of_filtered_followers['active_followers'].append(follower_link)
                print('активный, живой фоловер')
            else:
                dict_of_filtered_followers['bad_followers'].append(follower_link)
                print('бот, скорее всего')
                continue
        except NoSuchElementException:
            logger.error('ERROR on filter_followers_step, link with error:', follower_link)
        # except Exception as e:
        #     logger.error(e, follower_link)
        finally:
            with open(f'../dats/{user_name}_filtered_followers.yaml', 'w') as f:
                yaml.dump(dict_of_filtered_followers, f)
    if (len(dict_of_filtered_followers['active_followers']) +
        len(dict_of_filtered_followers['bad_followers'])) == len(dict_of_all_followers["all_followers"])+2:
        logger.debug(f'Профильтровал всех фолловеров, активных: {len(dict_of_filtered_followers["active_followers"])-1}, плохих фолловеров: {len(dict_of_filtered_followers["bad_followers"])-1}')
        for key, value in dict_of_filtered_followers.items():
            print(key, value)
    else:
        logger.debug(f'Где-то потерял {len(dict_of_all_followers["all_followers"])+2 - (len(dict_of_filtered_followers["active_followers"]) + len(dict_of_filtered_followers["bad_followers"]))}')


# --------------------------------------------------------------------------------------------
# ЛАЙКАЕМ ПОСЛЕДНИЙ ПОСТ
def like_last_users_post(browser, logger, user_name):
    with open(f'./../dats/{user_name}_filtered_followers.yaml', 'r') as file_of_filtered_followers:
        list_of_followers_links = yaml.safe_load(file_of_filtered_followers)['active_followers']
        random.shuffle(list_of_followers_links)
        for follower_link in list_of_followers_links:
            try:
                browser.implicitly_wait(0.5)
                browser.get(follower_link)
                # здесь пытается поймать элмемент, которого нет, если страница пустая или закрытая
                link_to_latest_post_of_follower = browser.find_element_by_css_selector(
                    '#react-root > section > main > div > div> article > '
                    'div:nth-child(1) > div > div:nth-child(1) > div:nth-child(1) > a').get_attribute('href')
            except NoSuchElementException:
                logger.debug(f'{follower_link} is close, or follower have no posts')
            except Exception as e:
                logger.error(e)
                logger.error('что-то полшло не так на странице', follower_link)

            try:
                browser.get(link_to_latest_post_of_follower)
                sleep(0.5)
                like_button = browser.find_element_by_css_selector('span [aria-label="Нравится"]')
                like_button.click()
                sleep(0.5)
            except UnboundLocalError:
                print('не нашел кнопки лайк на странице')
                continue
            except NoSuchElementException:
                continue



# --------------------------------------------------------------------------------------------
# ДОСТАЕТ ОДИН СЛУЧАЙНЫЙ КОММЕНТ ИЗ СПИСКА
def get_words_for_comment():
    list_of_comments = get_from_yaml('comments')
    random.shuffle(list_of_comments)
    return list_of_comments[-1]


# --------------------------------------------------------------------------------------------
# созадет и возвращает логгер для логирования в файл
def get_logger():
    with open('./../dats/config.yaml', 'r') as f:
        config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
    logger = logging.getLogger(__name__)
    return logger



if __name__ == '__main__':
    test = get_clear_number('7 209')
    print(test)
    comment = get_words_for_comment()
    print(comment)