# Test Leds

from time import sleep
import requests
from datetime import datetime, timedelta
from gpiozero import LED, RGBLED
import threading, time

# Définition des LEDs
# led_bleu = LED(16)
# led_blanc = LED(20)
# led_rouge = LED(21)
#
# leds = [("Bleu", led_bleu), ("Blanc", led_blanc), ("Rouge", led_rouge)]

# # GPIO affectation
leds_today = {
    "BLEU": LED(16),
    "BLANC": LED(20),
    "ROUGE": LED(21)
}
leds_tomorrow = {
    "BLEU": LED(13),
    "BLANC": LED(19),
    "ROUGE": LED(26)
}
led_rgb = RGBLED(red=22, green=27, blue=17)


print("=== Test des LEDs ===")
print("Chaque LED va s’allumer à tour de rôle...")

try:
    for i in range(0, 2):
        for name, led in leds_today.items():
            print(f"Jour actuel : {name}")
            led.on()
            sleep(1)
            led.off()
            sleep(0.5)

        for name, led in leds_tomorrow.items():
            print(f"Demain : {name}")
            led.on()
            sleep(1)
            led.off()
            sleep(0.5)

        print("Test LED RGB")
        for _ in range(0, 2):
            led_rgb.color = (1, 0, 0)  # Rouge
            sleep(1)
            led_rgb.color = (0, 1, 0)  # Vert
            sleep(1)
            led_rgb.color = (0, 0, 1)  # Bleu
            sleep(1)
            led_rgb.off()
except KeyboardInterrupt:
    print("\nArrêt du test.")
finally:
    for led in leds_today.values():
        led.off()
    for led in leds_tomorrow.values():
        led.off()
    led_rgb.off()
    print("Toutes les LEDs éteintes.")


#MAIN

# import requests
# from datetime import datetime, timedelta
# from gpiozero import LED, RGBLED
# import threading, time
#
# # === CONFIGURATION ===
# API_URL = "https://digital.iservices.rte-france.com/open_api/tempo_like_supply_contract/v1/sandbox/tempo_like_calendars"
# API_KEY = "TaCléAPI"
#
# # GPIO affectation
# leds_today = {
#     "BLEU": LED(2),
#     "BLANC": LED(3),
#     "ROUGE": LED(4)
# }
# leds_tomorrow = {
#     "BLEU": LED(17),
#     "BLANC": LED(27),
#     "ROUGE": LED(22)
# }
# led_rgb = RGBLED(red=19, green=20, blue=21)
#
# # Animation flag
# animation_running = False
#
#
# # === UTILS ===
# def clear_all():
#     for l in leds_today.values(): l.off()
#     for l in leds_tomorrow.values(): l.off()
#     led_rgb.off()
#
# def set_color_group(group, color):
#     clear_all()
#     if color in group:
#         group[color].on()
#
# # === ANIMATION RGB ===
# def smooth_rgb_animation():
#     global animation_running
#     animation_running = True
#     colors = [
#         (1, 0, 0), (1, 1, 0),
#         (0, 1, 0), (0, 1, 1),
#         (0, 0, 1), (1, 0, 1)
#     ]
#     while animation_running:
#         for i in range(len(colors)):
#             c1 = colors[i]
#             c2 = colors[(i+1) % len(colors)]
#             for t in range(20):
#                 if not animation_running:
#                     led_rgb.off()
#                     return
#                 r = c1[0] + (c2[0]-c1[0])*t/20
#                 g = c1[1] + (c2[1]-c1[1])*t/20
#                 b = c1[2] + (c2[2]-c1[2])*t/20
#                 led_rgb.color = (r, g, b)
#                 time.sleep(0.05)
#
# def start_rgb_animation():
#     t = threading.Thread(target=smooth_rgb_animation)
#     t.start()
#     return t
#
# def stop_rgb_animation(thread):
#     global animation_running
#     animation_running = False
#     thread.join(timeout=1)
#     led_rgb.off()
#
# # === ERREUR CLIGNOTEMENT ===
# def blink_error(color, times):
#     led_rgb.color = color
#     for _ in range(times):
#         led_rgb.on()
#         time.sleep(0.3)
#         led_rgb.off()
#         time.sleep(0.3)
#
# # === APPEL API ===
# def get_tempo_colors():
#     headers = {"Authorization": API_KEY, "Accept": "application/json"}
#     try:
#         r = requests.get(API_URL, headers=headers, timeout=10)
#         if r.status_code == 200:
#             data = r.json()
#             today = data.get("today", {}).get("value")
#             tomorrow = data.get("tomorrow", {}).get("value")
#             return today, tomorrow
#         elif r.status_code == 401:
#             blink_error((0, 0, 1), 1)  # bleu 1 clignotement
#         elif r.status_code == 403:
#             blink_error((0, 0, 1), 2)  # bleu 2 clignotements
#         elif r.status_code == 404:
#             blink_error((0, 0, 1), 3)
#         else:
#             blink_error((0, 0, 1), 4)
#     except requests.exceptions.RequestException:
#         blink_error((1, 0, 0), 3)  # rouge = problème réseau
#     return None, None
#
# # === LOGIQUE PRINCIPALE ===
# def update_leds():
#     today, tomorrow = get_tempo_colors()
#
#     if today in leds_today:
#         set_color_group(leds_today, today)
#     elif today is None:
#         blink_error((1, 0, 0), 1)  # null
#     elif today == "UNKNOWN":
#         blink_error((1, 0, 0), 2)
#     else:
#         blink_error((1, 0, 0), 3)
#
#     if tomorrow in leds_tomorrow:
#         set_color_group(leds_tomorrow, tomorrow)
#     elif tomorrow is None:
#         blink_error((1, 0, 0), 1)
#     elif tomorrow == "UNKNOWN":
#         blink_error((1, 0, 0), 2)
#     else:
#         blink_error((1, 0, 0), 3)
#
#
# # === PROGRAMME PRINCIPAL ===
# if __name__ == "__main__":
#     while True:
#         now = datetime.now()
#
#         # Entre 6h et 11h22 → animation d’attente
#         if 6 <= now.hour < 11 or (now.hour == 11 and now.minute < 22):
#             thread = start_rgb_animation()
#             print("[INFO] Attente jusqu’à 11h22…")
#             while True:
#                 now = datetime.now()
#                 if now.hour == 11 and now.minute >= 22:
#                     break
#                 time.sleep(30)
#             stop_rgb_animation(thread)
#
#         # Tentative de mise à jour
#         update_leds()
#         print("[INFO] LEDs mises à jour à", datetime.now().strftime("%H:%M"))
#
#         # Attendre 1h avant de réessayer
#         time.sleep(3600)
