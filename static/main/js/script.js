let popup = document.getElementById("popup");
let currentTab = 0;
let currentTikTokUrl = "";
let currentFiles = [];
let galleryData = {};
let popupHeight = 0;

// Parse gallery data from HTML data attributes on page load
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll(".gallery-item").forEach((item) => {
        const itemId = item.getAttribute("data-item-id");
        
        let filesData = [];
        const filesAttr = item.getAttribute("data-files");
        if (filesAttr) {
            try {
                filesData = JSON.parse(filesAttr);
            } catch (e) {
                console.error("Error parsing files data:", e);
            }
        }
        
        galleryData[itemId] = {
            id: itemId,
            title: item.querySelector(".item-title").textContent,
            description: item.getAttribute("data-description"),
            image: item.querySelector("img").src,
            tiktok_url: item.getAttribute("data-tiktok-url"),
            files: filesData
        };
    });
});

document.addEventListener("click", function(event) {
    if (popup.classList.contains("open-popup") && !popup.contains(event.target) && !event.target.closest(".gallery-item")) {
        closePopup();
    }
});

// Add click handlers to all gallery items
document.querySelectorAll(".gallery-item").forEach((item) => {
    item.addEventListener("click", function() {
        const img = this.querySelector("img");
        const title = this.querySelector(".item-title");
        const tiktokUrl = this.getAttribute("data-tiktok-url");
        const description = this.getAttribute("data-description");
        const filesAttr = this.getAttribute("data-files");
        
        let files = [];
        if (filesAttr) {
            try {
                files = JSON.parse(filesAttr);
            } catch (e) {
                console.error("Error parsing files:", e);
            }
        }
        
        openPopup(img.src, title.textContent, tiktokUrl, description, files);
    });
});

function openPopup(imageUrl, title, tiktokUrl, description, files) {
    document.getElementById("popupTitle").textContent = title;
    document.getElementById("popupImage").src = imageUrl;
    document.getElementById("popupDescription").textContent = description;
    currentTikTokUrl = tiktokUrl;
    currentFiles = files || [];
    currentTab = 0;
    popup.classList.add("open-popup");
    
    populateFiles();
    
    switchTab(0);
    
    // After switching to tab 0, measure and set the height
    setTimeout(() => {
        popupHeight = popup.offsetHeight;
        popup.style.height = popupHeight + 'px';
    }, 0);
}

function populateFiles() {
    const filesContainer = document.querySelector('.popup-tab[data-tab="1"]');
    const filesList = filesContainer.querySelector('.files-list') || document.createElement('div');
    filesList.className = 'files-list';
    filesList.innerHTML = '';
    
    if (currentFiles.length === 0) {
        filesList.innerHTML = '<p>Geen bestanden beschikbaar</p>';
    } else {
        currentFiles.forEach(file => {
            const fileLink = document.createElement('a');
            fileLink.href = file.url;
            fileLink.textContent = file.url.split('/').pop();
            fileLink.target = '_blank';
            fileLink.className = 'file-link';
            
            const fileItem = document.createElement('div');
            fileItem.className = 'file-item';
            fileItem.appendChild(fileLink);
            
            filesList.appendChild(fileItem);
        });
    }
    
    filesContainer.innerHTML = '';
    filesContainer.appendChild(filesList);
}

function closePopup() {
    popup.classList.remove("open-popup");
    popup.style.height = 'fit-content';
    popupHeight = 0;
}

function switchTab(tabIndex) {
    currentTab = tabIndex;
    
    document.querySelectorAll(".popup-tab").forEach(tab => {
        tab.style.display = "none";
    });
    
    const selectedTab = document.querySelector(`.popup-tab[data-tab="${tabIndex}"]`);
    selectedTab.style.display = "flex";
    selectedTab.style.flexDirection = "column";
    
    // Keep the popup at the fixed height
    if (popupHeight > 0) {
        popup.style.height = popupHeight + 'px';
    }
    
    document.querySelectorAll(".tab-btn").forEach((btn, index) => {
        if (index === tabIndex) {
            btn.classList.add("active");
            btn.style.backgroundColor = "#f0f0f0";
        } else {
            btn.classList.remove("active");
            btn.style.backgroundColor = "white";
        }
    });
    
    if (tabIndex === 0) {
        const popupImage = document.getElementById("popupImage");
        popupImage.style.cursor = "pointer";
        popupImage.onclick = () => {
            window.open(currentTikTokUrl, "_blank");
        };
    }
}

function updateHighlighted(itemId) {
    const item = galleryData[itemId];
    if (item) {
        document.querySelector('.highlighted-title').textContent = item.title;
        document.querySelector('.highlighted-description').textContent = item.description;
        document.querySelector('.highlighted-img').src = item.image;
        document.querySelector('.highlighted-img').alt = item.title;
        
        document.querySelectorAll('.gallery-item').forEach(el => {
            el.classList.remove('active');
        });
        document.querySelector(`[data-item-id="${itemId}"]`).classList.add('active');
    }
}

let currentFilter = 'all';

document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        currentFilter = this.getAttribute('data-filter');
        
        document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        this.classList.add('active');
        
        document.querySelectorAll('.gallery-item').forEach(item => {
            const genre = item.getAttribute('data-genre');
            if (currentFilter === 'all' || genre === currentFilter) {
                item.style.display = 'flex';
            } else {
                item.style.display = 'none';
            }
        });
    });
});