import time
import os
import cv2

from scanner import config
from scanner.wled import WLED

ANGLES = [0, 90, 180, 270]


def init():
    # Get amount of LEDs to scan
    global leds
    leds = config.get_config().get('wled_led_count')
    # Get IP address of WLED device
    ip = config.get_config().get('wled_ip')

    # Attempt to connect to WLED device
    try:
        global wled
        wled = WLED(ip, leds)
        wled.on()
        time.sleep(0.2)
        wled.off()
    except Exception as e:
        print(f'Failed to connect to WLED device: {e}')
        return


def take_picture(index, angle):
    # Turn on LED
    result = wled.set_led(index)
    if result.json() != {'success': True}:
        print(f'Failed to turn on LED {index}')
        return

    # Take picture
    # Clear ret and frame variables
    cam = cv2.VideoCapture(config.get_config().get('camera_index'))
    if not cam.isOpened():
        print('Failed to open camera')
        return

    ret, frame = cam.read()
    cam.release()
    # Ensure picture was taken
    if not ret:
        print('Failed to take picture')
        return False

    # Ensure directory exists
    if not os.path.exists(f'images/{angle}/'):
        os.makedirs(f'images/{angle}/')
    # Save picture
    cv2.imwrite(f'images/{angle}/{index}.png', frame)

    # Turn off LED
    wled.set_led(index, (0, 0, 0))
    time.sleep(config.get_config().get("wled_scan_delay"))
    return True


def scan_angle(angle):
    print(f'Please rotate to angle {angle}')
    input('Press enter to continue...')
    # Scan LEDs
    for i in range(1, leds + 1):
        retries = 0
        print(f'Scanning LED {i}')
        if not take_picture(i, angle):
            if retries < 3:
                retries += 1
                print(f'Retrying ({i}/3)')
                i -= 1
                continue

            return
    wled.on([0, 255, 0])
    time.sleep(1)
    wled.off()


def scan_from(start_at):
    for angle in ANGLES:
        if int(angle) < start_at:
            continue
        print(f'Scanning angle {angle}')
        scan_angle(angle)
