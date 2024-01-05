import requests
import json
import configparser
from pprint import pprint
from urllib.parse import urlencode
import logging

# Получение токена
# app_id = '51820304'
# auth_base_url = 'https://oauth.vk.com/authorize'
# params = {
#     'client_id': app_id,
#     'redirect_uri': 'https://oauth.vk.com/blank.html',
#     'display': 'page',
#     'scope': 'status, photos',
#     'response_type': 'token'
# }
#
# outh_url = f'{auth_base_url}?{urlencode(params)}'
# print(outh_url)

config = configparser.ConfigParser()
config.read('config.ini')
TOKEN = config['my_config']['TOKEN']
TOKEN_YD_POLIGON = config['my_config']['TOKEN_YD_POLIGON']
TOKEN_YD = 'OAuth ' + TOKEN_YD_POLIGON

base_url = 'https://cloud-api.yandex.net'  # для загрузки на яндекс диск
url_create_folder = base_url + '/v1/disk/resources'
url_get_link = base_url + '/v1/disk/resources/upload'
headers_dict = {'authorization': TOKEN_YD}
class VKAPIClient:
    API_BASE_URL = 'https://api.vk.com/method'
    def __init__(self, token, user_id):
        self.token = token
        self.user_id = user_id
    def get_common_params(self):
        return {
            'access_token': self.token,
            'v': '5.131'
        }
    def get_status(self):
        params = self.get_common_params()
        params.update({'user_id': self.user_id})
        response = requests.get(f'{self.API_BASE_URL}/status.get', params=params)
        return response.json().get('response', {}).get('text')
    def set_status(self, new_status):
        params = self.get_common_params()
        params.update({'user_id': self.user_id, 'text': new_status})
        response = requests.get(f'{self.API_BASE_URL}/status.set', params=params)
        response.raise_for_status()

    def replace_status(self, target, replace_string):
        status = self.get_status()
        new_status = status.replace(target, replace_string)
        self.set_status(new_status)
    def get_profile_photos(self, owner_id):
        params = self.get_common_params()
        params.update({'owner_id': self.user_id, 'album_id': 'profile', 'extended': 1})
        response = requests.get(f'{self.API_BASE_URL}/photos.get', params=params)
        result = response.json()
        dikt_file = {}
        for i in range(len(result.get('response').get('items'))):
            x = result.get('response').get('items')[i].get('sizes')[-1].get('url')
            y = result.get('response').get('items')[i].get('sizes')[-1].get('type')
            z = result.get('response').get('items')[i].get('likes').get('count')
            date = result.get('response').get('items')[i].get('date')
            if z not in dikt_file:
                dikt_file[z] = {x: y}
            else:
                dikt_file[str(z) + str(date)] = {x: y}
        return dikt_file
    def get_load_photos(self, owner_id):
        file_name = []
        size = []
        dikt_file = self.get_profile_photos(owner_id)
        for i in dikt_file:
            params_dict = {'path': f'Папка №{owner_id}/{i}.jpg'}
            response = requests.get(list(dikt_file.get(i).keys())[0])
            with open(f'{i}.jpg', 'wb') as file:
                file.write(response.content)
                response = requests.get(url_get_link, params=params_dict, headers=headers_dict)
                url_for_upload = response.json().get('href')
                with open(f'{i}.jpg', 'rb') as file:
                    response = requests.post(url_for_upload, files={'file': file}, headers=headers_dict)
                    file_name.append(f'{i}.jpg')
                    size.append(list(dikt_file.get(i).values())[0])
            file_for_load = {'file_name': file_name, 'size': size}
            with open('file_for_load.json', 'w') as file:
                json.dump(file_for_load, file)
        print(file_for_load)
def create_folder(owner_id):
    params_folder = {'path': f'Папка №{owner_id}'}
    response = requests.put(url_create_folder,
                            params=params_folder,
                            headers=headers_dict)

if __name__ == '__main__':
    # vk_client = VKAPIClient(TOKEN, 17088098)
    # print(vk_client.get_status())
    create_folder(17088098)
    vk_client = VKAPIClient(TOKEN, 17088098)
    photos_info= vk_client.get_load_photos(17088098)
    logging.basicConfig(level=logging.INFO,
                        filename="py_log.log",
                        filemode="w",
                        format="%(asctime)s %(levelname)s %(message)s")
    logging.debug("A DEBUG Message")
    logging.info("An INFO")
    logging.warning("A WARNING")
    logging.error("An ERROR")
    logging.critical("A message of CRITICAL severity")








