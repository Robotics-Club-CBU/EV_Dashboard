import customtkinter as ctk
import tkinter as tk
import cv2
from PIL import Image, ImageTk
import numpy as np
import random
import time
import math
import requests
import datetime  # Import the datetime module

# Initialize the main window
root = ctk.CTk()
root.title("MAFISHI 2.0 Dashboard")
root.geometry("1280x720")
root.configure(bg='black')
root.attributes('-fullscreen', True)  # Set the window to full screen
root.overrideredirect(True)  # Removes the window decorations (title bar, button, etc.)

api_key = "1d4e963e0b25a4c086afe092f64ec71a"
city = "Lusaka"
url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={api_key}"

# Create main frame
main_frame = ctk.CTkFrame(root, bg_color="black")
main_frame.pack(expand=True, fill="both", padx=10, pady=10)

# Configure grid
main_frame.grid_columnconfigure(0, weight=1)
main_frame.grid_columnconfigure(1, weight=1)
main_frame.grid_rowconfigure(2, weight=1)

# Add title or heading
title_label = ctk.CTkLabel(main_frame, text="MAFISHI 2.0 DASHBOARD", font=("Helvetica", 24, "bold"), text_color="white")
title_label.grid(row=0, column=0, columnspan=2, pady=10)

# Global variables for vitals
battery_percentage = 75  # Example starting value
speed = 60  # Example speed value

# Create a frame for camera feed
camera_frame = ctk.CTkFrame(main_frame, bg_color="black")
camera_frame.grid(row=1, column=0, padx=20, pady=20, rowspan=2, sticky="nsew")

# Create a frame for battery, speed, and other vitals
vitals_frame = ctk.CTkFrame(main_frame, bg_color="black")
vitals_frame.grid(row=1, column=1, padx=20, pady=20, rowspan=2, sticky="nsew")

# Battery percentage
battery_label = ctk.CTkLabel(vitals_frame, text="Battery: 75%", font=("Helvetica", 18), text_color="white")
battery_label.grid(row=0, column=0, pady=10, padx=10)

battery_bar = ctk.CTkProgressBar(vitals_frame, width=300)
battery_bar.grid(row=0, column=1, padx=10)
battery_bar.set(battery_percentage / 100)

# Additional vitals like temperature, voltage, etc.
temp_label = ctk.CTkLabel(vitals_frame, text="Temperature: 35°C", font=("Helvetica", 18), text_color="white")
temp_label.grid(row=2, column=0, pady=10, padx=10)

voltage_label = ctk.CTkLabel(vitals_frame, text="Voltage: 400V", font=("Helvetica", 18), text_color="white")
voltage_label.grid(row=2, column=1, pady=10, padx=10)

# Weather data labels
temperature_label = ctk.CTkLabel(vitals_frame, text="Temperature: N/A", font=("Helvetica", 18), text_color="white")
temperature_label.grid(row=3, column=0, pady=10, padx=10)

description_label = ctk.CTkLabel(vitals_frame, text="Weather: N/A", font=("Helvetica", 18), text_color="white")
description_label.grid(row=3, column=1, pady=10, padx=10)

wind_speed_label = ctk.CTkLabel(vitals_frame, text="Wind Speed: N/A", font=("Helvetica", 18), text_color="white")
wind_speed_label.grid(row=4, column=0, pady=10, padx=10)

# Fetch weather data from the API
response = requests.get(url)
weather_data = response.json()

if response.status_code == 200:
    temperature = weather_data['main']['temp']
    description = weather_data['weather'][0]['description']
    wind_speed = weather_data['wind']['speed']

    # Update the labels with the fetched data
    temperature_label.configure(text=f"Temperature: {temperature}°C")
    description_label.configure(text=f"Weather: {description}")
    wind_speed_label.configure(text=f"Wind Speed: {wind_speed} m/s")
else:
    print("Failed to retrieve data")

# Alert label
alert_label = ctk.CTkLabel(main_frame, text="", font=("Helvetica", 18), text_color="red")
alert_label.grid(row=3, column=0, columnspan=2, pady=10)

# Load YOLO
net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")
layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
classes = []
with open("coco.names", "r") as f:
    classes = [line.strip() for line in f.readlines()]

# Alert messages for specific classes
alert_messages = {
    "person": "Person detected!",
    "dog": "Dog detected!",
    "car": "Car detected!",
    "tree": "Tree detected!",
    "traffic light": "Traffic light detected!",
    "stop sign": "Stop sign detected!",
    # Add more classes and messages as needed
}

# Function to calculate the range based on battery percentage
def calculate_range(battery_percentage):
    max_range = 400  # Example maximum range in km
    return (battery_percentage / 100) * max_range

# Function to update the battery percentage
def update_battery():
    global battery_percentage
    battery_percentage = random.randint(0, 100)  # Simulate a random battery percentage for now
    battery_label.configure(text=f"Battery: {battery_percentage}%")
    battery_bar.set(battery_percentage / 100)
    range_km = calculate_range(battery_percentage)
    range_label.configure(text=f"Range: {range_km:.2f} km")
    draw_gauge(speed_canvas, speed, 0, 120, "Speed (km/h)")
    draw_gauge(range_canvas, range_km, 0, 400, "Range (km)")
    root.after(5000, update_battery)  # Update every 5 seconds

# Function to update the speed
def update_speed():
    global speed
    speed = random.randint(0, 120)  # Simulate a random speed for now
    speed_label.configure(text=f"Speed: {speed} km/h")
    draw_gauge(speed_canvas, speed, 0, 120, "Speed (km/h)")
    root.after(1000, update_speed)  # Update every 1 second

# Global variable to track camera state
camera_on = False

# Function to handle camera feed using OpenCV and YOLO
def update_camera():
    if camera_on:
        ret, frame = cap.read()
        if ret:
            # Resize the frame to desired dimensions, e.g., 320x240
            frame = cv2.resize(frame, (800, 600))
            
            height, width, channels = frame.shape

            # Detecting objects
            blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
            net.setInput(blob)
            outs = net.forward(output_layers)

            # Show info on the screen
            class_ids = []
            confidences = []
            boxes = []
            for out in outs:
                for detection in out:
                    scores = detection[5:]
                    class_id = np.argmax(scores)
                    confidence = scores[class_id]
                    if confidence > 0.5:
                        # Object detected
                        center_x = int(detection[0] * width)
                        center_y = int(detection[1] * height)
                        w = int(detection[2] * width)
                        h = int(detection[3] * height)

                        # Rectangle coordinates
                        x = int(center_x - w / 2)
                        y = int(center_y - h / 2)

                        boxes.append([x, y, w, h])
                        confidences.append(float(confidence))
                        class_ids.append(class_id)

            # Apply non-max suppression to avoid overlapping boxes
            indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

            detected_objects = set()
            for i in range(len(boxes)):
                if i in indexes:
                    x, y, w, h = boxes[i]
                    label = str(classes[class_ids[i]])
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    if label in alert_messages:
                        detected_objects.add(alert_messages[label])

            if detected_objects:
                alert_label.configure(text=", ".join(detected_objects), text_color="red")
            else:
                alert_label.configure(text="", text_color="black")

            # Convert frame to RGB for Tkinter
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            camera_label.imgtk = imgtk
            camera_label.configure(image=imgtk)
    camera_label.after(10, update_camera)  # Update camera feed every 10 ms

# Function to turn the camera on
def turn_camera_on():
    global camera_on
    if not camera_on:
        camera_on = True
        cap.open(0)
        print("Camera turned on")

# Function to turn the camera off
def turn_camera_off():
    global camera_on
    if camera_on:
        camera_on = False
        cap.release()
        camera_label.configure(image='')
        print("Camera turned off")

# Add camera feed
camera_label = ctk.CTkLabel(camera_frame)
camera_label.pack()

# OpenCV Camera Setup
cap = cv2.VideoCapture(0)  # Use the first camera available

# Add buttons for turning the camera on and off
turn_on_button = ctk.CTkButton(main_frame, text="Turn Camera On", command=turn_camera_on)
turn_on_button.grid(row=4, column=0, pady=10)

turn_off_button = ctk.CTkButton(main_frame, text="Turn Camera Off", command=turn_camera_off)
turn_off_button.grid(row=4, column=1, pady=10)

# Function to handle keyboard events
def on_key_press(event):
    print(f"Key pressed: {event.keysym}")

# Bind the keyboard event to the function
root.bind("<KeyPress>", on_key_press)

# Function to update the current time
def update_time():
    current_time = time.strftime("%Y-%m-%d %H:%M:%S")
    time_label.configure(text=current_time)
    root.after(1000, update_time)  # Update every 1 second

# Add a label to display the current time
time_label = ctk.CTkLabel(main_frame, text="", font=("Helvetica", 18), text_color="white")
time_label.grid(row=5, column=0, columnspan=2, pady=10)

# Function to draw a gauge
def draw_gauge(canvas, value, min_value, max_value, label):
    canvas.delete("all")
    width = canvas.winfo_width()
    height = canvas.winfo_height()
    center_x = width // 2
    center_y = height // 2
    radius = min(center_x, center_y) - 10

    # Draw the background arc
    canvas.create_arc(center_x - radius, center_y - radius, center_x + radius, center_y + radius, start=135, extent=270, style="arc", outline="white", width=2)

    # Draw tick marks and labels
    for i in range(min_value, max_value + 1, (max_value - min_value) // 10):
        angle = 135 + (270 * (i - min_value) / (max_value - min_value))
        angle_rad = math.radians(angle)
        tick_x1 = center_x + (radius - 10) * math.cos(angle_rad)
        tick_y1 = center_y - (radius - 10) * math.sin(angle_rad)
        tick_x2 = center_x + radius * math.cos(angle_rad)
        tick_y2 = center_y - radius * math.sin(angle_rad)
        canvas.create_line(tick_x1, tick_y1, tick_x2, tick_y2, fill="white", width=2)
        label_x = center_x + (radius - 20) * math.cos(angle_rad)
        label_y = center_y - (radius - 20) * math.sin(angle_rad)
        canvas.create_text(label_x, label_y, text=str(i), fill="white", font=("Helvetica", 10))

    # Draw the needle
    angle = 135 + (270 * (value - min_value) / (max_value - min_value))
    angle_rad = math.radians(angle)
    needle_x = center_x + radius * math.cos(angle_rad)
    needle_y = center_y - radius * math.sin(angle_rad)
    canvas.create_line(center_x, center_y, needle_x, needle_y, fill="red", width=2)

    # Draw the value text
    canvas.create_text(center_x, center_y + radius + 20, text=f"{value:.2f}", fill="white", font=("Helvetica", 12, "bold"))

    # Draw the label text
    canvas.create_text(center_x, center_y - radius - 20, text=label, fill="white", font=("Helvetica", 12, "bold"))

# Create canvases for speed and range gauges
speed_canvas = ctk.CTkCanvas(vitals_frame, width=200, height=200, bg="black", highlightthickness=0)
speed_canvas.grid(row=6, column=0, pady=10, padx=10)

range_canvas = ctk.CTkCanvas(vitals_frame, width=200, height=200, bg="black", highlightthickness=0)
range_canvas.grid(row=6, column=1, pady=10, padx=10)

# Speed display
speed_label = ctk.CTkLabel(vitals_frame, text="Speed: 60 km/h", font=("Helvetica", 18), text_color="white")
speed_label.grid(row=7, column=0, pady=10, padx=10)

# Range display
range_label = ctk.CTkLabel(vitals_frame, text="Range: Calculating...", font=("Helvetica", 18), text_color="white")
range_label.grid(row=7, column=1, pady=10, padx=10)

# Function to update the current day of the week
def update_day():
    current_day = datetime.datetime.now().strftime("%A")
    day_label.configure(text=f"Today is: {current_day}")
    root.after(86400000, update_day)  # Update every 24 hours

# Add a label to display the current day of the week
day_label = ctk.CTkLabel(main_frame, text="", font=("Helvetica", 18), text_color="white")
day_label.grid(row=6, column=0, columnspan=2, pady=10)

# Start updating vitals, camera feed, time, and day
update_battery()
update_speed()
update_camera()
update_time()
update_day()

# Turn the camera on at startup
turn_camera_on()

# Start the Tkinter main loop
root.mainloop()

# Release the camera when the window is closed
cap.release()
