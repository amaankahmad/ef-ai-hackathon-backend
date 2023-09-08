from flask import Flask, request, jsonify

app = Flask(__name__)

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

@app.route('/pre_inspection', methods=['POST'])
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

if __name__ == '__main__':
    app.run(debug=True)
