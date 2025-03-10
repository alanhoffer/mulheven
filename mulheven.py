import ctypes
import time
import random
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from pystray import Icon, MenuItem, Menu
from PIL import Image, ImageDraw
import keyboard
import os
import sys

# Obtener la ruta al icono en el directorio del archivo ejecutable
icon_path = os.path.join(sys._MEIPASS, 'icon.ico') if getattr(sys, 'frozen', False) else 'icon.ico'


# Constantes de la API de Windows
KEYEVENTF_KEYDOWN = 0x0000  # Simula la pulsación de la tecla
KEYEVENTF_KEYUP = 0x0002    # Simula la liberación de la tecla
VK_RBUTTON = 0x02  # Código del botón derecho del mouse en Windows

# Variables globales
running_combo = False
running_r = False  # Iniciar con la 'R' desactivada por defecto
running_q = False 

# Función para obtener el estado de una tecla o botón del mouse
def is_key_pressed(vk_code):
    state = ctypes.windll.user32.GetAsyncKeyState(vk_code)
    print(f"Estado de la tecla {vk_code}: {'Presionado' if state & 0x8000 else 'No presionado'}")
    return state & 0x8000

# Función para generar un cooldown aleatorio
def get_random_cooldown(base_cooldown, variation):
    cooldown = random.randint(base_cooldown - variation, base_cooldown + variation)
    print(f"Cooldown generado: {cooldown} ms")
    return cooldown

# Función para simular la presión de una tecla
def press_key(key):
    key_code = ord(key.upper())
    print(f"Presionando la tecla: {key.upper()}")  # Mensaje en consola
    ctypes.windll.user32.keybd_event(key_code, 0, KEYEVENTF_KEYDOWN, 0)
    time.sleep(0.05)
    ctypes.windll.user32.keybd_event(key_code, 0, KEYEVENTF_KEYUP, 0)
    print(f"Tecla {key.upper()} liberada")

# Función que ejecuta la secuencia de teclas mientras se mantiene el clic derecho presionado
def press_combo_while_right_click(cooldown, cant_poderes):
    global running_combo
    print(f"Iniciando el combo con cooldown de {cooldown} ms y {cant_poderes} poderes...")  # Mensaje de inicio de combo
    while running_combo:
        if is_key_pressed(VK_RBUTTON):
            print("Botón derecho presionado, comenzando combo...")  # Mensaje en consola
            while is_key_pressed(VK_RBUTTON) and running_combo:
                for i in range(cant_poderes):
                    print(f"Presionando el poder {i+1}")
                    press_key(str(1 + i))
                    time.sleep(get_random_cooldown(cooldown, 10) / 1000)
        time.sleep(1)  # Pequeña pausa para evitar uso excesivo de CPU
        print("Esperando 200 ms antes de verificar el estado del botón derecho")

# Función que presiona la tecla 'R' cada 60 segundos
def auto_press_r():
    global running_r
    while running_r:
        print("Esperando para presionar 'R'...")  # Mensaje en consola
        time.sleep(get_random_cooldown(30000, 1000) / 1000)
        print("Presionando 'R'...")  # Mensaje en consola
        press_key('R')

# Función que presiona la tecla 'R' cada 60 segundos
def auto_press_q():
    global running_q
    while running_q:
        print("Esperando para presionar 'Q'...")  # Mensaje en consola
        time.sleep(get_random_cooldown(100, 50) / 1000)
        print("Presionando 'Q'...")  # Mensaje en consola
        press_key('Q')


# Función para iniciar/detener el combo
def toggle_combo():
    global running_combo
    if running_combo:
        running_combo = False
        print("Deteniendo el combo...")
        combo_button.config(text="Iniciar Combo")
    else:
        try:
            poderes = int(power_entry.get())
            cooldown = int(cooldown_entry.get())
            print(f"Configuración del combo: {poderes} poderes, cooldown de {cooldown} ms")
            if not (0 <= poderes <= 5):
                messagebox.showerror("Error", "La cantidad de poderes debe estar entre 0 y 5.")
                print("Error: La cantidad de poderes no está entre 0 y 5")
                return
            if cooldown < 50:
                messagebox.showerror("Error", "El cooldown debe ser de al menos 50 ms.")
                print("Error: El cooldown es menor de 50 ms")
                return
        except ValueError:
            messagebox.showerror("Error", "Ingrese valores numéricos válidos.")
            print("Error: Valores no numéricos ingresados")
            return
        
        running_combo = True
        print("Iniciando el hilo del combo...")
        threading.Thread(target=press_combo_while_right_click, args=(cooldown, poderes), daemon=True).start()
        combo_button.config(text="Detener Combo")

# Función para activar/desactivar la tecla 'R'
def toggle_r():
    global running_r
    if running_r:
        running_r = False
        print("Deteniendo la tecla 'R'...")
    else:
        running_r = True
        print("Activando la tecla 'R'...")
        # Iniciar el hilo de auto_press_r solo si no está corriendo
        threading.Thread(target=auto_press_r, daemon=True).start()
    state = "activada" if running_r else "desactivada"
    print(f"Tecla 'R' {state}.")


# Función para activar/desactivar la tecla 'R'
def toggle_q():
    global running_q
    if running_q:
        running_q = False
        print("Deteniendo la tecla 'Q'...")
    else:
        running_q = True
        print("Activando la tecla 'Q'...")
        # Iniciar el hilo de auto_press_r solo si no está corriendo
        threading.Thread(target=auto_press_q, daemon=True).start()
    state = "activada" if running_r else "desactivada"
    print(f"Tecla 'Q' {state}.")


# Función para crear el icono de la bandeja del sistema
def create_tray_icon():
    icon_image = Image.new('RGB', (64, 64), (255, 255, 255))  # Imagen simple para el icono
    draw = ImageDraw.Draw(icon_image)
    draw.rectangle([0, 0, 64, 64], fill=(0, 0, 0))  # Fondo negro simple

    icon = Icon("Mulheven", icon_image, menu=Menu(
        MenuItem("Restaurar", restore_window),
        MenuItem("Salir", exit_program)
    ))

    icon.run()

    # Función para cerrar la aplicación
def exit_program(icon, item):
    global running_combo, running_r, running_q
    running_combo = False
    running_r = False
    running_q = False
    icon.stop()
    root.quit()

# Función para minimizar la aplicación a la bandeja del sistema
def minimize_to_tray(icon, item):
    root.withdraw()  # Oculta la ventana principal

# Función para restaurar la aplicación desde la bandeja al hacer clic
def restore_window(icon, item):
    root.deiconify()  # Muestra la ventana principal

# Función para manejar la tecla F4
def check_f4_key():
    if keyboard.is_pressed('F4'):
        if root.state() == 'normal':
            root.withdraw()  # Minimize the window
        else:
            root.deiconify()  # Restore the window
    root.after(100, check_f4_key)  # Revisa cada 100 ms


root = tk.Tk()
root.title("Mulheven")
root.resizable(False, False)
root.attributes("-topmost", True)
root.geometry("250x260")
root.config(bg="#DBAFA9")  # Fondo claro para toda la ventana
root.iconbitmap(icon_path)  # Reemplaza con la ruta correcta

# Usando estilos de ttk
style = ttk.Style()
style.configure("TButton",
                font=("Arial", 10),
                padding=2,
                relief="flat",
                background="#DBAFA9",
                foreground="black")
style.map("TButton", background=[('active', '#45a049')])  # Cambiar color al hacer clic
style.configure("TLabel", font=("Arial", 10), background="#DBAFA9", foreground="#333")
style.configure("Custom.TCheckbutton", background="#DBAFA9", font=("Arial", 10))

# Título
title_label = tk.Label(root, text="Mulheven 0.2", font=("Arial", 14, "bold"), bg="#DBAFA9")  # Cambia el color del texto a rojo
title_label.pack(pady=10)


# Variable para los checkboxes
q_check_var = tk.BooleanVar(value=False)  # Default desactivado
r_check_var = tk.BooleanVar(value=False)  # Default desactivado

# Botones de activación/desactivación (Checkboxes)
checkbox_frame = tk.Frame(root, bg='#DBAFA9')
checkbox_frame.pack(pady=10, anchor='w')  # Alineamos el frame a la izquierda

q_checkbox = ttk.Checkbutton(checkbox_frame, text="Auto Potion (Q)", variable=q_check_var, command=toggle_q, style="Custom.TCheckbutton")
q_checkbox.grid(row=0, column=0, padx=10, pady=5, sticky='w')  # Alineación a la izquierda

r_checkbox = ttk.Checkbutton(checkbox_frame, text="Auto Ulti 'R'", variable=r_check_var, command=toggle_r, style="Custom.TCheckbutton")
r_checkbox.grid(row=1, column=0, padx=10, pady=5, sticky='w')  # Alineación a la izquierda



# Frame para contener la etiqueta y el Entry
powerFrame = tk.Frame(root, bg='#DBAFA9')
powerFrame.pack(pady=5, padx=10, anchor="w")  # 'w' para alinear a la izquierda (west)



# Entry alineado a la izquierda
power_entry = ttk.Entry(powerFrame, font=("Arial", 10), width=5)
power_entry.grid(row=0, column=0)

# Etiqueta alineada a la derecha
power_label = ttk.Label(powerFrame, text="Skills (0-5):")
power_label.grid(row=0, column=1, padx=(0, 10))  # Ajusta la distancia con padx


# Frame para contener la etiqueta y el Entry
cooldownFrame = tk.Frame(root, bg='#DBAFA9')
cooldownFrame.pack(pady=5, padx=10, anchor="w")  # 'w' para alinear a la izquierda (west)



# Entry alineado a la izquierda
cooldown_entry = ttk.Entry(cooldownFrame, font=("Arial", 10), width=5)
cooldown_entry.grid(row=1, column=0)

# Etiqueta alineada a la derecha
cooldown_label = ttk.Label(cooldownFrame, text="Cooldown (ms, min 50):")
cooldown_label.grid(row=1, column=1, padx=(0, 10))  # Ajusta la distancia con padx




# Botón para iniciar combo
combo_button = ttk.Button(root, text="Iniciar Combo", command=toggle_combo)
combo_button.pack(pady=10)

# Se puede agregar más widgets de este estilo, como checkboxes, sliders, etc.

root.after(100, check_f4_key)  # Comienza a revisar la tecla F4

root.mainloop()