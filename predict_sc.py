# Melanoma classification model
import tensorflow as tf

melanoma_model = tf.keras.models.load_model('EfficientNetB6_512x512_2020_epoch15_auc_0.96.h55')

def predict_melanoma(image):
  # Preprocess 
  img = preprocess(image) 
  
  # Predict
  pred = melanoma_model.predict(img)[0]
  confidence = pred[0]

  return {
    'confidence': confidence 
  }

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
