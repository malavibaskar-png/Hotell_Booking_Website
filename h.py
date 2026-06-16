from flask import Flask, render_template, request
import cv2
import os
import numpy as np

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Dummy plant recommendation logic
def recommend_plants(light_level):
    if light_level == "high":
        return ["Tomato 🍅", "Chili 🌶️", "Sunflower 🌻"]
    elif light_level == "medium":
        return ["Mint 🌿", "Spinach 🥬", "Aloe Vera 🌱"]
    else:
        return ["Snake Plant 🌵", "Money Plant 🍃", "Fern 🌿"]

# Analyze image using OpenCV
def analyze_image(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    brightness = np.mean(gray)

    if brightness > 180:
        light = "high"
    elif brightness > 100:
        light = "medium"
    else:
        light = "low"

    return light

@app.route("/", methods=["GET", "POST"])
def index():
    plants = []
    light = None

    if request.method == "POST":
        file = request.files["image"]

        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)

            light = analyze_image(filepath)
            plants = recommend_plants(light)

    return render_template("index.html", plants=plants, light=light)

if __name__ == "__main__":
    app.run(debug=True)