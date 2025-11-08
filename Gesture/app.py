from flask import Flask, render_template, jsonify
from threading import Thread
import gesture_engine   # your OpenCV file

app = Flask(__name__)

# ---------------- Start Gesture Engine Thread ----------------
def run_engine():
    gesture_engine.start_gesture_engine()

Thread(target=run_engine, daemon=True).start()


# ---------------- Flask Routes ----------------
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/gesture")
def gesture_data():
    return jsonify({"gesture": gesture_engine.current_gesture})


# ---------------- Start Flask ----------------
if __name__ == "__main__":
    app.run(debug=True)
