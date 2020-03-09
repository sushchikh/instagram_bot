import yaml

with open(f'../dats/a.sushchikh@gmail.com_filtered_followers.yaml', 'r') as file_of_filtered_followers:
    dict_of_filtered_followers = yaml.safe_load(file_of_filtered_followers)
for key, value in dict_of_filtered_followers.items():
    print(key, value)