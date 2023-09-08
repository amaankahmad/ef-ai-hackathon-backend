import flask
from flask import Flask, request, jsonify
from flask_restful import Resource, Api
import numpy as np
import PIL
import tensorflow as tf

app = Flask(__name__)
api = Api(app)

# Model parameters
image_size = 256 
crop_size = 250

# Load model
model = tf.keras.models.load_model('EfficientNetB6_512x512_2020_epoch15_auc_0.96.h5')

class MelanomaPrediction(Resource):
    def post(self):
        # Get image from post request
        imagefile = request.files['image'] 
        image = PIL.Image.open(imagefile.stream)

        # Preprocess
        img = np.asarray(image.resize((image_size, image_size))) / 255.0
        img = tf.image.central_crop(img, crop_size / image_size)
        img = np.expand_dims(img, axis=0)

        # Prediction
        prediction = model.predict(img)[0]
        confidence = prediction[0]

        # Build response
        response = {
            'prediction': float(confidence)
        }
        return jsonify(response)

api.add_resource(MelanomaPrediction, '/predict')

if __name__ == '__main__':
    app.run(debug=True)