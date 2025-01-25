import adafruit_display_text.label
import board
import displayio
import framebufferio
import rgbmatrix
import terminalio
import requests
import time

matrix = rgbmatrix.RGBMatrix(
    width=64, height=32, bit_depth=1,
    rgb_pins=[board.D6, board.D5, board.D9, board.D11, board.D10, board.D12],
    addr_pins=[board.A5, board.A4, board.A3, board.A2],
    clock_pin=board.D13, latch_pin=board.D0, output_enable_pin=board.D1)
display = framebufferio.FramebufferDisplay(matrix, auto_refresh=False)

def get_bible_verse():
    try:
        url = "https://bible-api.com/data/web/random"
        response = requests.get(url)
        data = response.json()
        verse_text = data['random_verse']['text']
        reference = f"{data['random_verse']['book']} {data['random_verse']['chapter']}:{data['random_verse']['verse']}"
        return verse_text, reference
    except Exception as e:
        print("Error fetching Bible verse:", e)
        return "Error fetching verse", "Error"

verse_text, reference = get_bible_verse()
verse_words = verse_text.split()
verse_labels = []


x_position = 0
y_position = display.height - 13 
line_height = 10
max_width = display.width
current_line = []

for word in verse_words:
    word_label = adafruit_display_text.label.Label(
        terminalio.FONT,
        color=0xffffff,
        text=word
    )
    
  
    word_width = word_label.bounding_box[2]
    
  
    if x_position + word_width <= max_width:
        word_label.x = x_position
        word_label.y = y_position 
        current_line.append(word_label)
        x_position += word_width + 2 
    else:
        y_position += line_height
        x_position = 0 
        current_line = [word_label]
        word_label.x = x_position
        word_label.y = y_position
        x_position += word_width + 2

    verse_labels.append(word_label)
reference_label = adafruit_display_text.label.Label(
    terminalio.FONT,
    color=0x00ff00,
    text=reference
)
reference_label.x = display.width
reference_label.y = 15

group = displayio.Group()
for label in verse_labels:
    group.append(label)
group.append(reference_label)
display.root_group = group

import time
verse_scrolled = False

def scroll_verse():
    global verse_scrolled
    for label in verse_labels:
        label.y -= 1
        time.sleep(0.001)
    

    if verse_labels[0].y + len(verse_labels) * 8 < 0:
        y_position = display.height
        x_position = 0
        for index, label in enumerate(verse_labels):
            label.y = y_position
            x_position += label.bounding_box[2] + 2
        time.sleep(0.0001)
        verse_scrolled = True

def scroll_reference():
    if verse_scrolled:
        reference_label.x -= 1
        if reference_label.x + reference_label.bounding_box[2] < 0:
            reference_label.x = display.width



while True:
    scroll_verse()
    scroll_reference()
    display.refresh(minimum_frames_per_second=0)
    time.sleep(0.005)
