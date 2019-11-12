import pickle
import yaml
import random


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
def get_login_password():
    with open('lpt.yaml') as f:
        dict_from_yaml = yaml.safe_load(f)
    return dict_from_yaml

# --------------------------------------------------------------------------------------------
# ДОСТАЕТ ОДИН СЛУЧАЙНЫЙ КОММЕНТ ИЗ СПИСКА
def get_words_for_comment():
    list_of_comments = get_from_yaml('comments')
    random.shuffle(list_of_comments)
    return list_of_comments[-1]


if __name__ == '__main__':
    test = get_clear_number('7 209')
    print(test)
    comment = get_words_for_comment()
    print(comment)