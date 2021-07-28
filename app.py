from datetime import datetime
import functools
import time
# from typing import Optional
from modules.config import config, save_config
from modules.localization import locale, locales, load_locale
from modules.datify import Datify

import exifread
import os
from PIL import Image
from flask import Flask, render_template, request, redirect, url_for, send_file
from werkzeug.datastructures import FileStorage
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['UPLOAD_FOLDER'] = (config['PHOTO'].get('upload_folder'))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///photos.db'
backslash = '\\'
app.add_url_rule(
    f'/{app.config["UPLOAD_FOLDER"]}/<filename>', endpoint='photos'
)
db = SQLAlchemy(app)

database_index_timeout = config['PHOTO'].getint('database_index_timeout')
upload_folder_index_timeout = config['PHOTO'].getint('upload_folder_index_timeout')

LAST_DATABASE_INDEX = None
LAST_FOLDER_INDEX = None


locale = locale
lang, APP_CRASH = load_locale(locale)


def view_function_timer(prefix='', writeto=print):
    def decorator(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            try:
                t0 = time.time()
                return func(*args, **kwargs)
            finally:
                t1 = time.time()
                writeto(
                    'View Function',
                    '({})'.format(prefix) if prefix else '',
                    func.__name__,
                    args[1:],
                    'Took',
                    '{:.2f}ms'.format(1000 * (t1 - t0)),
                )

        return inner

    return decorator


@view_function_timer()
def create_database_if_absent():
    if not os.path.exists('photos.db'):
        print('Creating blank database..')
        db.create_all()


@view_function_timer()
def create_thumbnail(file):
    exif = exifread.process_file(file)
    if 'JPEGThumbnail' in exif:
        thumbnail = exif['JPEGThumbnail']

    elif 'TIFFThumbnail' in exif:
        thumbnail = exif['TIFFThumbnail']

    else:
        image = Image.open(file)
        long_side = image.size.index(max(image.size))
        size = [0, 0]
        size[long_side] = 160
        size[abs(1 - long_side)] = int(image.size[abs(1 - long_side)] * size[long_side] / image.size[long_side])
        thumbnail = image.resize(size)

    return thumbnail


@view_function_timer()
def delete_duplicates():
    paths = list()
    deleted = 0
    for photo in Photo.query.all():
        if photo.path in paths:
            db.session.delete(photo)
            deleted += 1
        else:
            paths.append(photo.path)
    else:
        if deleted > 0:
            try:
                db.session.commit()
            except:
                print('Error occurred during cleaning')


@view_function_timer()
def index_database():
    global LAST_DATABASE_INDEX

    for photo in Photo.query.all():
        # print('looking at', photo.path)
        # print('exists' if os.path.exists(photo.path) else 'not exists')
        if not os.path.exists(photo.path) or get_photo(
                os.path.join(photo.path.split('\\')[-2], photo.path.split('\\')[-1]).replace('\\', '/')) == 'False':
            # print('is not exists')
            Photo.query.filter(Photo.path == photo.path).delete()
        db.session.commit()
    else:
        LAST_DATABASE_INDEX = datetime.now()


class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    date_day = db.Column(db.Integer, nullable=False)
    date_month = db.Column(db.Integer, nullable=False)
    date_year = db.Column(db.Integer, nullable=False)
    filename = db.Column(db.String(100), nullable=False)
    path = db.Column(db.String(200), nullable=False)
    thumbnail_path = db.Column(db.String(200), nullable=True)
    description = db.Column(db.String(50), nullable=True)
    artist = db.Column(db.String(100), nullable=True)
    vendor = db.Column(db.String(70), nullable=True)
    camera_model = db.Column(db.String(70), nullable=True)
    hires = db.Column(db.Boolean, nullable=False)

    # tags = db.Column(db.String, nullable=True)

    def __repr__(self):
        return '<Photo %r>' % self.id


# @view_function_timer()
def photo_in_database(path):
    """
    Takes os PathLike strings with r'\' separators

    :param path:
    :return:
    """
    # print('photoInDatabase')
    if Photo.query.filter(Photo.path == path).all() or Photo.query.filter(
            Photo.filename == os.path.split(path)[-1]).all():
        return True
    else:
        return False


@view_function_timer()
def index_upload_folder():
    global LAST_FOLDER_INDEX

    print('Indexing Upload Folder..')
    ul_folder = app.config['UPLOAD_FOLDER'].replace('/', '\\')
    if os.path.exists(ul_folder):
        for directory in os.listdir(ul_folder):
            if os.path.isfile(os.path.join(ul_folder, directory)):
                path = os.path.join(ul_folder, directory)
                with open(path, 'rb') as stream:
                    file = FileStorage(stream=stream.raw, filename=filename)
                    res = add_photo_to_database(file, path)
                    # print(f'added {path}' if res else False)
                continue

            else:
                for filename in os.listdir(os.path.join(ul_folder, directory)):
                    path = os.path.join(ul_folder, directory, filename)
                    if os.path.isfile(path):
                        if not photo_in_database(path) and path.split('\\')[-1].split('.')[-1] in ['jpg', 'jpeg', 'png',
                                                                                                   'tiff', 'svg']:
                            # print('opening', path)
                            with open(path, 'rb') as stream:
                                file = FileStorage(stream=stream.raw, filename=filename)
                                res = add_photo_to_database(file, path)
                                # print(f'added {path}' if res else False)

    else:
        os.makedirs(ul_folder)
    LAST_FOLDER_INDEX = datetime.now()


@view_function_timer()
def setup():
    global LAST_DATABASE_INDEX

    create_database_if_absent()

    # print('Last folder index:', LAST_FOLDER_INDEX)
    if not LAST_FOLDER_INDEX or (datetime.now() - LAST_FOLDER_INDEX).seconds > upload_folder_index_timeout:
        index_upload_folder()

    # print('Last database index:', LAST_DATABASE_INDEX)
    if not LAST_DATABASE_INDEX or (datetime.now() - LAST_DATABASE_INDEX).seconds > database_index_timeout:
        index_database()

    delete_duplicates()


@view_function_timer()
def get_dates_dict(records):
    dates = dict()
    for record in records:
        date = record.date.strftime('%d %B, %Y')
        try:
            dates[date]

        except KeyError:
            dates[date] = list()

        dates[date].append(record)

    return dates


@app.route('/')
@view_function_timer()
def index():
    setup()

    records = Photo.query.order_by(Photo.date.desc()).all()
    records = get_dates_dict(records)

    server_message = {}
    # if not config['MISC'].getboolean('setup_done'):
    #     server_message['headline'] = 'Привет! Настрой меня ;)'
    #     server_message['paragraph'] = 'Перейди в настройки, чтобы установить папку для индексации и загрузки ' \
    #                                   'фотографий, а также IP и порт сервера '
    #     server_message['href'] = '/options'
    if not config['MISC'].getboolean('setup_done'):
        server_message['headline'] = lang['startup_greeting']
        server_message['paragraph'] = lang['startup_explanation']
        server_message['href'] = '/options'

    return render_template('home.html', locale=locale, lang=lang, dates_dict=records,
                           serverMessage=server_message)


def add_photo_to_database(file, path=None):
    try:
        if file.filename.split('.')[-1].lower() not in ['jpg', 'jpeg', 'png', 'tiff', 'svg']:
            return False

        name = file.filename
        tags = exifread.process_file(file)
        file_date = None
        try:
            file_date = str(tags['EXIF DateTimeOriginal'])
        except KeyError:
            date_search = Datify.find_date(name)
            # print('date_search', date_search)
            if date_search:
                try:
                    file_date = Datify(date_search).date().strftime('%Y:%m:%d %H:%M:%S')
                except TypeError:
                    print('Error while extracting date from filename')
                    pass

        except TypeError:
            pass
    except:
        print('EXCEPTION OCCURRED WHILE ADDING PHOTO')
        return False

    # print(file_date)

    if not file_date:
        file_date = datetime.now().strftime('%Y:%m:%d %H:%M:%S')

    date = datetime.strptime(file_date, '%Y:%m:%d %H:%M:%S')

    if not path or not os.path.isfile(path):
        address_date = date.strftime("%Y%m%d")
        path = os.path.abspath(os.path.join(app.config["UPLOAD_FOLDER"], address_date))

        if not os.path.exists(path):
            os.mkdir(path)

    else:
        path = '\\'.join(path.split('\\')[0:-1])
        # print('path:', path)

    img_path = os.path.join(path, name)
    # print('img path:', img_path)
    if os.path.exists(img_path):
        # print(file.filename, 'exists')
        if Photo.query.filter_by(filename=name).first():
            return True
        # else:
        # print('Adding to db without creating new files')

    else:
        file.seek(0)
        file.save(img_path)

    thumbnail_path = os.path.join(path, 'thumbnails')

    if not os.path.exists(thumbnail_path):
        os.mkdir(thumbnail_path)

    thumbnail = create_thumbnail(file)
    thumbnail_path_full = os.path.join(thumbnail_path, name)

    with open(thumbnail_path_full, 'wb') as thumbnail_file:
        if type(thumbnail) is Image.Image:
            thumbnail.save(thumbnail_file)
        else:
            thumbnail_file.write(thumbnail)

    try:
        vendor = str(tags['Image Make'])
    except KeyError:
        vendor = None

    try:
        camera_model = str(tags['Image Model'])
    except KeyError:
        camera_model = None

    try:
        description = str(tags['Image ImageDescription'])
    except KeyError:
        description = None

    try:
        artist = str(tags['Image Artist'])
    except KeyError:
        artist = None

    with Image.open(file) as img:
        if img.size[0] * img.size[1] > 2000000:
            hires = True
        else:
            hires = False

    record = Photo(
        date=date.date(),
        date_year=date.year,
        date_month=date.month,
        date_day=date.day,
        path=img_path,
        filename=name,
        thumbnail_path=thumbnail_path_full,
        vendor=vendor,
        camera_model=camera_model,
        description=description,
        artist=artist,
        hires=hires
    )

    try:
        db.session.add(record)
        db.session.commit()
        return True

    except:
        return False


@app.route('/new', methods=['POST', 'GET'])
@app.route('/n', methods=['POST', 'GET'])
def upload():
    if request.method == 'POST':
        create_database_if_absent()
        delete_duplicates()

        for file in request.files.getlist('file'):
            if not file.filename.find('.') or \
                    file.filename.split('.')[-1].lower() not in ['jpeg', 'jpg', 'png', 'tiff', 'svg']:
                file.close()
                print('refused file', file.filename)
                continue

            add_photo_to_database(file=file)

        try:
            db.session.commit()
            return redirect('/')
        except:
            db.session.rollback()
            return 'An error occurred during adding new photo'

    else:
        return render_template('upload.html', locale=locale, lang=lang)


@app.route('/get/<path:path>')
def get_photo(path):
    img_path = os.path.join(os.path.abspath(app.config['UPLOAD_FOLDER']), path.replace('/', '\\'))

    if os.path.exists(img_path):
        return send_file(img_path)

    else:
        return 'False'


@app.route('/thumbnail/<path:path>')
def get_thumbnail(path):
    path_parts = path.split('/')
    thumb_path = os.path.join(os.path.abspath(app.config['UPLOAD_FOLDER']), path_parts[0], 'thumbnails', path_parts[1])

    if os.path.exists(thumb_path):
        return send_file(thumb_path.replace(backslash, '/'))

    else:
        return 'False'


@app.route('/search', methods=['POST'])
def search():
    if request.method == 'POST':
        query = request.form['search']
        return redirect(f'/date/{query}')


@app.route('/date/<date>')
def photos_by_date(date: str):
    records = Photo.query
    datified = Datify(date)

    year = datified.year
    month = datified.month
    day = datified.day

    if day:
        records = records.filter(Photo.date_day == day)

    if month:
        records = records.filter(Photo.date_month == month)

    if year:
        records = records.filter(Photo.date_year == year)

    records = records.order_by(Photo.date.desc()).all()
    result = get_dates_dict(records)

    return render_template('imagesfromdate.html', locale=locale, lang=lang, date=date, records=result)


@app.route('/options')
def options():
    return render_template('options/options-main.html', locale=locale,  lang=lang,
                           startup_done=config['MISC'].getboolean('setup_done'))


@app.route('/options/server')
def options_server():
    return render_template('options/options-server.html', locale=locale, lang=lang,
                           server_address=config['SERVER'].get('host'),
                           server_port=config['SERVER'].getint('port'),
                           server_debug=config['SERVER'].getboolean('debug'))


@app.route('/options/photos')
def options_photos():
    return render_template('options/options-photos.html', locale=locale, lang=lang,
                           photos_folder=os.path.abspath(config['PHOTO'].get('upload_folder').replace('/', '\\')),
                           index_database_timeout=database_index_timeout,
                           index_upload_folder_timeout=upload_folder_index_timeout
                           )


@app.route('/options/other')
def options_other():
    return render_template('options/options-other.html', locale=locale, lang=lang,  locales=locales,
                           startup_done=config['MISC'].getboolean('setup_done'))


@app.route('/options/set', methods=['POST'])
def set_option():
    global database_index_timeout
    global upload_folder_index_timeout
    global lang
    global locale
    global APP_CRASH

    if request.method == 'POST':
        ip = request.form.get('ip')
        port = request.form.get('port')
        debug = request.form.get('debug')
        photos_folder = request.form.get('photos_folder')
        language = request.form.get('language')
        setup_done = request.form.get('setup_done')
        upload_folder_index_timeout_val = request.form.get('index_upload_folder_timeout')
        database_index_timeout_val = request.form.get('index_database_timeout')
        index_all = request.form.get('index_all')

        if ip:
            if len([char for char in ip if char == '.']) == 3 and len(ip.split('.')) == 4 and all(
                    [all([bool(part), part.isdigit()]) for part in ip.split('.')]):

                config['SERVER'].update({
                    'host': ip
                })
                save_config()
                return lang['server_answer_reload_to_continue']
            else:
                return f'{lang["server_answer_oops_it_seems_not"]} {lang["options_server_host_headline"].lower()}'

        elif port:
            if port.isdigit():
                config['SERVER'].update({
                    'port': port
                })
                save_config()

                return lang['server_answer_reload_to_continue']

            else:
                return f'{lang["server_answer_oops_it_seems_not"]} {lang["options_server_port_headline"].lower()}'

        elif debug:
            config['SERVER'].update({
                'debug': 'yes' if not config['SERVER'].getboolean('debug') else 'no'
            })
            save_config()

            return ''

        elif photos_folder:
            path = photos_folder
            if not os.path.exists(path):
                os.makedirs(path)
            elif not os.path.isdir(path):
                return lang['server_answer_not_folder']
            elif path.split(':')[0].lower() != os.path.abspath(app.config['UPLOAD_FOLDER']).split(':')[0].lower():
                return lang['server_answer_folder_drive']

            rel_path = os.path.relpath(path).replace('\\', '/')
            config['PHOTO'].update({
                'upload_folder': rel_path
            })
            save_config()

            return lang['server_answer_reload_to_continue']

        elif setup_done:
            config['MISC'].update({
                'setup_done': 'yes'
            })
            save_config()

            return ''

        elif language:
            fmt_lang = language.strip().lower()
            if fmt_lang in locales:
                config['MISC'].update({
                    'language': fmt_lang
                })
                save_config()
                lang, APP_CRASH = load_locale(fmt_lang)
                locale = fmt_lang

                return '$redirect;/options'

            else:
                return lang['server_answer_incorrect_value']

        elif database_index_timeout_val:
            try:
                timeout = int(database_index_timeout_val)
            except ValueError:
                return lang['server_answer_incorrect_value']

            config['PHOTO'].update({
                'database_index_timeout': str(timeout)
            })
            save_config()
            database_index_timeout = timeout
            return ''

        elif upload_folder_index_timeout_val:
            try:
                timeout = int(upload_folder_index_timeout_val)
            except ValueError:
                return lang['server_answer_incorrect_value']

            config['PHOTO'].update({
                'upload_folder_index_timeout': str(timeout)
            })
            save_config()
            upload_folder_index_timeout = timeout
            return ''

        elif index_all:
            create_database_if_absent()
            index_upload_folder()
            index_database()
            delete_duplicates()
            return ''

        else:
            return ''


if __name__ == '__main__':
    if not APP_CRASH:
        print(f"Server running on {config['SERVER'].get('host')}:{config['SERVER'].getint('port')}")
        app.run(
            host=config['SERVER'].get('host'),
            port=config['SERVER'].getint('port'),
            debug=config['SERVER'].getboolean('debug')
        )
    else:
        print('An error occurred. Stopping..')
        input()
