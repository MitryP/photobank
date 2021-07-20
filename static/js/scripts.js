let thumbnails = Array.from(document.querySelectorAll('.thumbnail'));
let selection;
let photoView = document.querySelector('.photo-view');
let searchButton = document.querySelector('.search-button');
let searchPanel = document.querySelector('.search-panel');
let menuButton = document.querySelector('.menu-button');
let menuPanel = document.querySelector('.menu-panel');
if (thumbnails) {

	for (const thumbnail of thumbnails) {

	    thumbnail.onclick = (event) => {

	        selection = event.target;
	        displaySelection();

	    }

	}
}

function displaySelection() {

    document.querySelector('.window').src = `${selection.dataset['src']}`;
    document.querySelector('.photo-view').classList.remove('hidden');
    hideArrowsIfNeeded()

}

function hideSelection() {

    document.querySelector('.photo-view').classList.add('hidden');

}

// navToggle = true;
function toggleNavButtons() {
    buttons = document.querySelectorAll('.button');

    for (const button of buttons) {

    	if (button.classList.contains('next') && getThumbnailIndex(selection) == thumbnails.length-1) {
    		continue
    	}
    	else {
    		if (button.classList.contains('previous') && getThumbnailIndex(selection) == 0) {
	    		continue
	    	}
	    	else {
	    		button.classList.toggle('hidden')
	    	}
	    }

    }
}
if (document.querySelector('.window')) {   			
	document.querySelector('.window').onclick = (event) => {
	        toggleNavButtons()
	}
}


function getThumbnailIndex(thumbnail) {
    return thumbnails.indexOf(thumbnail)
}

function next() {
    index = getThumbnailIndex(selection)
	if (index != thumbnails.length-1) {
	    selection = thumbnails[index+1]
	    displaySelection()
	}
	hideArrowsIfNeeded()
}

function previous() {
	index = getThumbnailIndex(selection)
	if (index != 0) {
		selection = thumbnails[index-1]
		displaySelection()
	}
	hideArrowsIfNeeded()
}

function hideArrowsIfNeeded() {
	btn_next = document.querySelector('.button.next');
	btn_prev = document.querySelector('.button.previous');
	selection_index = getThumbnailIndex(selection);

	if (selection_index == 0) { //and !btn_prev.classList.contain('hidden')) {
		btn_prev.classList.add('hidden')
	}
	else {
		btn_prev.classList.remove('hidden')

	}

	if (selection_index == thumbnails.length-1) { 
		btn_next.classList.add('hidden')
	}
	else {
		btn_next.classList.remove('hidden')

	}

}

function toggleSearchPanel() {
	searchButton.classList.toggle('active');
	searchPanel.classList.toggle('shown');
	if (searchPanel.classList.contains('shown')) {
        searchPanel.querySelector('input[type="search"]').focus()
	}
	else {
	    searchPanel.querySelector('input[type="search"]').blur()
	};

	menuPanel.classList.remove('shown');
	menuButton.classList.remove('active');

}


function toggleMenu() {
	menuButton.classList.toggle('active');
	menuPanel.classList.toggle('shown');
	searchPanel.classList.remove('shown');
	searchButton.classList.remove('active');
}

function hidePopup() {
	document.querySelector('.popup-container').classList.add('hidden')
	document.querySelector('html').style = '';

}

document.body.onload = () => {

	// if (location.pathname.length > 1) {
		// document.querySelector('.home-link').classList.remove('hidden')
	// }

	if (document.querySelector('.popup')) {

		document.querySelector('body').scrollIntoView({
			behavior: "smooth",
		});

		document.querySelector('html').style = 'overflow-y: hidden';

	}
}

function applyOption(optionName, value) {
	const XHR = new XMLHttpRequest(),
		  FD = new FormData();

	FD.append(optionName, value);
	console.log(FD);

	XHR.addEventListener('load', function (event) {
		if (event.target.responseText.length > 0) {
			alert(event.target.responseText)

		}
	})
	XHR.addEventListener('error', function () {
		alert('Сервер не ответил')
	})

	XHR.open('POST', '/options/set');
	XHR.send(FD);
}

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

function toggleDebug() {
	applyOption('debug', '1')
}

function setPhotosFolder() {
	path = prompt('Введите новый абсолютный путь к папке с фотографиями на сервере:', document.querySelectorAll('span.important')[0].innerHTML)
	if (path) {
		applyOption('photos_folder', path)

	}
}

function setupDone() {
	applyOption('setup_done', '1')
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

function indexDatabaseAndUploadFolder() {
	applyOption('index_all', '1')
}

let fileInput = document.querySelector('#file');
let label = fileInput.nextElementSibling;
let labelText = label.innerText;

fileInput.addEventListener('change', function (e) {
    let countFiles = '';
    if (this.files && this.files.length >= 1)
      countFiles = this.files.length;

    if (countFiles)
		label.innerText = `Файлов: ${countFiles}`;
    else
		label.innerText = labelText;
});
