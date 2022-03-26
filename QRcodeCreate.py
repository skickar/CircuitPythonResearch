# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import board
import displayio
import adafruit_miniqr
import os
import board
import neopixel
from board import SCL, SDA
import busio
import displayio
import adafruit_framebuf
import adafruit_displayio_sh1106
import time

displayio.release_displays()
WIDTH = 130 # Change these to the right size for your display!
HEIGHT = 64
BORDER = 1
i2c = busio.I2C(SCL, SDA) # Create the I2C interface.
display_bus = displayio.I2CDisplay(i2c, device_address=0x3c)
display = adafruit_displayio_sh1106.SH1106(display_bus, width=WIDTH, height=HEIGHT) # Create the SH1106 OLED class.



def bitmap_QR(matrix):
    # monochome (2 color) palette
    BORDER_PIXELS = 1

    # bitmap the size of the screen, monochrome (2 colors)
    bitmap = displayio.Bitmap(
        matrix.width + 2 * BORDER_PIXELS, matrix.height + 2 * BORDER_PIXELS, 2
    )
    # raster the QR code
    for y in range(matrix.height):  # each scanline in the height
        for x in range(matrix.width):
            if matrix[x, y]:
                bitmap[x + BORDER_PIXELS, y + BORDER_PIXELS] = 1
            else:
                bitmap[x + BORDER_PIXELS, y + BORDER_PIXELS] = 0
    return bitmap




qr = adafruit_miniqr.QRCode(qr_type=3, error_correct=adafruit_miniqr.L)
qr.add_data(b"WIFI:T:WPA;S:MyOnlyVaronis;P:MySecretVaronis;H:;")
qr.make()

# generate the 1-pixel-per-bit bitmap
qr_bitmap = bitmap_QR(qr.matrix)
# We'll draw with a classic black/white palette
palette = displayio.Palette(2)
palette[0] = 0xFFFFFF
palette[1] = 0x000000
# we'll scale the QR code as big as the display can handle
scale = min(
    display.width // qr_bitmap.width, display.height // qr_bitmap.height
)
# then center it!
pos_x = int(((display.width / scale) - qr_bitmap.width) / 2)
pos_y = int(((display.height / scale) - qr_bitmap.height) / 2)
qr_img = displayio.TileGrid(qr_bitmap, pixel_shader=palette, x=pos_x, y=pos_y)

splash = displayio.Group(scale=scale)
splash.append(qr_img)
display.show(splash)

# Hang out forever
while True:
    pass
