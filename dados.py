import requests
import json
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QGridLayout
from PyQt5.QtGui import QPixmap
import requests
from PIL import Image
from io import BytesIO

BASE_URL = "http://api.openweathermap.org/data/2.5/weather?"
API_KEY = "f2ff9922e8c2c8b3d2819fef43c1a9c5"
CITY = "Lisbon"

def get_weather_data(API_KEY, CITY):
    url = f"{BASE_URL}q={CITY}&appid={API_KEY}"
    data = requests.get(url).json()
    return data

def kevin_to_celsius_and_fahreneit(kelvin):
    celsius = kelvin - 273.15
    fahrenheit = celsius * (9/5) + 32
    return celsius, fahrenheit

data = get_weather_data(API_KEY, CITY)
print(data)

# Defina o limite para variação de temperatura, humidade e velocidade do vento
temp_threshold = 5 # em graus Celsius
humidity_threshold = 10 # em percentagem
wind_speed_threshold = 10 # em m/s

def detect_temperature_variation(data, threshold):
    temperature_celsius, temperature_fahreneit = kevin_to_celsius_and_fahreneit(data['main']['temp'])
    
    # Verifica se a variação é maior que o limiar
    if abs(temperature_celsius) > threshold:
        return True, temperature_celsius
    else:
        return False, None

def detect_humidity_variation(data, threshold):
    humidity = data['main']['humidity']
    
    # Verifica se a variação é maior que o limiar
    if abs(humidity) > threshold:
        return True, humidity
    else:
        return False, None

def detect_wind_speed_variation(data, threshold):
    wind_speed = data['wind']['speed']
    
    # Verifica se a variação é maior que o limiar
    if abs(wind_speed) > threshold:
        return True, wind_speed
    else:
        return False, None

# Obter os dados climáticos
data = get_weather_data(API_KEY, CITY)

# Detetar variações abruptas na temperatura
abrupt_temp_change, temp = detect_temperature_variation(data, temp_threshold)
if abrupt_temp_change:
    print("Alerta: Variação abrupta na temperatura detectada!")
    print(f"Temperatura atual: {round(temp)}°C")
else:
    print("Nenhuma variação abrupta na temperatura detectada.")

# Detetar mudanças rápidas na humidade
rapid_humidity_change, humidity = detect_humidity_variation(data, humidity_threshold)
if rapid_humidity_change:
    print("Alerta: Mudança rápida na humidade detectada!")
    print("Humidade atual:", humidity)
else:
    print("Nenhuma mudança rápida na humidade detectada.")

# Detetar mudanças rápidas na velocidade do vento
rapid_wind_speed_change, wind_speed = detect_wind_speed_variation(data, wind_speed_threshold)
if rapid_wind_speed_change:
    print("Alerta: Mudança rápida na velocidade do vento detectada!")
    print("Velocidade do vento atual:", wind_speed)
else:
    print("Nenhuma mudança rápida na velocidade do vento detectada.")


def check_weather_conditions(data):
    alerts = []
    # Verificar condições meteorológicas e adicionar alertas conforme necessário
    temperature = data['main']['temp']
    humidity = data['main']['humidity']
    wind_speed = data['wind']['speed']

    # Exemplo: alerta para temperatura alta
    if temperature > 30:
        alerts.append(("Temperatura muito alta", "red"))
    # Exemplo: alerta para humidade baixa
    if humidity < 30:
        alerts.append(("Humidade baixa", "yellow"))
    # Exemplo: alerta para velocidade do vento alta
    if wind_speed > 15:
        alerts.append(("Velocidade do vento alta", "red"))

    return alerts

class WeatherApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Obter os dados climáticos
        data = get_weather_data(API_KEY, CITY)
        temp_kelvin = data['main']['temp']
        temp_celsius, temp_fahreneit = kevin_to_celsius_and_fahreneit(temp_kelvin)
        humidity = data['main']['humidity']
        wind_speed = data['wind']['speed']
        weather_icon = data['weather'][0]['icon']

        # Verificar as condições meteorológicas para alertas
        alerts = check_weather_conditions(data)

        # Criar widgets para exibir os dados climáticos
        temp_label = QLabel(f"Temperatura: {round(temp_celsius)}°C")
        humidity_label = QLabel(f"Humidade: {humidity}%")
        wind_speed_label = QLabel(f"Velocidade do Vento: {wind_speed} m/s")

        # Criar label para exibir os alertas
        alerts_label = QLabel()
        alerts_text = ""
        for alert, color in alerts:
            alerts_text += f"<font color={color}>{alert}</font><br>"
        alerts_label.setText(alerts_text)

        # Carregar o ícone do tempo previsto em uma imagem
        response = requests.get(f"http://openweathermap.org/img/wn/{weather_icon}.png")
        img = Image.open(BytesIO(response.content))
        img_path = "weather_icon.png"
        img.save(img_path)

        weather_icon_label = QLabel()
        weather_icon_pixmap = QPixmap(img_path).scaled(100, 100)  # Redimensionar a imagem
        weather_icon_label.setPixmap(weather_icon_pixmap)

        # Criar layout grid para organizar os widgets
        grid_layout = QGridLayout()
        grid_layout.addWidget(temp_label, 0, 0)
        grid_layout.addWidget(humidity_label, 1, 0)
        grid_layout.addWidget(wind_speed_label, 2, 0)
        grid_layout.addWidget(weather_icon_label, 0, 1, 3, 1)  # Posicionar a imagem na coluna 1, ocupando 3 linhas
        grid_layout.addWidget(alerts_label, 0, 2, 3, 1)  # Posicionar os alertas na coluna 2, ocupando 3 linhas

        self.setLayout(grid_layout)

        self.setWindowTitle('Weather App')
        self.setGeometry(100, 100, 500, 200)  # Aumentar a largura da janela para acomodar os alertas
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = WeatherApp()
    sys.exit(app.exec_())
     
'''
f = open("data.json", "w")

caminho_arquivo = "C:/Python/Projeto Lab II/data.json"

try:
    with open(caminho_arquivo, "w") as f:
        f.write(json.dumps(data))
        print("Arquivo criado com sucesso!")
except Exception as e:
    print("Erro ao criar o arquivo:", e)

f.close()
'''