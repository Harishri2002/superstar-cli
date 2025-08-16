import time
import os
import sys
import random
import playsound

# --- Configuration ---
TRACE_SPEED = 0.015
RAJNI_SPEED = 0.4
GLOW_DURATION = 3
GLOW_SPEED = 0.05

# --- ANSI Color Codes ---
class Colors:
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[96m'
    BRIGHT_YELLOW = '\033[93;1m'
    RESET = '\033[0m'

# --- Helper Functions ---
def clear_screen(): os.system('cls' if os.name == 'nt' else 'clear')
def hide_cursor(): sys.stdout.write("\033[?25l"); sys.stdout.flush()
def show_cursor(): sys.stdout.write("\033[?25h"); sys.stdout.flush()

# --- ASCII Art & Trace Path Definitions ---
DOT_ART = { 'S':[" ●●●","●   "," ●●●","   ●","●●● "],'U':["●  ●","●  ●","●  ●","●  ●"," ●●●"],'P':["●●● ","●  ●","●●● ","●   ","●   "],'E':["●●●●","●   ","●●● ","●   ","●●●●"],'R':["●●● ","●  ●","●●● ","● ● ","●  ●"],'T':["●●●●●","  ●  ","  ●  ","  ●  ","  ●  "],'A':[" ●●● ","●   ●","●●●●●","●   ●","●   ●"],' ':["     ","     ","     ","     ","     "] }
TRACE_ORDER = { 'S':[(1,0),(2,0),(3,0),(0,1),(1,2),(2,2),(3,2),(4,3),(3,4),(2,4),(1,4),(0,4)], 'U':[(0,0),(0,1),(0,2),(0,3),(0,4),(1,4),(2,4),(3,4),(4,4),(4,3),(4,2),(4,1),(4,0)], 'P':[(0,4),(0,3),(0,2),(0,1),(0,0),(1,0),(2,0),(3,0),(4,1),(3,2),(2,2),(1,2)], 'E':[(4,0),(3,0),(2,0),(1,0),(0,0),(0,1),(0,2),(0,3),(0,4),(1,4),(2,4),(3,4),(4,4),(0,2),(1,2),(2,2)], 'R':[(0,4),(0,3),(0,2),(0,1),(0,0),(1,0),(2,0),(3,0),(4,1),(3,2),(2,2),(1,2),(2,3),(3,4)], 'T':[(0,0),(1,0),(2,0),(3,0),(4,0),(2,1),(2,2),(2,3),(2,4)], 'A':[(0,4),(0,3),(0,2),(1,0),(2,0),(3,0),(4,1),(4,2),(4,3),(4,4),(0,2),(1,2),(2,2),(3,2)] }
SOLID_ART = { 'R':["███ ","█  █","███ ","█ █ ","█  █"],'A':[" ██ ","█  █","████","█  █","█  █"],'J':["   █","   █","   █","█  █"," ██ "],'N':["█  █","██ █","█ ██","█  █","█  █"],'I':["███"," █ "," █ "," █ ","███"],' ':["    ","    ","    ","    ","    "] }

def get_text_width(text, art_dict):
    width = 0
    for char in text:
        if char != ' ':
            width += len(art_dict.get(char)[0])
        else:
            width += 5
    return width

# --- Unified Renderer ---
def render_frame(canvas_width, top_coords={}, middle_coords={}, bottom_coords={}, glow_sets={}):
    height = 22
    padding = (os.get_terminal_size().columns - canvas_width) // 2
    if padding < 0: padding = 0

    output = ""
    for y in range(height):
        line = ""
        for x in range(canvas_width):
            top_char = f"{Colors.BRIGHT_BLUE if (x,y) in glow_sets.get('top', set()) else Colors.BLUE}●"
            middle_char = f"{Colors.BRIGHT_YELLOW if (x,y) in glow_sets.get('middle', set()) else Colors.YELLOW}█"
            bottom_char = f"{Colors.BRIGHT_BLUE if (x,y) in glow_sets.get('bottom', set()) else Colors.BLUE}●"

            if (x, y) in top_coords: line += top_char
            elif (x, y) in middle_coords: line += middle_char
            elif (x, y) in bottom_coords: line += bottom_char
            else: line += ' '
        output += " " * padding + line + '\n'
    clear_screen(); sys.stdout.write(output + Colors.RESET); sys.stdout.flush()

# --- Animation Functions ---
def trace_word(text_to_draw, y_offset, existing_dots, canvas_width):
    newly_drawn_dots = set()
    cursor_x = 0
    word_width = get_text_width(text_to_draw, DOT_ART)
    x_offset = (canvas_width - word_width) // 2

    for char in text_to_draw:
        if char in TRACE_ORDER:
            for (px, py) in TRACE_ORDER[char]:
                newly_drawn_dots.add((cursor_x + px + x_offset, y_offset + py))
                render_frame(canvas_width, top_coords=existing_dots.union(newly_drawn_dots))
                time.sleep(TRACE_SPEED)
        cursor_x += len(DOT_ART.get(char, DOT_ART[' '])[0])
    return existing_dots.union(newly_drawn_dots)

def animate_rajni_reveal(top_coords, bottom_coords, canvas_width):
    text_middle = "R A J N I"
    y_offset = 8
    revealed_coords = set()
    cursor_x = 0
    word_width = get_text_width(text_middle, SOLID_ART)

    # --- THE ONLY CHANGE IS HERE ---
    # Manually nudged the text 2 spaces to the right for perfect visual alignment.
    x_offset = (canvas_width - word_width) // 2 + 2

    for char in text_middle:
        if char != ' ':
            art = SOLID_ART.get(char, SOLID_ART[' '])
            for y, line in enumerate(art):
                for x, pixel in enumerate(line):
                    if pixel != ' ':
                        revealed_coords.add((cursor_x + x + x_offset, y + y_offset))
            render_frame(canvas_width, top_coords, revealed_coords, bottom_coords)
            time.sleep(RAJNI_SPEED)
        
        if char in SOLID_ART: cursor_x += len(SOLID_ART.get(char)[0])
        else: cursor_x += 5

    return revealed_coords

def animate_glow(top_coords, middle_coords, bottom_coords, canvas_width):
    start_time = time.time()
    while time.time() - start_time < GLOW_DURATION:
        glow_sets = {
            'top': set(random.sample(list(top_coords), k=len(top_coords)//3)),
            'middle': set(random.sample(list(middle_coords), k=len(middle_coords)//3)),
            'bottom': set(random.sample(list(bottom_coords), k=len(bottom_coords)//3)) }
        render_frame(canvas_width, top_coords, middle_coords, bottom_coords, glow_sets)
        time.sleep(GLOW_SPEED)

# --- Run the Animation ---
if __name__ == "__main__":
    try:
        try:
            playsound.playsound('./assets/Rajani-8Bit.mp3', False)
        except Exception as e:
            print(f"Could not play music. Error: {e}\nAnimation will continue without sound.")
            time.sleep(3)

        hide_cursor()
        
        super_width = get_text_width("S U P E R", DOT_ART)
        star_width = get_text_width("S T A R", DOT_ART)
        rajni_width = get_text_width("R A J N I", SOLID_ART)
        canvas_width = max(super_width, star_width, rajni_width)

        top_coords = trace_word("S U P E R", y_offset=2, existing_dots=set(), canvas_width=canvas_width)
        time.sleep(0.2)

        all_traced_coords = trace_word("S T A R", y_offset=14, existing_dots=top_coords, canvas_width=canvas_width)
        final_top_coords = {(x, y) for (x, y) in all_traced_coords if y < 10}
        final_bottom_coords = {(x, y) for (x, y) in all_traced_coords if y >= 10}
        time.sleep(0.5)

        final_middle_coords = animate_rajni_reveal(final_top_coords, final_bottom_coords, canvas_width)
        time.sleep(1)

        animate_glow(final_top_coords, final_middle_coords, final_bottom_coords, canvas_width)
        
    finally:
        show_cursor()