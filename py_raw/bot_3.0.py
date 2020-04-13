from instapy import InstaPy as ip

username = 'a89638857493@gmail.com'
password = 'Mop$513493'


session = ip(username=username, password=password)
session.login()
session.like_by_tags(['animation'], amount=5)

