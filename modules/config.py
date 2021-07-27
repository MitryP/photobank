import configparser
import os


config = configparser.ConfigParser()


def save_config():
    with open('config.ini', 'w') as configfile:
        config.write(configfile)


if not os.path.exists('config.ini'):
    print('Creating config.ini..')
    config['SERVER'] = {
        'host': '127.0.0.1',
        'port': 5500,
        'debug': 'no'
    }
    config['PHOTO'] = {
        'upload_folder': 'photos',
        'database_index_timeout': 1800,
        'upload_folder_index_timeout': 300
    }
    config['MISC'] = {
        'language': 'en',
        'setup_done': 'no',
    }
    save_config()

else:
    config.read('config.ini')
