import requests
from bs4 import BeautifulSoup

# Crear sesión para manejar cookies automáticamente
session = requests.Session()

# URL del login y de la cuenta
LOGIN_URL = "https://muarrakis.com/login/"
MY_ACCOUNT_URL = "https://muarrakis.com/usercp/myaccount"

# Datos del formulario (ajusta con tu usuario y contraseña)
payload = {
    "webengineLogin_user": "anxiousmov",  # Reemplázalo con tu usuario real
    "webengineLogin_pwd": "15441109",  # Reemplázalo con tu contraseña real
    "webengineLogin_submit": "submit",
}

# Encabezados HTTP (simulan un navegador real)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Referer": "https://muarrakis.com/login/",
    "Origin": "https://muarrakis.com",
    "Content-Type": "application/x-www-form-urlencoded",
}

# 1️⃣ Enviar la solicitud de login
response = session.post(LOGIN_URL, data=payload, headers=headers)

# 2️⃣ Verificar si el login fue exitoso
if "logout" in response.text.lower() or "dashboard" in response.text.lower():
    print("✅ Inicio de sesión exitoso")

    # 3️⃣ Acceder a la página "My Account"
    response = session.get(MY_ACCOUNT_URL, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    # 4️⃣ Buscar todos los personajes dentro de `col-xs-3`
    characters = soup.find_all(class_="col-xs-3")

    for character in characters:
        name = character.find(class_="myaccount-character-name")
        location = character.find(class_="myaccount-character-block-location")
        level = character.find(class_="myaccount-character-block-level")

        name_text = name.text.strip() if name else "N/A"
        location_text = location.text.strip() if location else "N/A"
        level_text = level.text.strip() if level else "N/A"

        print(f"🛡️ Personaje: {name_text}")
        print(f"📍 Ubicación: {location_text}")
        print(f"🎚️ Nivel: {level_text}")
        print("-" * 30)

else:
    print("❌ Error en el inicio de sesión")
    print(response.text[:500])  # Muestra un fragmento de la respuesta para depuración
