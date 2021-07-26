function setIP() {
	ip = prompt('Введите новый ip', document.querySelectorAll('span.important')[0].innerHTML);
	if (ip) {
		applyOption('ip', ip);

	}
}

function setPort() {
	port = prompt('Введите новый порт', document.querySelectorAll('span.important')[1].innerHTML)
	if (port) {
		applyOption('port', port)
	}
}

function setPhotosFolder() {
	path = prompt('Введите новый абсолютный путь к папке с фотографиями на сервере:', document.querySelectorAll('span.important')[0].innerHTML)
	if (path) {
		applyOption('photos_folder', path)

	}
}

function setLanguage() {
    lang = prompt('Укажите необходимую локализацию из указанных:', document.querySelectorAll('span.important')[0].innerHTML)
    if (lang) {
        applyOption('language', lang)
    }
}

function setDatabaseIndexTimeout() {
	timeout = prompt('Введите новую задержку (в секундах):');
	if (timeout) {
		applyOption('index_database_timeout', timeout)
	}
}

function setUploadFolderIndexTimeout() {
	timeout = prompt('Введите новую задержку (в секундах):');
	if (timeout) {
		applyOption('index_upload_folder_timeout', timeout)
	}
}
