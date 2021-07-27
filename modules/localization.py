from modules.config import config

import os
import json


locales = [name.split('.')[0] for name in os.listdir('locale')]
locale = config['MISC'].get('language') if len(config['MISC'].get('language')) == 2 else 'en'


def load_locale(lang_name: str):
    lang: dict = {}
    app_crash = False

    try:
        with open(f'locale/{lang_name}.json', encoding='utf-8') as f:
            lang = json.load(f)
    except TypeError:
        print('Localisation not found!')
        app_crash = True

    return lang, app_crash
