function initializeViewer() {
    // Use session storage values or defaults
    document.getElementById('brightness').value = sessionStorage.getItem('defaultBrightness') || '1.0';
    document.getElementById('fontsize').value = sessionStorage.getItem('defaultFontSize') || '8';
    document.getElementById('resolution').value = sessionStorage.getItem('defaultResolution') || '160';
    
    // Update displayed values
    document.getElementById('brightness-value').textContent = document.getElementById('brightness').value;
    document.getElementById('fontsize-value').textContent = document.getElementById('fontsize').value;
    document.getElementById('resolution-value').textContent = document.getElementById('resolution').value;
    
    // Set initial font size
    document.getElementById('ansi-art-container').style.fontSize = 
        document.getElementById('fontsize').value + 'px';
    
    // Set default effect from session storage or -1 (None)
    const defaultEffect = sessionStorage.getItem('defaultEffect') || '-1';
    currentEffect = parseInt(defaultEffect);
    
    // Update the selected effect button
    document.querySelectorAll('.effect-buttons span').forEach(btn => {
        btn.classList.remove('selected');
        if (parseInt(btn.getAttribute('data-effect')) === currentEffect) {
            btn.classList.add('selected');
        }
    });
    
    // Render initial art
    document.getElementById('ansi-art').innerHTML = ansi_up.ansi_to_html(originalArt);
    
    // Setup event listeners
    setupEventListeners();
}

function setupEventListeners() {
    document.getElementById('brightness').addEventListener('change', function(e) {
        document.getElementById('brightness-value').textContent = e.target.value;
        updateArt();
    });

    document.getElementById('fontsize').addEventListener('input', function(e) {
        let size = e.target.value + 'px';
        document.getElementById('fontsize-value').textContent = e.target.value;
        document.getElementById('ansi-art-container').style.fontSize = size;
    });

    document.getElementById('resolution').addEventListener('input', function(e) {
        document.getElementById('resolution-value').textContent = e.target.value;
        updateArt();
    });

    document.querySelectorAll('.effect-buttons span').forEach(btn => {
        btn.addEventListener('click', async function() {
            document.querySelectorAll('.effect-buttons span').forEach(b => b.classList.remove('selected'));
            this.classList.add('selected');
            currentEffect = parseInt(this.getAttribute('data-effect'));
            await updateArt();
        });
    });
}

async function updateArt() {
    const brightness = document.getElementById('brightness').value;
    const resolution = document.getElementById('resolution').value;
    const fetchUrl = `/update_ansi?image=${encodeURIComponent(imagePath)}&brightness=${brightness}&effect=${currentEffect}&resolution=${resolution}`;
    
    try {
        const response = await fetch(fetchUrl);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const newArt = await response.text();
        if (!newArt.trim()) {
            throw new Error('Empty response from server');
        }
        
        originalArt = newArt;
        document.getElementById('ansi-art').innerHTML = ansi_up.ansi_to_html(newArt);
    } catch (error) {
        console.error('Error updating art:', error);
        showToast(`<strong>Error:</strong> Failed to update ANSI art. ${error.message}`);
    }
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = message;
    document.body.appendChild(toast);
    
    // Trigger show animation
    setTimeout(() => toast.classList.add('show'), 100);
    
    // Auto hide after 4 seconds
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            if (document.body.contains(toast)) {
                document.body.removeChild(toast);
            }
        }, 300);
    }, 4000);
}

function downloadAnsi() {
    // Create blob with ANSI content
    const blob = new Blob([originalArt], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    
    // Create download link
    const a = document.createElement('a');
    a.href = url;
    a.download = `${filename}.ans`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);

    // Show toast notification
    showToast('<strong>ANSI file downloaded!</strong><br><strong>View in terminal:</strong><br>Windows PowerShell: <code>Get-Content filename.ans | Write-Host</code><br>Windows CMD: <code>chcp 65001 & type filename.ans</code><br>Linux/Mac: <code>cat filename.ans</code>');
}