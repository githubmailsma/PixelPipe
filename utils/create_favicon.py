from PIL import Image, ImageDraw

def create_favicon():
    # Create a 32x32 image with dark background
    img = Image.new('RGBA', (32, 32), (42, 42, 42, 255))
    draw = ImageDraw.Draw(img)
    
    # Colors for the pixel art (ANSI-inspired)
    cyan = (0, 255, 255, 255)
    magenta = (255, 0, 255, 255)
    
    # Draw first 'P' in cyan
    pixels_p1 = [
        (8, 8), (9, 8), (10, 8),
        (8, 9), (11, 9),
        (8, 10), (11, 10),
        (8, 11), (9, 11), (10, 11),
        (8, 12), (8, 13)
    ]
    
    # Draw second 'P' in magenta
    pixels_p2 = [
        (16, 8), (17, 8), (18, 8),
        (16, 9), (19, 9),
        (16, 10), (19, 10),
        (16, 11), (17, 11), (18, 11),
        (16, 12), (16, 13)
    ]
    
    # Draw the pixels
    for x, y in pixels_p1:
        draw.rectangle([x*2, y*2, x*2+1, y*2+1], fill=cyan)
    for x, y in pixels_p2:
        draw.rectangle([x*2, y*2, x*2+1, y*2+1], fill=magenta)
    
    # Save as PNG
    img.save('static/favicon.png')
    
    # Also create ICO version
    img.save('static/favicon.ico', format='ICO', sizes=[(32, 32)])

if __name__ == '__main__':
    create_favicon()
