let thumbnails = Array.from(document.querySelectorAll('.thumbnail'));
let selection;
let navButtons = true;
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

function handleArrows(e) {
    switch (e.key) {
        case 'ArrowLeft': {
            e.preventDefault()
            e.stopImmediatePropagation()
            // e.initEvent('keyup')
            previous()
            // setTimeout('', 1000)

            break
        }
        case 'ArrowRight': {
            e.preventDefault()
            e.stopImmediatePropagation()
            // e.initEvent('keyup')
            next()
            setTimeout('', 1000)
            break
        }
        case 'Escape': {
            e.preventDefault()
            e.stopImmediatePropagation()
            hideSelection()
            break
        }
    }
}

function handleScrollZoom(e) {
    zoom = Number(document.querySelector('.window').style.transform.replace('scale(', '').replace(')', ''))
    pointer = document.querySelector('.pointer')
    if (!zoom) {
        zoom = 1
        pointer.innerHTML = '1x'
        pointer.classList.add('hidden')
    }

    if (e.deltaY < 0 && zoom < 3.91) {
        document.querySelector('.window').style.transform = `scale(${zoom + 0.1}`
    } else if (e.deltaY > 0 && zoom > 1) {
        document.querySelector('.window').style.transform = `scale(${zoom - 0.1}`
    }

    pointer.innerHTML = `${zoom}x`
    if (zoom > 1) {
        pointer.classList.remove('hidden')
    }
    else {
        pointer.classList.add('hidden')
    }
}


function displaySelection() {
    document.querySelector('.window').src = `${selection.dataset['src']}`;
    document.querySelector('.photo-view').classList.remove('hidden');
    if (!navButtons) {
        toggleNavButtons()
    }
    hideArrowsIfNeeded()
    // document.querySelector('.window').focus()
    document.addEventListener('keydown', handleArrows)

    document.querySelector('.window').addEventListener('wheel', handleScrollZoom)


}

function hideSelection() {

    document.querySelector('.photo-view').classList.add('hidden');
    document.removeEventListener('keydown', handleArrows)
    document.querySelector('.window').style.transform = ''
    document.querySelector('.pointer').classList.add('hidden')

}

// navToggle = true;
function toggleNavButtons() {
    navButtons = !navButtons;
    buttons = document.querySelectorAll('.button');

    for (const button of buttons) {

        if (button.classList.contains('next') && getThumbnailIndex(selection) == thumbnails.length - 1) {
            continue
        } else {
            if (button.classList.contains('previous') && getThumbnailIndex(selection) == 0) {
                continue
            } else {
                button.classList.toggle('hidden')
            }
        }

    }
    pointer = document.querySelector('.pointer')
    if (pointer.classList.contains('invisible')) {
        pointer.classList.remove('invisible')
    }
    else {
        pointer.classList.add('invisible')
    }
}

if (document.querySelector('.window')) {
    document.querySelector('.window').onclick = () => {
        toggleNavButtons()
    }

}


function getThumbnailIndex(thumbnail) {
    return thumbnails.indexOf(thumbnail)
}

function next() {
    index = getThumbnailIndex(selection)
    console.log(index)
    if (index != thumbnails.length - 1) {
        selection = thumbnails[index + 1]
        displaySelection()
    }
    hideArrowsIfNeeded()
}

function previous() {
    index = getThumbnailIndex(selection)
    console.log(index)
    if (index != 0) {
        selection = thumbnails[index - 1]
        displaySelection()
    }
    hideArrowsIfNeeded()
}

function hideArrowsIfNeeded() {
    btn_next = document.querySelector('.button.next');
    btn_prev = document.querySelector('.button.previous');
    selection_index = getThumbnailIndex(selection);

    if (selection_index === 0) { //and !btn_prev.classList.contain('hidden')) {
        btn_prev.classList.add('hidden')
    } else {
        if (navButtons) {
            btn_prev.classList.remove('hidden')
        }

    }

    if (selection_index == thumbnails.length - 1) {
        btn_next.classList.add('hidden')
    } else {
        if (navButtons) {
            btn_next.classList.remove('hidden')
        }
    }

}

function toggleSearchPanel() {
    searchButton.classList.toggle('active');
    searchPanel.classList.toggle('shown');
    if (searchPanel.classList.contains('shown')) {
        searchPanel.querySelector('input[type="search"]').focus()
    } else {
        searchPanel.querySelector('input[type="search"]').blur()
    }

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
//	    event.preventDefault()
        if (event.target.responseText == '$reload') {
            document.location.reload()
        } else {
            if (~event.target.responseText.indexOf('$redirect;')) {
                loc = event.target.responseText.split(';')[1]
//                location.href = loc
            } else {
                if (event.target.responseText.length > 0) {
                    alert(event.target.responseText)
                }
            }
        }
    })
    XHR.addEventListener('error', function () {
        alert('An error occurred')
    })

    XHR.open('POST', '/options/set');
    XHR.send(FD);
}

function toggleDebug() {
    applyOption('debug', '1')
}

function setupDone() {
    applyOption('setup_done', '1')
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
