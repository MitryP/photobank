function setIP() {
	ip = prompt('Type in new ip', document.querySelectorAll('span.important')[0].innerHTML);
	if (ip) {
		applyOption('ip', ip);

	}
}

function setPort() {
	port = prompt('Type in new port', document.querySelectorAll('span.important')[1].innerHTML)
	if (port) {
		applyOption('port', port)
	}
}

function setPhotosFolder() {
	path = prompt('Type in new absolute path to the photos folder on the server', document.querySelectorAll('span.important')[0].innerHTML)
	if (path) {
		applyOption('photos_folder', path)

	}
}

function setLanguage() {
    lang = prompt('Select preferable localization among given', document.querySelectorAll('span.important')[0].innerHTML)
    if (lang) {
        applyOption('language', lang)
    }
}

function setDatabaseIndexTimeout() {
	timeout = prompt('Type in new timeout (in seconds)');
	if (timeout) {
		applyOption('index_database_timeout', timeout)
	}
}

function setUploadFolderIndexTimeout() {
	timeout = prompt('Type in new timeout (in seconds)');
	if (timeout) {
		applyOption('index_upload_folder_timeout', timeout)
	}
}
