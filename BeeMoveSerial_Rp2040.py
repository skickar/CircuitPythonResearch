import board
import busio
import time
import os
import neopixel
import gc

# UART config (adjust TX/RX pins)
uart = busio.UART(tx=board.GP4, rx=board.GP5, baudrate=38400, timeout=1)

# NeoPixel LED config
LED_PIN = board.GP16
pixel = neopixel.NeoPixel(LED_PIN, 1, brightness=0.3, auto_write=False)

def led_flash(times=3, delay=0.1, color=(0,255,0)):
    for _ in range(times):
        pixel[0] = color
        pixel.write()
        time.sleep(delay)
        pixel[0] = (0,0,0)
        pixel.write()
        time.sleep(delay)

FILENAME = "beemovie.txt"
TARGET_CHARS = 150
SEND_DELAY = 2
ACK_TIMEOUT = 5

def send_and_wait(msg):
    try:
        uart.write(msg.encode("utf-8"))
    except Exception as e:
        print("ERROR UART write:", e)
        return False
    print("Sent:", msg[:100], "…")
    start = time.monotonic()
    buffer = b""
    while time.monotonic() - start < ACK_TIMEOUT:
        data = uart.read(32)
        if data:
            buffer += data
            try:
                s = buffer.decode("utf-8", errors="ignore")
            except:
                s = ""
            if s.strip():
                print("ACK received:", s.strip())
                led_flash(color=(0,255,0))
                return True
        time.sleep(0.1)
    print("WARNING: No ACK within timeout.")
    led_flash(color=(255,0,0))
    return False

def stream_and_chunk(file_path, target_len=TARGET_CHARS):
    """Generator that yields text chunks approx target_len characters, splitting on word boundaries."""
    buf = ""
    with open(file_path, "r") as f:
        for line in f:
            # split line into words and append to buffer
            for word in line.split():
                if buf:
                    sep = " "
                else:
                    sep = ""
                # if adding this word would exceed target length
                if len(buf) + len(sep) + len(word) > target_len:
                    yield buf
                    buf = word
                else:
                    buf = buf + sep + word
    if buf:
        yield buf

def main():
    if FILENAME not in os.listdir():
        print("Error: File not found:", FILENAME)
        return

    chunk_generator = stream_and_chunk(FILENAME, TARGET_CHARS)
    idx = 1
    for chunk in chunk_generator:
        print(f"Sending chunk #{idx}")
        gc.collect()  # free up memory
        _ = send_and_wait(chunk)
        idx += 1
        time.sleep(SEND_DELAY)

if __name__ == "__main__":
    main()
