import requests

from bs4 import BeautifulSoup as bs

list_of_followers_links = [
    'https://www.instagram.com/alekssandra_alekseeva/', 'https://www.instagram.com/kat_ushaa/',
    'https://www.instagram.com/lubov_908/', 'https://www.instagram.com/lub.kraeva/',
    'https://www.instagram.com/vera_sofia_arina/', 'https://www.instagram.com/veralevnail/',
    'https://www.instagram.com/termish_velur.kirov/'
]

def filter_list_followers_links(list_of_followers_links):
    for item in list_of_followers_links:
        session = requests.session()
        req = session.get(item)
        if req.status_code == 200:
            soup = bs(req.content, 'html.parser')
            first_post_link = soup.find(
                '#react-root > section > main > div > div > article > div > div > div > div > a')
            print(first_post_link)

if __name__ == '__main__':
    filter_list_followers_links(list_of_followers_links)

