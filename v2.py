import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import requests
from datetime import datetime, timedelta
import os
import json


# Definição da classe WeatherApp, que é uma janela de aplicativo PyQt5
class WeatherApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Metereologia')  # Define o título da janela
        self.setGeometry(100, 100, 600, 300)  # Define a posição e o tamanho da janela

        # Criação dos widgets (elementos visuais)
        self.city_line_edit = QLineEdit()  # Caixa de texto para inserir o nome da cidade
        self.city_line_edit.setPlaceholderText(
            "Digite o nome da cidade")  # Define um texto de orientação dentro da caixa de texto

        self.update_button = QPushButton('Atualizar')  # Botão para atualizar os dados do tempo
        self.update_button.clicked.connect(
            self.update_weather_data)  # Conecta o clique do botão a um método para atualizar os dados do tempo

        self.temp_label = QLabel()  # Rótulo para exibir a temperatura
        self.humidity_label = QLabel()  # Rótulo para exibir a umidade
        self.wind_speed_label = QLabel()  # Rótulo para exibir a velocidade do vento
        self.weather_icon_label = QLabel()  # Rótulo para exibir o ícone do tempo
        self.weather_icon_label.setFixedSize(100, 100)  # Define o tamanho fixo para o rótulo do ícone do tempo

        self.alerts_label = QLabel()  # Rótulo para exibir alertas meteorológicos
        self.history_label = QLabel()  # Rótulo para exibir o histórico do tempo

        # Layout principal da janela
        layout = QVBoxLayout()
        layout.addWidget(self.city_line_edit)

        # Layout para o botão de atualização
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.update_button)
        button_layout.addStretch(1)

        layout.addLayout(button_layout)

        # Layout para exibir informações do clima e o ícone do tempo
        info_layout = QHBoxLayout()
        info_layout.addWidget(self.temp_label)
        info_layout.addWidget(self.humidity_label)
        info_layout.addWidget(self.wind_speed_label)
        info_layout.addStretch(1)
        info_layout.addWidget(self.weather_icon_label, alignment=Qt.AlignRight | Qt.AlignTop)  # Alinha o ícone do tempo

        layout.addLayout(info_layout)
        layout.addWidget(self.alerts_label)
        layout.addWidget(self.history_label)
        self.setLayout(layout)

    # Método para atualizar os dados do tempo quando o botão de atualização é clicado
    def update_weather_data(self):
        city = self.city_line_edit.text()  # Obtém o nome da cidade inserido pelo usuário na caixa de texto
        if not city:
            QMessageBox.warning(self, "Erro",
                                "Por favor, digite o nome da cidade.")  # Exibe uma mensagem de aviso se o campo de texto estiver vazio
            return

        data = self.get_weather_data(city)  # Obtém os dados do tempo da API com base no nome da cidade
        if not data:
            QMessageBox.warning(self, "Erro",
                                "Não foi possível obter dados para esta cidade. Verifique se o nome está correto.")  # Exibe uma mensagem de aviso se não foi possível obter os dados do tempo
            return

        # Extrai informações relevantes dos dados do tempo recebidos da API
        temp_kelvin = data['main']['temp']
        temp_celsius, temp_fahrenheit = self.kelvin_to_celsius_and_fahrenheit(temp_kelvin)
        humidity = data['main']['humidity']
        wind_speed = data['wind']['speed']
        weather_icon = data['weather'][0]['icon']

        # Atualiza os rótulos com as informações do tempo
        self.temp_label.setText(f"Temperatura: {round(temp_celsius)}°C")
        self.humidity_label.setText(f"Humidade: {humidity}%")
        self.wind_speed_label.setText(f"Velocidade do Vento: {wind_speed} m/s")

        # Obtém e exibe o ícone do tempo
        response = requests.get(f"http://openweathermap.org/img/wn/{weather_icon}.png")
        weather_icon_data = response.content
        pixmap = QPixmap()
        pixmap.loadFromData(weather_icon_data)
        self.weather_icon_label.setPixmap(pixmap)
        self.weather_icon_label.setScaledContents(True)

        # Verifica as condições meteorológicas e exibe alertas, se necessário
        alerts = self.check_weather_conditions(data)
        alerts_text = ""
        for alert, color in alerts:
            alerts_text += f"<font color={color}>{alert}</font><br>"
        self.alerts_label.setText(alerts_text)

        # Salva os dados do tempo em um arquivo e exibe o histórico do tempo
        self.save_weather_data(city, data)
        self.display_weather_history(city)

    # Função para obter as cordenadas da Cidade.
    def get_cords(self, city):
        url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=10&language=pt&format=json"
        try:
            data = requests.get(url).json()
            print(data["results"][0]["latitude"], data["results"][0]["longitude"])
            return data["results"][0]["latitude"], data["results"][0]["longitude"]
        except Exception as e:
            print(f"Erro ao obter coordenadas: {e}")
            return None

    # Método para obter os dados do tempo da API com base no nome da cidade
    def get_weather_data(self, city):
        latitude, longitude = self.get_cords(city)
        url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,relative_humidity_2m,precipitation,rain,wind_speed_10m,wind_direction_10m&hourly=temperature_2m,relative_humidity_2m,precipitation_probability,precipitation,rain,cloud_cover,wind_speed_10m,wind_direction_10m&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,rain_sum,precipitation_hours,precipitation_probability_max,wind_speed_10m_max&timezone=Europe%2FLondon"
        try:
            data = requests.get(url).json()
            print(data)
            return data
        except Exception as e:
            print(f"Erro ao obter dados: {e}")
            return None

    # Método para converter a temperatura de Kelvin para Celsius e Fahrenheit
    def kelvin_to_celsius_and_fahrenheit(self, kelvin):
        celsius = kelvin - 273.15
        fahrenheit = celsius * (9 / 5) + 32
        return celsius, fahrenheit

    # Método para verificar as condições meteorológicas e gerar alertas, se necessário
    def check_weather_conditions(self, data):
        alerts = []
        temperature = data['main']['temp'] - 273.15
        humidity = data['main']['humidity']
        wind_speed = data['wind']['speed']

        if temperature > 30:
            alerts.append(("Temperatura alta", "red"))
        if 30 > temperature >= 20:
            alerts.append(("Temperatura normal", "yellow"))
        if temperature < 20:
            alerts.append(("Temperatura baixa", "blue"))

        if humidity > 30:
            alerts.append(("Humidade Alta", "blue"))
        if humidity < 30:
            alerts.append(("Humidade baixa", "gray"))

        if wind_speed > 15:
            alerts.append(("Velocidade do vento alta", "red"))

        return alerts

    # Método para salvar os dados do tempo em um arquivo JSON
    def save_weather_data(self, city, data):
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')  # Obtém o timestamp atual
        data['city'] = city  # Adiciona o nome da cidade aos dados do tempo
        base_directory = os.path.join(os.getcwd(), 'citys')  # Diretório base para salvar os dados do tempo
        city_directory = os.path.join(base_directory, city)  # Diretório específico para a cidade
        if not os.path.exists(city_directory):  # Cria o diretório da cidade se não existir
            os.makedirs(city_directory)
        filename = os.path.join(city_directory, f"weather_{timestamp}.json")  # Caminho completo para o arquivo de dados do tempo
        with open(filename, 'w') as file:  # Abre o arquivo para escrita
            json.dump(data, file)  # Salva os dados do tempo no arquivo JSON

    # Método para exibir o histórico do tempo para uma cidade específica
    def display_weather_history(self, city):
        now = datetime.now()  # Obtém a data e hora atuais
        past_week = now - timedelta(days=7)  # Obtém a data e hora há uma semana atrás
        history_text = "<h3>Histórico dos últimos 7 dias:</h3>"  # Título para o histórico do tempo
        base_directory = os.path.join(os.getcwd(), 'citys')  # Diretório base onde os dados do tempo são salvos
        city_directory = os.path.join(base_directory, city)  # Diretório específico para a cidade
        if not os.path.exists(city_directory):  # Verifica se há dados para a cidade
            self.history_label.setText(history_text + "<p>Nenhum dado disponível.</p>")  # Exibe uma mensagem se não houver dados
            return

        daily_data = {}  # Dicionário para armazenar os dados diários do tempo
        for filename in sorted(os.listdir(city_directory)):  # Itera sobre os arquivos na pasta da cidade
            if filename.startswith('weather_') and filename.endswith('.json'):  # Verifica se o arquivo contém dados do tempo
                timestamp_str = filename[len('weather_'):-len('.json')]  # Extrai o timestamp do nome do arquivo
                timestamp = datetime.strptime(timestamp_str, '%Y%m%d%H%M%S')  # Converte o timestamp de string para objeto datetime
                if past_week <= timestamp <= now:  # Verifica se o timestamp está dentro da última semana
                    date_str = timestamp.strftime('%Y-%m-%d')  # Converte o timestamp para uma string de data
                    if date_str not in daily_data or daily_data[date_str]['timestamp'] < timestamp:  # Verifica se os dados já foram registrados para este dia
                        with open(os.path.join(city_directory, filename), 'r') as file:  # Abre o arquivo JSON
                            data = json.load(file)  # Carrega os dados do arquivo
                            daily_data[date_str] = {  # Adiciona os dados diários ao dicionário
                                'timestamp': timestamp,  # Armazena o timestamp
                                'data': data  # Armazena os dados do tempo
                            }

        # Filtra os dados climáticos antes de exibir o histórico
        filtered_daily_data = self.filter_weather_data([daily_data[date]['data'] for date in daily_data])

        for date_str in sorted(daily_data.keys(), reverse=True):  # Itera sobre as datas em ordem decrescente
            data = daily_data[date_str]['data']  # Obtém os dados do tempo para a data atual
            timestamp = daily_data[date_str]['timestamp']  # Obtém o timestamp para a data atual
            temp_kelvin = data['main']['temp']  # Obtém a temperatura em Kelvin
            temp_celsius, _ = self.kelvin_to_celsius_and_fahrenheit(temp_kelvin)  # Converte a temperatura de Kelvin para Celsius
            # Adiciona as informações do tempo ao texto do histórico
            history_text += f"<p>{timestamp.strftime('%d/%m/%Y %H:%M:%S')}: {round(temp_celsius)}°C, {data['main']['humidity']}% humidade, {data['wind']['speed']} m/s vento</p>"

        self.history_label.setText(history_text)  # Define o texto do histórico na label

    # Método para filtrar os dados do tempo
    def filter_weather_data(self, data_list):
        filtered_data = []  # Lista para armazenar os dados filtrados
        prev_temp = None  # Variável para armazenar a temperatura anterior
        for data in data_list:
            temp_kelvin = data['main']['temp']  # Obtém a temperatura em Kelvin
            temp_celsius, _ = self.kelvin_to_celsius_and_fahrenheit(temp_kelvin)  # Converte a temperatura de Kelvin para Celsius
            # Verifica se a temperatura é significativamente diferente da temperatura anterior
            if prev_temp is None or abs(temp_celsius - prev_temp) >= 2:
                filtered_data.append(data)  # Adiciona os dados à lista filtrada
                prev_temp = temp_celsius  # Atualiza a temperatura anterior
        return filtered_data  # Retorna os dados filtrados

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Aplicar tema escuro
    dark_stylesheet = """
    QWidget {
        background-color: #2E2E2E;
        color: #F0F0F0;
    }
    QLineEdit {
        background-color: #3E3E3E;
        color: #F0F0F0;
        border: 1px solid #F0F0F0;
    }
    QPushButton {
        background-color: #4E4E4E;
        color: #F0F0F0;
        border: 1px solid #F0F0F0;
    }
    QLabel {
        color: #F0F0F0;
    }
    QMessageBox {
        background-color: #3E3E3E;
        color: #F0F0F0;
    }
    """
    app.setStyleSheet(dark_stylesheet)

    ex = WeatherApp()
    ex.show()
    sys.exit(app.exec_())


