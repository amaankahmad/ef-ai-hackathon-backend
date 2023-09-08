# Melanoma classification model
import tensorflow as tf

def preprocess(image):
    img = Image.open(image).convert("RGB")
    img = img.resize((512, 512))
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    return img_array

import tensorflow as tf

# Initialize an empty dictionary to hold the models
models = {}

# List of model filenames
model_filenames = [
    'EfficientNetB6_512x512_2020_epoch15_auc_0.96.h5',
    'AnotherModel.h5',
    # Add more model filenames here
]

# Load models
for filename in model_filenames:
    try:
        models[filename] = tf.keras.models.load_model(filename)
    except Exception as e:
        print(f"Failed to load {filename}. Error Type: {type(e).__name__}, Error Message: {e}")

def predict_melanoma(image, model_name):
    # Preprocess
    img = preprocess(image)
    
    # Predict using the specified model
    if model_name in models:
        pred = models[model_name].predict(img)[0]
        confidence = pred[0]
        return {'confidence': confidence}
    else:
        return {'error': 'Model not found'}

# Your Flask API remains the same, just call predict_melanoma with an additional 'model_name' parameter



# Questionnaire API
from flask import Flask, request, jsonify 
import requests

app = Flask(__name__)

@app.route('/diagnose', methods=['POST'])
def diagnose():

  # Classify melanoma
  image = request.files['image'] 
  prediction = predict_melanoma(image)

  # Get questionnaire
  confidence = prediction['confidence']
  response = requests.post('http://localhost:5000/pre_inspection', 
                           json={'confidence': confidence})

  # Return diagnosis  
  result = {
    'prediction': prediction,
    'questionnaire': response.json()
  }

  return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)