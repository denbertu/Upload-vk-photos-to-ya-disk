import requests
import json
import logging
import configparser
from pprint import pprint

logging.basicConfig(level=logging.INFO)

config = configparser.ConfigParser()
config.read('settings.ini')

class VKConnector:

    def __init__(self, owner_id, token, photos_count, api_version='5.199'):
        self.owner_id = owner_id
        self.token = token
        self.photos_count = photos_count
        self.version = api_version

    def _get_id(self):
        params = {
            'access_token': self.token,
            'v': self.version,
            'owner_id': self.owner_id,
        }
        resp = requests.get(
            'https://api.vk.com/method/account.getProfileInfo', params=params
            )
        return resp.json()['response']['id']
    
    def build_url(self):
        self.params = {
            'access_token': self.token,
            'v': self.version,
            'owner_id': self.owner_id,
            'album_id': 'profile',
            'photo_sizes': '1',
            'extended': '1',
            'count': self.photos_count
        }
        if any(char.isalpha() for char in self.owner_id):
            id = str(self._get_id())
            self.params['owner_id'] = id
        else:
            self.params
        response = requests.get(
            'https://api.vk.com/method/photos.get', params=self.params
            )
        return response

    # def get_photos_info(self):
    #     photos_info = []
    #     response = self.build_url().json()
    #     if 'error' in response:
    #         return response['error']['error_msg']
    #     else:
    #         r = response.get('response').get('items')
    #         for i in r:
    #             for el in i['sizes']:
    #                 if el['type'] == 'z':
    #                     if any(
    #                         d.get("file_name") == i.get('likes').get('count') for d in photos_info
    #                         ):
    #                         photos_info.append(
    #                             {
    #                                 'file_name': i.get('date'),
    #                                 'size': el['type']
    #                                 }
    #                                 )
    #                     else:
    #                         photos_info.append(
    #                             {
    #                                 'file_name': i.get('likes').get('count'),
    #                                 'size': el['type']
    #                                 }
    #                                 )
    #         with open('results.json', 'w') as f:
    #             json.dump(photos_info, f, ensure_ascii=False, indent=4)
    #         # logging.info(self.build_url().status_code)
    #         return photos_info
    
    # def __str__(self) -> str:
    #     string = str(self.get_photos_info())
    #     return string

    # def get_photos_url(self):
    #     photos_high_res = {}
    #     response = self.build_url().json()
    #     if 'error' in response:
    #         return response['error']['error_msg']
    #     else:
    #         r = response.get('response').get('items')
    #         for i in r:
    #             for el in i['sizes']:
    #                 if el['type'] == 'z':
    #                     if i.get('likes').get('count') in photos_high_res:
    #                         photos_high_res[i.get('date')] = el['url']
    #                     else:
    #                         photos_high_res[i.get('likes').get('count')] = el['url']
    #         return photos_high_res

    # def get_photos_url(self):
    #     photos_high_res = {}
    #     response = self.build_url().json()
    #     if 'error' in response:
    #         return response['error']['error_msg']
    #     else:
    #         r = response.get('response').get('items')
    #         for i in r:
    #             max_height = 0
    #             max_width = 0
    #             for el in i['sizes']:
    #                 if el['height'] > max_height:
    #                     max_height = el['height']
    #                 if el['width'] > max_width:
    #                     max_width = el['width']
    #             for el in i['sizes']:
    #                 if max_width > max_height:
    #                     if el['width'] == max_width: 
    #                         if i.get('likes').get('count') in photos_high_res:
    #                             photos_high_res[i.get('date')] = el['url']
    #                         else:
    #                             photos_high_res[i.get('likes').get('count')] = el['url']
    #                 elif max_height > max_width:
    #                     if el['height'] == max_height: 
    #                         if i.get('likes').get('count') in photos_high_res:
    #                             photos_high_res[i.get('date')] = el['url']
    #                         else:
    #                             photos_high_res[i.get('likes').get('count')] = el['url']
    #         return photos_high_res

    def get_photos_url(self):
        photos_high_res = {}
        response = self.build_url().json()
        if 'error' in response:
            return response['error']['error_msg']
        else:
            r = response.get('response').get('items')
            for i in r:
                max_value = 0
                for el in i['sizes']:
                    if el['height'] > max_value:
                        max_value = el['height']
                    if el['width'] > max_value:
                        max_value = el['width']
                for el in i['sizes']:
                    if el['width'] == max_value: 
                        if i.get('likes').get('count') in photos_high_res:
                            photos_high_res[i.get('date')] = el['url']
                        else:
                            photos_high_res[i.get('likes').get('count')] = el['url']
                    elif el['height'] == max_value: 
                        if i.get('likes').get('count') in photos_high_res:
                            photos_high_res[i.get('date')] = el['url']
                        else:
                            photos_high_res[i.get('likes').get('count')] = el['url']
            return photos_high_res

    def download_photos(self):
        images_links = self.get_photos_url()
        if isinstance(images_links, dict):
            names = []
            for i in images_links.items():
                response = requests.get(i[1])
                filename = f'{i[0]}.jpg'
                names.append(filename)
                with open(filename, 'wb') as f:
                    f.write(response.content)
            logging.info('Photos was successfully downloaded')
            return names
        else:
            return images_links


class YAConnector:

    def __init__(self, ya_token, folder_name):
        self.ya_token = ya_token
        self.ya_headers = {'Authorization': f'OAuth {self.ya_token}'}
        self.folder_name = folder_name
        # self._ya_create_folder()
        # self.ya_upload_photos()


    def create_folder(self, folder_name):
            response = requests.put(
            url='https://cloud-api.yandex.net/v1/disk/resources',
            headers=self.ya_headers,
            params={'path': folder_name}
            )
            logging.info('Folder was created')
            return response.status_code

    def _get_upload_url(self, image, folder=None):
        params = None
        if folder == None:
            params = {'path': image}
        else:
            params = {'path': f'{folder}/{image}'}
        response = requests.get(
            url='https://cloud-api.yandex.net/v1/disk/resources/upload',
            headers=self.ya_headers,
            params=params
            )
        if 'error' in response.json():
            return response.json().get('message')
        else:
            return response.json().get('href')


    def upload_photos(self, names, folder=None):
        upload_url = None
        if isinstance(names, list):
            upload_counts = 0
            for i in names:
                with open(i, 'rb') as image:
                    if folder == None:
                        upload_url = self._get_upload_url(i)
                    else:
                        upload_url = self._get_upload_url(i, folder)   
                    if 'http' in upload_url:
                        files = {'file': image}
                        requests.put(upload_url, files=files)
                        upload_counts =+ 1
                    elif 'DiskResourceAlreadyExistsError' in upload_url:
                        continue
                    else:
                        return upload_url   
            if upload_counts > 0:
                    logging.info('Photos was uploaded')
        elif isinstance(names, str):
            upload_counts = 0
            with open(names, 'rb') as image:
                if folder == None:
                    upload_url = self._get_upload_url(names)
                else:
                    upload_url = self._get_upload_url(names, folder)
                if 'http' in upload_url:
                    files = {'file': image}
                    requests.put(upload_url, files=files)
                    upload_counts =+ 1
                else:
                    return upload_url   
            if upload_counts > 0:
                    logging.info('Photo was uploaded')


def get_photos_info(ya_token, folder=None):
    token = ya_token
    headers = {'Authorization': f'OAuth {token}'}
    base_url = 'https://cloud-api.yandex.net/v1/disk/resources/files'
    response = requests.get(
        base_url, headers=headers
        )
    if folder == None:
        photos_info = []
        for el in response.json()['items']:
            photos_info.append(
                {
                    'file_name': el['name'],
                    'size': el['size']
                    }
                    )
    else:
        photos_info = []
        for el in response.json()['items']:
            if folder in el['path']:
                photos_info.append(
                    {
                        'file_name': el['name'],
                        'size': el['size']
                        }
                        )
    with open('results.json', 'w') as f:
        json.dump(photos_info, f, ensure_ascii=False, indent=4)
    logging.info('Json was created')
    return photos_info


vk = VKConnector(config['VK']['userid'], config['VK']['token'], 2)
y = YAConnector(config['YA']['token'], 'images')
y.create_folder('images')
y.upload_photos(vk.download_photos(), 'images')
json_ = get_photos_info(config['YA']['token'], 'images')
pprint(json_)
