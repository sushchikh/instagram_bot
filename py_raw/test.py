import random
from moduls import get_from_yaml

def get_words_for_comment():
    list_of_comments = get_from_yaml('comments')
    random.shuffle(list_of_comments)
    return list_of_comments[-1]

if __name__ == '__main__':
    comment = get_words_for_comment()
    print(comment)