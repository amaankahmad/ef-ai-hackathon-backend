import numpy as np
import os
import pandas as pd
import random
import string
from flask import Flask, flash, request, redirect, send_from_directory, url_for, jsonify
from keras.preprocessing import image
from keras.models import load_model
from werkzeug.utils import secure_filename

# Initialize Flask app
app = Flask(__name__, static_folder='../client/build')

# Helper functions and classes for the first endpoint
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def benignMaligant(folderpath):
    model = load_model('assets/model.h5')
    model.compile(loss='categorical_crossentropy',
                  optimizer='rmsprop', metrics=['accuracy'])
    test_filenames = os.listdir(folderpath)
    test_df = pd.DataFrame({
        'filename': test_filenames
    })
    nb_samples = test_df.shape[0]

    test_gen = image.ImageDataGenerator(rescale=1./255)
    test_generator = test_gen.flow_from_dataframe(
        test_df,
        folderpath,
        x_col='filename',
        y_col=None,
        class_mode=None,
        target_size=(128, 128),
        batch_size=3,
        shuffle=False
    )
    predict = model.predict_generator(
        test_generator, steps=np.ceil(nb_samples/3))
    return str(predict[0][1])


def randomString():
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(24))

# Helper class for the second endpoint


class PreInspectionAI:
    def __init__(self):
        self.risk_factor = 0

    def process_responses(self, responses):
        try:
            for i, response in enumerate(responses):
                if i == 0 and response.lower() == "yes":
                    self.risk_factor += 0.3
                if i == 1 and response.lower() in ["weeks", "months", "years"]:
                    self.risk_factor += 0.2
                if i == 2 and response.lower() == "yes":
                    self.risk_factor += 0.3
                if i == 3 and response.lower() == "yes":
                    self.risk_factor += 0.2

            self.risk_factor = min(self.risk_factor, 1)
            return None
        except Exception as e:
            return str(e)

# First endpoint: /predict


@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return app.make_response(('No File', 400))
    file = request.files['file']
    if file.filename == '':
        return app.make_response(('', 400))
    if file and allowed_file(file.filename):
        foldername = randomString()
        filename = secure_filename(file.filename)
        folderpath = os.path.join(foldername)
        filepath = os.path.join(foldername, filename)
        os.mkdir(folderpath)
        file.save(filepath)
        message = benignMaligant(folderpath)
        os.remove(filepath)
        os.rmdir(folderpath)
        return app.make_response(message)
    return app.make_response(('Invalid File', 400))

# Second endpoint: /pre-inspection


@app.route('/pre-inspection', methods=['POST'])
def pre_inspection():
    try:
        data = request.json
        responses = data.get('responses', [])

        if len(responses) != 4:
            return jsonify({'error': 'Invalid number of responses'}), 400

        pre_inspection = PreInspectionAI()
        error = pre_inspection.process_responses(responses)

        if error:
            return jsonify({'error': error}), 400

        risk_factor = pre_inspection.risk_factor
        confidence_score = f"{risk_factor:.2f} ± 0.05"

        recommendation = "So far, there's no immediate cause for concern, but monitoring is always good."
        if risk_factor > 0.7:
            recommendation = "I strongly recommend consulting a healthcare professional for a thorough evaluation."
        elif risk_factor > 0.4:
            recommendation = "It may be beneficial to consult a healthcare professional for further assessment."

        result = {
            'risk_factor': risk_factor,
            'confidence_score': confidence_score,
            'recommendation': recommendation
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Catch-all route


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    if path != '' and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')


# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
