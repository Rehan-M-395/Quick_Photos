import cv2
import os
from flask import Flask, render_template, Response, request

app = Flask(__name__)

dataset_dir = "students_dataset"
os.makedirs(dataset_dir, exist_ok=True)

camera = cv2.VideoCapture(1)
current_student = None
count = 0



def gen_frames():
    """Stream video frames to the frontend."""
    global camera
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            _, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/set_student', methods=['POST'])
def set_student():
    global current_student, count
    current_student = request.form.get("student_name").strip()
    count = 0
    os.makedirs(os.path.join(dataset_dir, current_student), exist_ok=True)
    return f"✅ Student set: {current_student}"


@app.route('/capture', methods=['POST'])
def capture():
    global current_student, count, camera
    if not current_student:
        return "⚠️ No student set!"
    ret, frame = camera.read()
    if not ret:
        return "❌ Failed to capture"
    filename = os.path.join(dataset_dir, current_student, f"{current_student}_{count}.jpg")
    cv2.imwrite(filename, frame)
    count += 1
    return f"✅ Saved {filename}"

@app.route('/finish_student', methods=['POST'])

def finish_student():
    global current_student, count
    if not current_student:
        return "Finish photoshoot"
    
    finished_student = current_student
    current_student = None
    count = 0
    return f"Finished collecting photos for {finished_student}"

@app.route('/stop_photoshoot', methods=['POST'])
def stop_photoshoot():
    global photoshoot_active, camera, current_student, count
    photoshoot_active = False
    current_student = None
    count = 0
    if camera.isOpened():
        camera.release()
    return "🛑 Photoshoot stopped. Restart app to use again."
if __name__ == '__main__':
    app.run(debug=True)
