from image_to_ansi import image_to_ansi, create_html, create_animated_html
from subprocess import Popen
import os
import time

def show_menu():
    print("\nSelect conversion option:")
    print("1. Basic image conversion")
    print("2. Image conversion with brightness control")
    print("3. Animated image conversion")
    return input("Enter choice (1-3): ")

def main():
    image_path = 'castle.png'
    output_path = 'output.html'
    
    choice = show_menu()
    
    server_process = Popen(['python', 'server.py'])
    time.sleep(1)
    
    # Process based on choice
    ansi_art = image_to_ansi(image_path, 250)
    
    if choice == '1':
        create_html(ansi_art, output_path, image_path, include_brightness=False)
    elif choice == '2':
        create_html(ansi_art, output_path, image_path, include_brightness=True)
    elif choice == '3':
        create_animated_html(ansi_art, output_path, image_path)
    else:
        print("Invalid choice. Using basic conversion.")
        create_html(ansi_art, output_path, image_path, include_brightness=False)
    
    os.system(f'start {output_path}')
    input("Press Enter to quit...")
    server_process.terminate()

if __name__ == '__main__':
    main()
