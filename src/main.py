from time import sleep
import requests, threading, time, json, os
from datetime import datetime, timedelta
from gpiozero import LED, RGBLED

# === TEST DES LEDS ===

# GPIO affectation
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
led_rgb = RGBLED(red=22, green=27, blue=17, active_high=False)

print("=== Test des LEDs ===")
print("Chaque LED va s’allumer à tour de rôle...")

try:
    led_rgb.off()
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


# === CONFIGURATION ===
# API_URL = "https://digital.iservices.rte-france.com/open_api/tempo_like_supply_contract/v1/sandbox/tempo_like_calendars"
# API_KEY = "TaCléAPI"
API_TODAY = "https://www.api-couleur-tempo.fr/api/jourTempo/today"
API_TOMORROW = "https://www.api-couleur-tempo.fr/api/jourTempo/tomorrow"
CACHE_FILE = "/home/aurel/tempo_colors.json"
animation_running = False


# === UTILS ===
def set_color_group(group, color):
    for led in group.values():
        led.off()
    color = color.upper()
    if color in group:
        group[color].on()

# === RGB ANIMATION ===
animation_running = False

def smooth_rgb_animation():
    global animation_running
    animation_running = True
    colors = [(1,0,0),(1,1,0),(0,1,0),(0,1,1),(0,0,1),(1,0,1)]
    try:
        while animation_running:
            for i in range(len(colors)):
                c1, c2 = colors[i], colors[(i+1)%len(colors)]
                for t in range(20):
                    if not animation_running:
                        led_rgb.off()
                        return
                    r = c1[0] + (c2[0]-c1[0])*t/20
                    g = c1[1] + (c2[1]-c1[1])*t/20
                    b = c1[2] + (c2[2]-c1[2])*t/20
                    led_rgb.color = (r,g,b)
                    time.sleep(0.05)
    except Exception as e:
        print(f"[ERREUR] Animation RGB interrompue : {e}")
        led_rgb.off()
        animation_running = False

def start_rgb_animation():
    t = threading.Thread(target=smooth_rgb_animation)
    t.start()
    return t

def stop_rgb_animation(t):
    global animation_running
    animation_running = False
    t.join(timeout=1)
    led_rgb.off()

# === ERREUR ===
def blink_error(color, times):
    for _ in range(times):
        led_rgb.color = color
        time.sleep(0.3)
        led_rgb.off()
        time.sleep(0.3)

# === CACHE LOCAL ===
def load_cached_colors():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                data = json.load(f)
            if data.get("date") == datetime.now().strftime("%Y-%m-%d"):
                return data.get("today"), data.get("tomorrow")
            elif data.get("date") == (datetime.now() + timedelta(days=-1)).strftime("%Y-%m-%d") and datetime.now().hour > 6:
                return data.get("tomorrow"), None
        except Exception:
            pass
    return None, None

def save_cached_colors(today, tomorrow):
    try:
        with open(CACHE_FILE, "w") as f:
            json.dump({
                "date": datetime.now().strftime("%Y-%m-%d"),
                "today": today,
                "tomorrow": tomorrow
            }, f)
    except Exception as e:
        print(f"[WARN] Impossible de sauvegarder le cache : {e}")

# === FONCTION APPEL API ===
def get_tempo_colors():
    """Ne contacte l’API que si la donnée est manquante ou ancienne."""
    today, tomorrow = load_cached_colors()

    # Si on est passé à un nouveau jour → "demain" devient "aujourd'hui"
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            data = json.load(f)
        if data.get("date") == (datetime.now() + timedelta(days=-1)).strftime("%Y-%m-%d") and datetime.now().hour > 6:
            print("[INFO] Nouveau jour détecté → transfert de la couleur de demain vers aujourd’hui")
            save_cached_colors(today, tomorrow)
        elif data.get("date") != datetime.now().strftime("%Y-%m-%d") :
            today, tomorrow = None, None
        return today, tomorrow

    # Si la couleur du jour manque → on la cherche
    if not today:
        print("[INFO] Récupération de la couleur d’aujourd’hui depuis l’API")
        today = get_color_from_api(API_TODAY)
        save_cached_colors(today, tomorrow)

    # Si la couleur de demain manque → on la cherche
    if not tomorrow:
        print("[INFO] Récupération de la couleur de demain depuis l’API")
        tomorrow = get_color_from_api(API_TOMORROW)
        save_cached_colors(today, tomorrow)

    return today, tomorrow

def get_color_from_api(url):
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            code = data.get("codeJour")
            lib = data.get("libCouleur", "").upper()
            if code == 0:
                return "INCONNU"
            return lib
        else:
            print(f"[WARN] Erreur HTTP {r.status_code} sur {url}")
            return None
    except requests.exceptions.RequestException:
        print(f"[WARN] Problème réseau sur {url}")
        return None

# === LOGIQUE PRINCIPALE ===
def update_leds():
    today, tomorrow = get_tempo_colors()

    # Gestion de la LED du jour
    if today in leds_today:
        set_color_group(leds_today, today)
    elif today == "INCONNU":
        blink_error((1, 0, 0), 1)
    else:
        blink_error((1, 0, 0), 3)

    # Gestion de la LED du lendemain
    if tomorrow in leds_tomorrow:
        set_color_group(leds_tomorrow, tomorrow)
    elif tomorrow == "INCONNU":
        blink_error((0, 0, 1), 1)
    else:
        blink_error((0, 0, 1), 3)

    return today, tomorrow

# === PROGRAMME PRINCIPAL ===
if __name__ == "__main__":
    today, tomorrow = update_leds()

    try:
        while True:
            now = datetime.now()
            # Animation entre 6h et 11h22
            if 6 <= now.hour < 11 or (now.hour == 11 and now.minute < 22):
                try:
                    today, tomorrow = update_leds()
                    thread = start_rgb_animation()
                    print("[INFO] Attente jusqu’à 11h22…")
                    while True:
                        now = datetime.now()
                        if now.hour == 11 and now.minute >= 22:
                            break
                        time.sleep(60)
                    stop_rgb_animation(thread)

                    today, tomorrow = update_leds()
                    print("[INFO] LEDs mises à jour à", datetime.now().strftime("%H:%M"))
                except Exception as e:
                    print(f"[ERREUR] Attente interrompue : {e}")

            while today is None and tomorrow is None:
                # Mise à jour
                # Pause 1h avant nouvelle tentative
                time.sleep(3600)

                today, tomorrow = update_leds()
                print("[INFO] LEDs mises à jour à", datetime.now().strftime("%H:%M"))

            time.sleep(60)
    except Exception as e:
        print(f"[WARN] Erreur while : {e}")