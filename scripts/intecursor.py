import os
import subprocess

# First, try to get the current display
try:
    display = subprocess.check_output(['echo $DISPLAY'], shell=True).decode().strip()
    if display:
        os.environ['DISPLAY'] = display
    else:
        os.environ['DISPLAY'] = ':0'
except:
    os.environ['DISPLAY'] = ':0'

# Run xhost to allow local connections
try:
    subprocess.run(['xhost', '+local:'], check=True)
except subprocess.CalledProcessError:
    print("Warning: Could not set xhost permissions. You may need to run 'xhost +local:' manually.")

# Set XAUTHORITY environment variable if needed
if 'XAUTHORITY' not in os.environ:
    os.environ['XAUTHORITY'] = os.path.expanduser('~/.Xauthority')

import pyautogui
import time
import pandas as pd

# First, try to install xclip if not present
try:
    subprocess.run(['which', 'xclip'], check=True)
except subprocess.CalledProcessError:
    print("Installing xclip...")
    try:
        subprocess.run(['sudo', 'apt-get', 'install', '-y', 'xclip'], check=True)
    except subprocess.CalledProcessError:
        print("Failed to install xclip. Please run 'sudo apt-get install xclip' manually.")

# Function to automate Cursor Chat
def interact_with_cursor_chat(link):
    try:
        # Bring Cursor Chat to focus and send message
        time.sleep(2)
        pyautogui.hotkey('ctrl', 'l')  
        time.sleep(1)
        message = f"Summarize this GitHub repo: {link}"
        pyautogui.write(message)
        time.sleep(1)
        pyautogui.press('enter')
        
        # Wait longer for response to fully load
        time.sleep(15)  # Increased wait time for response generation

        # Method 1: Try clicking the copy button (adjust coordinates as needed)
        try:
            # Move to where the last message's copy button typically appears
            # You'll need to adjust these coordinates based on your screen
            pyautogui.moveTo(800, 500)  # Example coordinates
            time.sleep(0.5)
            # Look for and click the copy button
            pyautogui.click()
            time.sleep(1)
        except:
            # Method 2: Fallback to text selection
            # Click to focus on the last message
            pyautogui.click()
            time.sleep(0.5)
            # Double click to select the message text
            pyautogui.doubleClick()
            time.sleep(0.5)
            # Copy the selected text
            pyautogui.hotkey('ctrl', 'c')
            time.sleep(1)
        
        # Try multiple methods to get clipboard content
        response = None
        
        # Method 1: xclip
        try:
            response = subprocess.check_output(
                ['xclip', '-selection', 'clipboard', '-o'],
                universal_newlines=True,
                stderr=subprocess.DEVNULL
            ).strip()
        except:
            pass
            
        # Method 2: pyperclip
        if not response:
            try:
                import pyperclip
                response = pyperclip.paste().strip()
            except:
                pass
        
        if not response:
            return "Failed to get response from clipboard"
            
        return response

    except Exception as e:
        return f"Error: {str(e)}"

# Load CSV and extract first 5 repo links
input_csv = "data_extraction_framework.csv"
column_name = "Image URL"

try:
    # Read CSV with error handling
    df = pd.read_csv(input_csv, delimiter=";", encoding="utf-8", on_bad_lines="skip")
    if column_name not in df.columns:
        raise ValueError(f"Column '{column_name}' not found in CSV file")
    
    df = df.head(5)
    output_txt = "output.txt"

    # Open file to save results
    with open(output_txt, "w", encoding="utf-8") as file:
        for index, row in df.iterrows():
            link = row[column_name]
            if pd.notna(link):
                response = interact_with_cursor_chat(link)  # Automate interaction
                file.write(f"Repo: {link}\nResponse:\n{response}\n\n")
                print(f"Processed repo: {link}")

    print(f"Results saved in {output_txt}")

except Exception as e:
    print(f"Error processing CSV: {str(e)}")
    print("Please check if your CSV file is properly formatted and contains the correct column name.")

def get_cursor_position():
    """Helper function to get current cursor position"""
    try:
        while True:
            x, y = pyautogui.position()
            print(f"Current position: x={x}, y={y}")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nPosition recording stopped")
