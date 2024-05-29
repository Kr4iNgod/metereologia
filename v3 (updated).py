from customtkinter import *
import requests
from datetime import datetime, timedelta
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Caminho do ícone
icon_path = "icone.ico"
logo_path = "icone.png"

app = CTk()
app.geometry("1200x600")
set_appearance_mode("dark")
app.title("Meteorologia")
app.iconbitmap(icon_path) # Adiciona um ícone à janela

# Variáveis globais para o alerta e dados climáticos
invalid_city = None
weather_data = None
frames = []  # Lista para armazenar os frames dos dias

# Funções
def get_cords(city):
    global invalid_city
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=10&language=pt&format=json"
    try:
        data = requests.get(url).json()
        print(data["results"][0]["latitude"], data["results"][0]["longitude"])
        # Remover alerta se a cidade for válida
        if invalid_city is not None:
            invalid_city.destroy()
            invalid_city = None
        return data["results"][0]["latitude"], data["results"][0]["longitude"]
    except Exception as e:
        print(f"Erro ao obter coordenadas: {e}")
        # Mostrar alerta de cidade inválida
        if invalid_city is None:
            invalid_city = CTkLabel(master=app, text="Cidade Inválida", text_color="red")
            invalid_city.place(relx=0.92, rely=0.12, anchor="ne")
        return None, None

def get_weather_data():
    global weather_data
    city = city_entry.get()
    latitude, longitude = get_cords(city)
    if latitude is not None and longitude is not None:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,relative_humidity_2m,precipitation,rain,wind_speed_10m,wind_direction_10m&hourly=temperature_2m,relative_humidity_2m,precipitation_probability,precipitation,rain,cloud_cover,wind_speed_10m,wind_direction_10m&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,rain_sum,precipitation_hours,precipitation_probability_max,wind_speed_10m_max&timezone=Europe%2FLondon"
        try:
            weather_data = requests.get(url).json()
            display_weather_data(weather_data)

            # Verificação de desastres naturais
            alerts = check_for_disasters(weather_data)
            if alerts:
                display_alerts(alerts, city)

        except Exception as e:
            print(f"Erro ao obter dados: {e}")
    else:
        print("Não foi possível obter as coordenadas. Por favor verifique o nome da cidade.")

def display_weather_data(data):
    global frames
    daily_data = data['daily']
    days_of_week = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
    today = datetime.now()

    # Encontra o índice do dia atual na lista de dias da semana
    current_day_index = today.weekday()

    # Remove qualquer frame existente antes de criar novos
    for frame in frames:
        frame.destroy()
    frames = []

    for i in range(7):
        # Calcula o índice do dia a ser exibido (começando do dia atual)
        display_day_index = (current_day_index + i) % 7
        day = today + timedelta(days=i)
        day_name = days_of_week[display_day_index]
        day_date = day.strftime("%d")

        day_frame = CTkFrame(master=app, width=100, height=150, corner_radius=15)
        day_frame.place(relx=0.1 + i * 0.13, rely=0.55, anchor="center")  # Ajustado para estar no meio do aplicativo
        frames.append(day_frame)

        day_label = CTkLabel(master=day_frame, text=f"{day_name}, dia {day_date}")
        day_label.pack(pady=5)

        temp_max_label = CTkLabel(master=day_frame, text=f"Max: {daily_data['temperature_2m_max'][i]}°C")
        temp_max_label.pack(pady=5)

        temp_min_label = CTkLabel(master=day_frame, text=f"Min: {daily_data['temperature_2m_min'][i]}°C")
        temp_min_label.pack(pady=5)

        precipitation_label = CTkLabel(master=day_frame, text=f"Precipitação: {daily_data['precipitation_sum'][i]} mm")
        precipitation_label.pack(pady=5)

        # Adiciona botão para ver gráficos
        graph_button = CTkButton(master=day_frame, text="Ver Gráficos", command=lambda day_name=day_name, index=i: show_graphs(day_name, index))
        graph_button.pack(pady=5)


def show_graphs(day, index):
    global weather_data
    hourly_data = weather_data['hourly']
    temperatures = hourly_data['temperature_2m'][index*24:(index+1)*24]
    windspeed = hourly_data['wind_speed_10m'][index*24:(index+1)*24]
    precipitation = hourly_data['precipitation'][index*24:(index+1)*24]
    humidity = hourly_data['relative_humidity_2m'][index*24:(index+1)*24]

    # Cria uma nova janela para os gráficos
    graph_window = CTkToplevel(app)
    graph_window.geometry("1000x600")
    graph_window.title(f"Gráficos para {day}")

    # Traz a nova janela para frente
    graph_window.focus_force()
    graph_window.grab_set()

    # Plota o gráfico de temperatura
    plt.subplot(221)
    plt.plot(range(24), temperatures, color='red')
    plt.xlabel('Hora do Dia')
    plt.ylabel('Temperatura (°C)')
    plt.title('Variação da Temperatura ao Longo do Dia')

    # Plota o gráfico de velocidade do vento
    plt.subplot(222)
    plt.plot(range(24), windspeed, color='blue')
    plt.xlabel('Hora do Dia')
    plt.ylabel('Velocidade do Vento (km/h)')
    plt.title('Variação da Velocidade do Vento ao Longo do Dia')

    # Plota o gráfico de precipitação
    plt.subplot(223)
    plt.plot(range(24), precipitation, color='green')
    plt.xlabel('Hora do Dia')
    plt.ylabel('Precipitação (mm)')
    plt.title('Variação da Precipitação ao Longo do Dia')

    # Plota o gráfico de umidade
    plt.subplot(224)
    plt.plot(range(24), humidity, color='orange')
    plt.xlabel('Hora do Dia')
    plt.ylabel('Umidade (%)')
    plt.title('Variação da Umidade ao Longo do Dia')

    plt.tight_layout()  # Ajusta automaticamente o layout para evitar sobreposição

    # Converte a figura em um widget que pode ser adicionado ao tkinter
    canvas = FigureCanvasTkAgg(plt.gcf(), master=graph_window)
    canvas.draw()
    canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)

    # Fecha a janela de gráficos ao clicar no botão "Voltar"
    def close_window():
        graph_window.destroy()


def check_for_disasters(weather_data):
    alerts = []
    hourly_data = weather_data['hourly']

    # Definição das condições de furacão
    hurricane_conditions = {
        "wind_speed": 119,  # km/h
        "pressure": 980  # hPa (não disponível na API, mas poderia ser usado se disponível)
    }

    # Definição das condições de tornado
    tornado_conditions = {
        "wind_speed": 150  # km/h (aproximado)
    }

    # Definição das condições de inundação
    flood_conditions = {
        "precipitation": 50  # mm/h (aproximado)
    }

    # Verificação das condições a cada hora
    for i in range(len(hourly_data['time'])):
        wind_speed = hourly_data['wind_speed_10m'][i]
        precipitation = hourly_data['precipitation'][i]

        # Verificação de furacão
        if wind_speed >= hurricane_conditions['wind_speed']:
            alerts.append(f"Alerta de Furacão! Velocidade do vento: {wind_speed} km/h")

        # Verificação de tornado
        if wind_speed >= tornado_conditions['wind_speed']:
            alerts.append(f"Alerta de Tornado! Velocidade do vento: {wind_speed} km/h")

        # Verificação de inundação
        if precipitation >= flood_conditions['precipitation']:
            alerts.append(f"Alerta de Inundação! Precipitação: {precipitation} mm/h")

    return alerts

def display_alerts(alerts, city):
    alert_window = CTk()
    alert_window.geometry("400x200")
    alert_window.title(f"Alertas de Desastres Naturais para {city}")

    for alert in alerts:
        alert_label = CTkLabel(master=alert_window, text=alert, text_color="red")
        alert_label.pack(pady=10)

    close_button = CTkButton(master=alert_window, text="Fechar", command=alert_window.destroy)
    close_button.pack(pady=10)

    alert_window.mainloop()

# Design

# Adiciona o texto "Meteorologia"
title_label = CTkLabel(master=app, text="Meteorologia", font=("Arial", 24))
title_label.place(anchor="nw", relx=0.05, rely=0.02)

# Carrega a imagem
image = Image.open(logo_path)
image = image.resize((100, 100), Image.LANCZOS)  # Usando LANCZOS para redimensionar
photo_image = CTkImage(image)
image_label = CTkLabel(master=app, image=photo_image, text="")
image_label.place(anchor="nw", relx=0.02, rely=0.02)

# Cria a caixa de texto para colocar a cidade
city_entry = CTkEntry(master=app, placeholder_text="Introduza a Cidade", width=170)
city_entry.place(anchor="ne", relx=0.97, rely=0.02)  # Coloca a caixa de texto no canto superior direito

# Cria um botão para executar a função de get_weather_data com a cor azul do Windows e cor de texto branca
check_button = CTkButton(master=app, text="Verificar", command=get_weather_data, corner_radius=32, fg_color="#0078D7", hover_color="#005A9E", text_color="white")
check_button.place(anchor="ne", relx=0.95, rely=0.07)  # Coloca o botão no canto superior direito

app.mainloop()
