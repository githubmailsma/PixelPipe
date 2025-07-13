from PIL import Image
import os
import random
from utils.template_renderer import render_template

def rgb_to_ansi(r, g, b):
    # Calculate brightness (0-255)
    brightness = (r + g + b) // 3
    
    # Select character based on brightness with adjusted thresholds
    if brightness < 32:      # Very dark
        char = ' '
    elif brightness < 96:    # Dark
        char = '░'
    elif brightness < 160:   # Medium
        char = '▒'
    elif brightness < 224:   # Light
        char = '▓'
    else:                    # Very light
        char = '█'
    
    return f"\x1b[38;2;{r};{g};{b}m{char}"

def image_to_ansi(image_path, max_width=160, brightness=1.0, font_size=8):
    img = Image.open(image_path)
    
    # Calculate new width and height based on max_width (resolution)
    width, height = img.size
    aspect_ratio = height / width
    new_width = min(width, max_width)
    new_height = int(aspect_ratio * new_width * 0.55)  # 0.55 compensates for font aspect ratio

    img = img.resize((new_width, new_height))
    pixels = img.convert('RGB')
    
    ansi_art = []
    for y in range(new_height):
        line = []
        for x in range(new_width):
            r, g, b = pixels.getpixel((x, y))
            # Apply brightness adjustment
            r = min(255, int(r * brightness))
            g = min(255, int(g * brightness))
            b = min(255, int(b * brightness))
            line.append(rgb_to_ansi(r, g, b))
        ansi_art.append(''.join(line) + '\x1b[0m')
    
    return '\n'.join(ansi_art)

def create_html(ansi_art, output_path, image_path):
    """
    Create HTML file using template system.
    """
    template_path = os.path.join('templates', 'ansi_viewer.html')
    
    # Sanitize image path for JavaScript
    clean_image_path = image_path.replace('\\', '/')
    
    # Prepare context for template rendering
    context = {
        'ansi_art': ansi_art,
        'image_path': clean_image_path,
        'filename': os.path.splitext(os.path.basename(image_path))[0]
    }
    
    # Render the template
    html_content = render_template(template_path, context)
    
    # Write to output file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

def create_animated_html(ansi_art, output_path, image_path):
    """
    Create animated HTML using the animated viewer template.
    """
    # Generate effect variants
    effect_arts = [generate_simple_effect(ansi_art, i) for i in range(5)]
    
    # Use template for animated viewer if it exists, otherwise use inline HTML
    template_path = os.path.join('templates', 'animated_viewer.html')
    if os.path.exists(template_path):
        context = {
            'effects': repr(effect_arts),
            'image_path': image_path.replace('\\', '/'),
            'filename': os.path.splitext(os.path.basename(image_path))[0]
        }
        html_content = render_template(template_path, context)
    else:
        # Fallback to inline HTML for effect version
        html_content = f'''<!DOCTYPE html>
<html>
<head>
    <title>PixelPipe - Effects</title>
    <script src="https://cdn.jsdelivr.net/npm/ansi_up@5.1.0/ansi_up.min.js"></script>
    <link rel="stylesheet" href="/styles/ansi_viewer.css">
</head>
<body>
    <div class="sidebar">
        <button onclick="window.location.href='/'" title="Back to Gallery">🏠</button>
    </div>
    <div class="controls">
        <label>Brightness: <input type="range" id="brightness" min="0.5" max="3" step="0.1" value="1.0"></label>
        <div class="effect-buttons">
            Effects:
            <span data-effect="-1" class="selected">None</span>
            <span data-effect="0">Rainbow</span>
            <span data-effect="1">Glitch</span>
            <span data-effect="2">Matrix</span>
            <span data-effect="3">Fire</span>
            <span data-effect="4">Neon</span>
        </div>
    </div>
    <pre id="ansi-art"></pre>
    <script>
        const ansi_up = new AnsiUp();
        let arts = {repr(effect_arts)};
        let currentEffect = -1;
        
        function renderArt() {{
            if (currentEffect === -1) {{
                document.getElementById('ansi-art').innerHTML = ansi_up.ansi_to_html(arts[0]); // Use original art
            }} else {{
                document.getElementById('ansi-art').innerHTML = ansi_up.ansi_to_html(arts[currentEffect]);
            }}
        }}
        
        document.querySelectorAll('.effect-buttons span').forEach(btn => {{
            btn.addEventListener('click', function() {{
                document.querySelectorAll('.effect-buttons span').forEach(b => b.classList.remove('selected'));
                this.classList.add('selected');
                currentEffect = parseInt(this.getAttribute('data-effect'));
                renderArt();
            }});
        }});
        
        renderArt();
    </script>
</body>
</html>'''
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

def generate_simple_effect(ansi_art, effect_type):
    """
    Generate cool effect versions of ANSI art with proper ANSI code handling.
    """
    lines = ansi_art.split('\n')
    new_lines = []
    
    for y, line in enumerate(lines):
        # Parse ANSI codes properly to avoid breaking them
        chars = []
        i = 0
        while i < len(line):
            if line[i:i+2] == '\x1b[':
                # Find the end of the ANSI escape sequence
                end = line.find('m', i)
                if end != -1:
                    chars.append(line[i:end+1])  # Include the 'm'
                    i = end + 1
                else:
                    chars.append(line[i])
                    i += 1
            else:
                chars.append(line[i])
                i += 1
        
        # Apply effect
        if effect_type == 0:
            # Rainbow wave effect - shift hue across the image
            new_line = apply_rainbow_wave(chars, y, len(lines))
        elif effect_type == 1:
            # Glitch effect - random color shifts and intensity changes
            new_line = apply_glitch_effect(chars, y)
        elif effect_type == 2:
            # Matrix rain effect - green cascade with varying intensity
            new_line = apply_matrix_effect(chars, y, len(lines))
        elif effect_type == 3:
            # Fire effect - warm colors with flickering
            new_line = apply_fire_effect(chars, y, len(lines))
        elif effect_type == 4:
            # Neon glow effect - bright colors with pulsing
            new_line = apply_neon_effect(chars, y)
        else:
            new_line = ''.join(chars)
        
        new_lines.append(new_line)
    
    return '\n'.join(new_lines)

def apply_rainbow_wave(chars, row, total_rows):
    """Create a rainbow wave effect that shifts hue based on position."""
    import math
    
    result = []
    wave_offset = (row / total_rows) * 2 * math.pi
    
    for i, char in enumerate(chars):
        if char.startswith('\x1b[38;2;'):
            # Extract RGB values
            try:
                rgb_part = char[7:-1]  # Remove '\x1b[38;2;' and 'm'
                if 'm' in rgb_part:
                    rgb_part = rgb_part.split('m')[0]
                r, g, b = map(int, rgb_part.split(';'))
                
                # Convert to HSV, shift hue, convert back to RGB
                h, s, v = rgb_to_hsv(r, g, b)
                h = (h + wave_offset + (i * 0.1)) % (2 * math.pi)
                new_r, new_g, new_b = hsv_to_rgb(h, s, v)
                
                # Find the character after the color code
                char_part = char[char.find('m')+1:]
                result.append(f'\x1b[38;2;{new_r};{new_g};{new_b}m{char_part}')
            except (ValueError, IndexError):
                result.append(char)
        else:
            result.append(char)
    
    return ''.join(result)

def apply_glitch_effect(chars, row):
    """Create a digital glitch effect with bigger blobs instead of single spots."""
    import random
    
    result = []
    # Create glitch "zones" - bigger blobs of corruption
    glitch_zones = []
    
    # Generate random glitch zones for this row
    if random.random() < 0.15:  # 15% chance for any glitch on this row
        num_zones = random.randint(1, 3)  # 1-3 glitch zones per row
        for _ in range(num_zones):
            zone_start = random.randint(0, max(0, len(chars) - 10))
            zone_size = random.randint(5, 15)  # Bigger glitch blobs
            glitch_type = random.choice(['color_shift', 'invert', 'corrupt', 'noise'])
            glitch_zones.append({
                'start': zone_start,
                'end': min(len(chars), zone_start + zone_size),
                'type': glitch_type,
                'intensity': random.uniform(0.5, 1.0)
            })
    
    for i, char in enumerate(chars):
        # Check if this character is in a glitch zone
        in_glitch_zone = False
        glitch_type = 'normal'
        glitch_intensity = 1.0
        
        for zone in glitch_zones:
            if zone['start'] <= i < zone['end']:
                in_glitch_zone = True
                glitch_type = zone['type']
                glitch_intensity = zone['intensity']
                break
        
        if char.startswith('\x1b[38;2;') and in_glitch_zone:
            try:
                rgb_part = char[7:-1]
                if 'm' in rgb_part:
                    rgb_part = rgb_part.split('m')[0]
                r, g, b = map(int, rgb_part.split(';'))
                
                if glitch_type == 'color_shift':
                    # Shift color channels dramatically
                    shift = int(100 * glitch_intensity)
                    r = min(255, max(0, r + random.randint(-shift, shift)))
                    g = min(255, max(0, g + random.randint(-shift, shift)))
                    b = min(255, max(0, b + random.randint(-shift, shift)))
                    
                elif glitch_type == 'invert':
                    # Invert colors completely
                    r, g, b = 255-r, 255-g, 255-b
                    
                elif glitch_type == 'corrupt':
                    # Digital corruption - random bright colors
                    corruption_colors = [
                        (255, 0, 255),  # Magenta
                        (0, 255, 255),  # Cyan
                        (255, 255, 0),  # Yellow
                        (255, 0, 0),    # Red
                        (0, 255, 0),    # Green
                    ]
                    r, g, b = random.choice(corruption_colors)
                    
                elif glitch_type == 'noise':
                    # Add random noise while preserving some original color
                    noise = random.randint(0, 100)
                    r = min(255, max(0, int(r * 0.3) + noise))
                    g = min(255, max(0, int(g * 0.3) + noise))
                    b = min(255, max(0, int(b * 0.3) + noise))
                
                char_part = char[char.find('m')+1:]
                result.append(f'\x1b[38;2;{r};{g};{b}m{char_part}')
            except (ValueError, IndexError):
                result.append(char)
        else:
            result.append(char)
    
    return ''.join(result)

def apply_matrix_effect(chars, row, total_rows):
    """Create a Matrix-style digital rain effect."""
    import random
    
    result = []
    # Green intensity varies by row (top is brighter)
    intensity = max(0.3, 1.0 - (row / total_rows))
    
    for char in chars:
        if char.startswith('\x1b[38;2;'):
            try:
                rgb_part = char[7:-1]
                if 'm' in rgb_part:
                    rgb_part = rgb_part.split('m')[0]
                r, g, b = map(int, rgb_part.split(';'))
                
                # Convert to green with varying intensity
                brightness = (r + g + b) / 3
                green_val = int(brightness * intensity * random.uniform(0.7, 1.3))
                green_val = min(255, max(0, green_val))
                
                # Add some random bright green highlights
                if random.random() < 0.05:
                    green_val = 255
                
                char_part = char[char.find('m')+1:]
                result.append(f'\x1b[38;2;0;{green_val};0m{char_part}')
            except (ValueError, IndexError):
                result.append(char)
        else:
            result.append(char)
    
    return ''.join(result)

def apply_fire_effect(chars, row, total_rows):
    """Create a fire effect with warm colors."""
    import random
    
    result = []
    # Fire is hottest at bottom, cooler at top
    heat = 1.0 - (row / total_rows)
    
    for char in chars:
        if char.startswith('\x1b[38;2;'):
            try:
                rgb_part = char[7:-1]
                if 'm' in rgb_part:
                    rgb_part = rgb_part.split('m')[0]
                r, g, b = map(int, rgb_part.split(';'))
                
                brightness = (r + g + b) / 3
                
                # Create fire colors based on heat and brightness
                if heat > 0.7:  # Hot - white/yellow
                    new_r = min(255, int(brightness * 1.2))
                    new_g = min(255, int(brightness * 1.1))
                    new_b = int(brightness * 0.3)
                elif heat > 0.4:  # Medium - orange/red
                    new_r = min(255, int(brightness * 1.3))
                    new_g = int(brightness * 0.6)
                    new_b = int(brightness * 0.1)
                else:  # Cool - red/dark
                    new_r = int(brightness * 0.8)
                    new_g = int(brightness * 0.2)
                    new_b = 0
                
                # Add random flicker
                flicker = random.uniform(0.8, 1.2)
                new_r = min(255, int(new_r * flicker))
                new_g = min(255, int(new_g * flicker))
                new_b = min(255, int(new_b * flicker))
                
                char_part = char[char.find('m')+1:]
                result.append(f'\x1b[38;2;{new_r};{new_g};{new_b}m{char_part}')
            except (ValueError, IndexError):
                result.append(char)
        else:
            result.append(char)
    
    return ''.join(result)

def apply_neon_effect(chars, row):
    """Create a comprehensive neon glow effect that transforms the entire image."""
    import random
    import math
    
    result = []
    
    # Pulsing effect - varies across the image
    time_offset = row * 0.1  # Different pulse timing per row
    pulse = 0.8 + 0.4 * math.sin(time_offset)  # Smooth pulsing between 0.8 and 1.2
    
    # Neon color palettes to choose from
    neon_palettes = [
        'electric_blue',
        'hot_pink',
        'acid_green',
        'cyber_purple',
        'sunset_orange'
    ]
    
    # Choose a dominant palette for this row (changes per row for variety)
    row_palette = neon_palettes[row % len(neon_palettes)]
    
    for i, char in enumerate(chars):
        if char.startswith('\x1b[38;2;'):
            try:
                rgb_part = char[7:-1]
                if 'm' in rgb_part:
                    rgb_part = rgb_part.split('m')[0]
                r, g, b = map(int, rgb_part.split(';'))
                
                # Get original brightness to preserve image structure
                brightness = (r + g + b) / 3 / 255.0
                
                # Apply neon transformation based on palette
                if row_palette == 'electric_blue':
                    new_r = int(brightness * 100 * pulse)
                    new_g = int(brightness * 200 * pulse)
                    new_b = int(brightness * 255 * pulse)
                    
                elif row_palette == 'hot_pink':
                    new_r = int(brightness * 255 * pulse)
                    new_g = int(brightness * 50 * pulse)
                    new_b = int(brightness * 150 * pulse)
                    
                elif row_palette == 'acid_green':
                    new_r = int(brightness * 50 * pulse)
                    new_g = int(brightness * 255 * pulse)
                    new_b = int(brightness * 100 * pulse)
                    
                elif row_palette == 'cyber_purple':
                    new_r = int(brightness * 200 * pulse)
                    new_g = int(brightness * 50 * pulse)
                    new_b = int(brightness * 255 * pulse)
                    
                elif row_palette == 'sunset_orange':
                    new_r = int(brightness * 255 * pulse)
                    new_g = int(brightness * 150 * pulse)
                    new_b = int(brightness * 50 * pulse)
                
                # Add random neon highlights for extra glow
                if random.random() < 0.08:
                    glow_boost = random.uniform(1.2, 1.8)
                    new_r = min(255, int(new_r * glow_boost))
                    new_g = min(255, int(new_g * glow_boost))
                    new_b = min(255, int(new_b * glow_boost))
                
                # Add subtle color bleeding to adjacent areas
                if random.random() < 0.05:
                    bleed_colors = [
                        (0, 255, 255),    # Cyan bleed
                        (255, 0, 255),    # Magenta bleed
                        (255, 255, 0),    # Yellow bleed
                    ]
                    bleed_r, bleed_g, bleed_b = random.choice(bleed_colors)
                    new_r = min(255, (new_r + bleed_r) // 2)
                    new_g = min(255, (new_g + bleed_g) // 2)
                    new_b = min(255, (new_b + bleed_b) // 2)
                
                # Ensure minimum brightness for neon effect
                min_neon_brightness = 80
                if new_r + new_g + new_b < min_neon_brightness * 3:
                    boost_factor = (min_neon_brightness * 3) / max(1, new_r + new_g + new_b)
                    new_r = min(255, int(new_r * boost_factor))
                    new_g = min(255, int(new_g * boost_factor))
                    new_b = min(255, int(new_b * boost_factor))
                
                # Clamp values
                new_r = max(0, min(255, new_r))
                new_g = max(0, min(255, new_g))
                new_b = max(0, min(255, new_b))
                
                char_part = char[char.find('m')+1:]
                result.append(f'\x1b[38;2;{new_r};{new_g};{new_b}m{char_part}')
            except (ValueError, IndexError):
                result.append(char)
        else:
            result.append(char)
    
    return ''.join(result)

def rgb_to_hsv(r, g, b):
    """Convert RGB to HSV color space."""
    import math
    
    r, g, b = r/255.0, g/255.0, b/255.0
    max_val = max(r, g, b)
    min_val = min(r, g, b)
    diff = max_val - min_val
    
    # Hue
    if diff == 0:
        h = 0
    elif max_val == r:
        h = (60 * ((g - b) / diff) + 360) % 360
    elif max_val == g:
        h = (60 * ((b - r) / diff) + 120) % 360
    else:
        h = (60 * ((r - g) / diff) + 240) % 360
    
    # Convert to radians
    h = h * math.pi / 180
    
    # Saturation
    s = 0 if max_val == 0 else diff / max_val
    
    # Value
    v = max_val
    
    return h, s, v

def hsv_to_rgb(h, s, v):
    """Convert HSV to RGB color space."""
    import math
    
    h = h * 180 / math.pi  # Convert back to degrees
    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c
    
    if 0 <= h < 60:
        r, g, b = c, x, 0
    elif 60 <= h < 120:
        r, g, b = x, c, 0
    elif 120 <= h < 180:
        r, g, b = 0, c, x
    elif 180 <= h < 240:
        r, g, b = 0, x, c
    elif 240 <= h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x
    
    r = int((r + m) * 255)
    g = int((g + m) * 255)
    b = int((b + m) * 255)
    
    return max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))
