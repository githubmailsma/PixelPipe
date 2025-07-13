/**
 * PixelPipe Image Browser Module
 * Handles image gallery, uploads, and navigation
 */

class ImageBrowser {
    constructor() {
        this.container = null;
        this.imageContainer = null;
        this.initialize();
    }

    /**
     * Initialize the image browser
     */
    initialize() {
        this.container = document.createElement('div');
        this.container.style.display = 'flex';
        
        this.imageContainer = document.createElement('div');
        this.imageContainer.className = 'image-browser';
        
        this.loadImages();
        this.container.appendChild(this.imageContainer);
    }

    /**
     * Load images from both built-in and uploaded sources
     */
    async loadImages() {
        try {
            await Promise.all([
                this.loadBuiltInImages(),
                this.loadUploadedImages()
            ]);
        } catch (error) {
            console.error('Error loading images:', error);
            this.showError('Failed to load images');
        }
    }

    /**
     * Load built-in images
     */
    async loadBuiltInImages() {
        const response = await fetch('/images');
        const files = await response.json();
        files.forEach(file => this.addImageToContainer(file, 'images'));
    }

    /**
     * Load uploaded images
     */
    async loadUploadedImages() {
        const response = await fetch('/uploads');
        const files = await response.json();
        files.forEach(file => this.addImageToContainer(file, 'uploads'));
    }

    /**
     * Add image thumbnail to container
     * @param {string} filename - Image filename
     * @param {string} source - Source directory ('images' or 'uploads')
     */
    addImageToContainer(filename, source) {
        const thumbnail = this.createThumbnail(filename, source);
        this.imageContainer.appendChild(thumbnail);
    }

    /**
     * Create thumbnail element
     * @param {string} filename - Image filename
     * @param {string} source - Source directory
     * @returns {HTMLElement} Thumbnail element
     */
    createThumbnail(filename, source) {
        const thumbnail = document.createElement('div');
        thumbnail.className = 'thumbnail';
        
        const img = document.createElement('img');
        img.src = `/${source}/${filename}`;
        img.alt = filename;
        img.loading = 'lazy'; // Performance improvement
        
        thumbnail.appendChild(img);
        thumbnail.addEventListener('click', () => this.handleImageClick(filename));
        
        return thumbnail;
    }

    /**
     * Handle image click event
     * @param {string} filename - Clicked image filename
     */
    handleImageClick(filename) {
        const brightness = sessionStorage.getItem('defaultBrightness') || '1.0';
        const resolution = sessionStorage.getItem('defaultResolution') || '160';
        const effect = sessionStorage.getItem('defaultEffect') || '-1';
        
        const url = new URL(`/convert/${filename}`, window.location.origin);
        url.searchParams.set('brightness', brightness);
        url.searchParams.set('resolution', resolution);
        url.searchParams.set('effect', effect);
        
        window.location.href = url.toString();
    }

    /**
     * Show error message
     * @param {string} message - Error message
     */
    showError(message) {
        // Implement error display logic
        console.error(message);
    }

    /**
     * Get the browser container element
     * @returns {HTMLElement} Container element
     */
    getContainer() {
        return this.container;
    }
}

/**
 * Create and return image browser instance
 * @returns {HTMLElement} Image browser container
 */
function createImageBrowser() {
    const browser = new ImageBrowser();
    
    // Make addUploadToContainer available globally for upload handlers
    window.addUploadToContainer = (filename) => {
        browser.addImageToContainer(filename, 'uploads');
    };
    
    return browser.getContainer();
}

function openUploadModal() {
    const modal = document.createElement('div');
    modal.className = 'upload-modal';
    modal.innerHTML = `
        <div class="upload-content">
            <h2>Upload Images</h2>
            <div class="upload-methods">
                <div class="upload-method" onclick="handleFileUpload()">
                    <h3>📁 Upload from Computer</h3>
                    <p>Select images from your device to upload</p>
                    <input type="file" id="file-upload" accept="image/*" multiple style="display: none;">
                </div>
                <div class="upload-method" onclick="handleUrlUpload()">
                    <h3>🔗 Add from URL</h3>
                    <p>Paste an image URL to add it to your collection</p>
                </div>
                <div class="upload-method" onclick="handleDragDrop()">
                    <h3>📥 Drag and Drop</h3>
                    <p>Drag images directly into this window</p>
                </div>
            </div>
            <div class="upload-controls">
                <button onclick="closeUploadModal(this)">Close</button>
            </div>
        </div>
    `;
    document.body.appendChild(modal);

    // Add ESC key handler
    const handleEsc = (e) => {
        if (e.key === 'Escape') {
            closeUploadModal(modal);
            document.removeEventListener('keydown', handleEsc);
        }
    };
    document.addEventListener('keydown', handleEsc);
}

function showUploadSuccess(filename, fileUrl) {
    const modal = document.createElement('div');
    modal.className = 'upload-success-modal';
    modal.innerHTML = `
        <div class="success-content">
            <h3>✅ Upload Successful!</h3>
            <div class="preview-container">
                <img src="${fileUrl}" alt="${filename}" class="upload-preview">
            </div>
            <button onclick="this.closest('.upload-success-modal').remove()">Close</button>
        </div>
    `;
    document.body.appendChild(modal);
}

function handleFileUpload(files) {
    const status = document.createElement('div');
    status.style.marginTop = '10px';
    status.style.color = '#fff';
    document.body.appendChild(status);
    
    for(const file of files) {
        const formData = new FormData();
        formData.append('image', file);
        status.textContent = `Uploading ${file.name}...`;
        
        fetch('/upload_image', { method: 'POST', body: formData })
            .then(resp => resp.json())
            .then(data => {
                if (data.success) {
                    status.textContent = `Upload successful: ${file.name}`;
                    window.addUploadToContainer(data.filename);
                    showUploadSuccess(data.filename, data.url);
                } else {
                    status.textContent = data.error || "Upload failed.";
                }
            })
            .catch(err => {
                status.textContent = "Upload error.";
            });
    }
}

function handleUrlUpload() {
    const urlPrompt = document.createElement('div');
    urlPrompt.innerHTML = `
        <input type="text" placeholder="Paste image URL here" style="width: 100%; padding: 8px; margin: 10px 0;">
        <button onclick="submitUrl(this)">Add Image</button>
    `;
    document.querySelector('.upload-methods').appendChild(urlPrompt);
}

async function submitUrl(btn) {
    const url = btn.previousElementSibling.value.trim();
    if (!url) return;
    
    const status = document.createElement('div');
    status.style.marginTop = '10px';
    status.style.color = '#fff';
    btn.parentElement.appendChild(status);
    
    status.textContent = "Adding...";
    try {
        const resp = await fetch('/add_image_url', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url })
        });
        const data = await resp.json();
        if (data.success) {
            status.textContent = "Image added!";
            window.addUploadToContainer(data.filename);
            showUploadSuccess(data.filename, data.url);
        } else {
            status.textContent = data.error || "Add failed.";
        }
    } catch (err) {
        status.textContent = "Add error.";
    }
}

function handleDragDrop() {
    const dropZone = document.createElement('div');
    dropZone.style.border = '2px dashed #666';
    dropZone.style.borderRadius = '8px';
    dropZone.style.padding = '20px';
    dropZone.style.textAlign = 'center';
    dropZone.style.marginTop = '10px';
    dropZone.innerHTML = 'Drop your images here';
    
    dropZone.ondragover = e => {
        e.preventDefault();
        dropZone.style.borderColor = '#fff';
    };
    
    dropZone.ondragleave = e => {
        e.preventDefault();
        dropZone.style.borderColor = '#666';
    };
    
    dropZone.ondrop = async e => {
        e.preventDefault();
        dropZone.style.borderColor = '#666';
        
        const files = Array.from(e.dataTransfer.files).filter(f => f.type.startsWith('image/'));
        for(const file of files) {
            const formData = new FormData();
            formData.append('image', file);
            
            try {
                const resp = await fetch('/upload_image', { method: 'POST', body: formData });
                const data = await resp.json();
                if (data.success) {
                    window.addUploadToContainer(data.filename);
                }
            } catch (err) {
                console.error('Upload error:', err);
            }
        }
    };
    
    document.querySelector('.upload-methods').appendChild(dropZone);
}

function closeUploadModal(btn) {
    btn.closest('.upload-modal').remove();
}

function openSettings() {
    const modal = document.createElement('div');
    modal.className = 'settings-modal';
    modal.innerHTML = `
        <div class="settings-content">
            <h2>Default Settings</h2>
            <div class="setting-item">
                <label>Default Brightness: <input type="range" id="default-brightness" min="0.5" max="3" step="0.1" value="${sessionStorage.getItem('defaultBrightness') || '1.0'}">
                <span>${sessionStorage.getItem('defaultBrightness') || '1.0'}</span></label>
            </div>
            <div class="setting-item">
                <label>Default Font Size: <input type="range" id="default-fontsize" min="1" max="24" step="1" value="${sessionStorage.getItem('defaultFontSize') || '8'}">
                <span>${sessionStorage.getItem('defaultFontSize') || '8'}</span></label>
            </div>
            <div class="setting-item">
                <label>Default Resolution: <input type="range" id="default-resolution" min="20" max="800" step="1" value="${sessionStorage.getItem('defaultResolution') || '160'}">
                <span>${sessionStorage.getItem('defaultResolution') || '160'}</span></label>
            </div>
            <div class="setting-item">
                <label>Default Effect: 
                    <select id="default-effect">
                        <option value="-1" ${(sessionStorage.getItem('defaultEffect') || '-1') === '-1' ? 'selected' : ''}>None</option>
                        <option value="0" ${sessionStorage.getItem('defaultEffect') === '0' ? 'selected' : ''}>Rainbow</option>
                        <option value="1" ${sessionStorage.getItem('defaultEffect') === '1' ? 'selected' : ''}>Glitch</option>
                        <option value="2" ${sessionStorage.getItem('defaultEffect') === '2' ? 'selected' : ''}>Matrix</option>
                        <option value="3" ${sessionStorage.getItem('defaultEffect') === '3' ? 'selected' : ''}>Fire</option>
                        <option value="4" ${sessionStorage.getItem('defaultEffect') === '4' ? 'selected' : ''}>Neon</option>
                    </select>
                </label>
            </div>
            <div class="setting-item">
                <label>
                    <input type="checkbox" id="show-quickstart" ${localStorage.getItem('hideQuickStart') !== 'true' ? 'checked' : ''}>
                    Show Quick Start Guide
                </label>
            </div>
            <button onclick="saveSettings(this)">Save</button>
            <button onclick="closeSettings(this)">Cancel</button>
        </div>
    `;
    document.body.appendChild(modal);

    // Add ESC key handler
    const handleEsc = (e) => {
        if (e.key === 'Escape') {
            closeSettings(modal);
            document.removeEventListener('keydown', handleEsc);
        }
    };
    document.addEventListener('keydown', handleEsc);

    // Add input listeners to update displayed values
    ['brightness', 'fontsize', 'resolution'].forEach(setting => {
        const input = document.getElementById(`default-${setting}`);
        input.addEventListener('input', e => {
            input.nextElementSibling.textContent = e.target.value;
        });
    });
}

function saveSettings(btn) {
    sessionStorage.setItem('defaultBrightness', document.getElementById('default-brightness').value);
    sessionStorage.setItem('defaultFontSize', document.getElementById('default-fontsize').value);
    sessionStorage.setItem('defaultResolution', document.getElementById('default-resolution').value);
    sessionStorage.setItem('defaultEffect', document.getElementById('default-effect').value);
    
    const showQuickStart = document.getElementById('show-quickstart').checked;
    localStorage.setItem('hideQuickStart', (!showQuickStart).toString());
    
    const quickStart = document.getElementById('quickStart');
    if (quickStart) {
        quickStart.style.display = showQuickStart ? 'block' : 'none';
    }
    
    closeSettings(btn);
}

function closeSettings(btn) {
    btn.closest('.settings-modal').remove();
}

function openHelp() {
    const modal = document.createElement('div');
    modal.className = 'help-modal';
    modal.innerHTML = `
        <div class="help-content">
            <h2>Welcome to PixelPipe!</h2>
            <div class="help-section">
                <h3>🎨 How to Use</h3>
                <ul>
                    <li>Click on any image to convert it to ANSI art</li>
                    <li>Use the settings (⚙️) to set default brightness and resolution</li>
                    <li>Upload your own images using the upload button (📤)</li>
                </ul>
                
                <h3>🔧 Features</h3>
                <ul>
                    <li>Image to ANSI Conversion</li>
                    <li>Multiple upload methods</li>
                    <li>Adjustable brightness and resolution</li>
                    <li>Animation effects</li>
                    <li>Font size control</li>
                </ul>
                
                <h3>💡 Tips</h3>
                <ul>
                    <li>Higher resolution means more detailed ANSI art (but will impact performance)</li>
                    <li>Larger font sizes combined with high resolution may slow down rendering</li>
                    <li>Adjust brightness for better character contrast</li>
                    <li>Try different animation effects for fun results</li>
                </ul>
            </div>
            <button onclick="closeHelp(this)">Got it!</button>
        </div>
    `;
    document.body.appendChild(modal);

    // Add ESC key handler
    const handleEsc = (e) => {
        if (e.key === 'Escape') {
            closeHelp(modal);
            document.removeEventListener('keydown', handleEsc);
        }
    };
    document.addEventListener('keydown', handleEsc);
}

function closeHelp(btn) {
    btn.closest('.help-modal').remove();
}

function hideQuickStart() {
    const quickStart = document.getElementById('quickStart');
    quickStart.style.display = 'none';
    localStorage.setItem('hideQuickStart', 'true');
}

// Modify the file upload handling
function handleDropArea() {
    const uploadZone = document.getElementById('uploadZone');
    const dropArea = document.getElementById('drop-area');
    const urlInput = uploadZone.querySelector('.url-input input');
    const urlButton = uploadZone.querySelector('.url-input button');
    
    // Add URL button handler
    urlButton.addEventListener('click', async () => {
        const url = urlInput.value.trim();
        if (!url) return;
        
        urlButton.disabled = true;
        urlButton.textContent = 'Adding...';
        
        try {
            const resp = await fetch('/add_image_url', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url })
            });
            const data = await resp.json();
            if (data.success) {
                window.addUploadToContainer(data.filename);
                showUploadSuccess(data.filename, data.url);
                urlInput.value = ''; // Clear input after success
            } else {
                alert(data.error || 'Failed to add image');
            }
        } catch (err) {
            alert('Error adding image');
        } finally {
            urlButton.disabled = false;
            urlButton.textContent = 'Add URL';
        }
    });

    dropArea.addEventListener('click', () => {
        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.accept = 'image/*';
        fileInput.multiple = true;
        fileInput.click();
        
        fileInput.onchange = (e) => handleFileUpload(e.target.files);
    });
    
    dropArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropArea.style.borderColor = '#fff';
    });
    
    dropArea.addEventListener('dragleave', (e) => {
        e.preventDefault();
        uploadZone.style.borderColor = '#4CAF50';
    });
    
    dropArea.addEventListener('drop', (e) => {
        e.preventDefault();
        dropArea.style.borderColor = '#4CAF50';
        handleFileUpload(e.dataTransfer.files);
    });
}

// Initialize the drop area functionality
document.addEventListener('DOMContentLoaded', handleDropArea);
