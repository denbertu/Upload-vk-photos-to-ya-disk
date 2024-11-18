import requests
import json
import logging


class UPLOADPHOTOS:
    logging.basicConfig(level=logging.INFO)

    def __init__(self, vk_token, vk_owner_id,  ya_token, vk_api_version='5.199', photos_count=5):
        self.vk_token = vk_token
        self.version = vk_api_version
        self.vk_owner_id = vk_owner_id
        self.ya_token = ya_token
        self.photos_count = photos_count
        self.ya_headers = {'Authorization': f'OAuth {self.ya_token}'}
        self._ya_create_folder()
        self.ya_upload_photos()
        self.__str__()

    def _vk_build_url(self):
        self.vk_params = {
        'access_token': self.vk_token,
        'v': self.version,
        'owner_id': self.vk_owner_id,
        'album_id': 'profile',
        'photo_sizes': '1',
        'extended': '1',
        'count': self.photos_count
        }
        response = requests.get(
            'https://api.vk.com/method/photos.get', params=self.vk_params
            )
        return response

    def _vk_get_photos_info(self):
        photos_info = []
        response = self._vk_build_url().json()
        if 'error' in response:
            return response['error']['error_msg']
        else:
            r = response.get('response').get('items')
            for i in r:
                for el in i['sizes']:
                    if el['type'] == 'z':
                        if any(
                            d.get("file_name") == i.get('likes').get('count') for d in photos_info
                            ):
                            photos_info.append(
                                {
                                    'file_name': i.get('date'),
                                    'size': el['type']
                                    }
                                    )
                        else:
                            photos_info.append(
                                {
                                    'file_name': i.get('likes').get('count'),
                                    'size': el['type']
                                    }
                                    )
            with open('results.json', 'w') as f:
                json.dump(photos_info, f, ensure_ascii=False, indent=4)
            # logging.info(self._vk_build_url().status_code)
            return photos_info
    
    def __str__(self) -> str:
        string = str(self._vk_get_photos_info())
        return string

    def _vk_get_photos_url(self):
        photos_high_res = {}
        response = self._vk_build_url().json()
        if 'error' in response:
            return response['error']['error_msg']
        else:
            r = response.get('response').get('items')
            for i in r:
                for el in i['sizes']:
                    if el['type'] == 'z':
                        if i.get('likes').get('count') in photos_high_res:
                            photos_high_res[i.get('date')] = el['url']
                        else:
                            photos_high_res[i.get('likes').get('count')] = el['url']
            return photos_high_res

    def _vk_download_photos(self):
        images_links = self._vk_get_photos_url()
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
    
    def _ya_create_folder(self):
            response = requests.put(
            url='https://cloud-api.yandex.net/v1/disk/resources',
            headers=self.ya_headers,
            params={'path': 'Images'}
            )
            logging.info('Folder was created')
            return response.status_code

    def ya_get_upload_url(self, image_path):
        response = requests.get(
            url='https://cloud-api.yandex.net/v1/disk/resources/upload',
            headers=self.ya_headers,
            params={'path': f'Images/{image_path}'}
            )
        if 'error' in response.json():
            return response.json().get('message')
        else:
            return response.json().get('href')


    def ya_upload_photos(self):
            names_list = self._vk_download_photos()
            if isinstance(names_list, list):
                upload_counts = 0
                for i in names_list:
                    with open(i, 'rb') as image: 
                        upload_url = self.ya_get_upload_url(i)
                        if 'http' in upload_url:
                            files = {'file': image}
                            requests.put(upload_url, files=files)
                            # logging.info('Photos was uploaded')
                            upload_counts =+ 1
                        elif 'DiskResourceAlreadyExistsError' in upload_url:
                            continue
                        else:
                            return upload_url   
                if upload_counts > 0:
                     logging.info('Photos was uploaded')
            else:
                return names_list








