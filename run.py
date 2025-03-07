from flask import Flask, render_template, jsonify
import json
import os

app = Flask(__name__)

def load_data():
    with open('saas_growth_quadratic_1.json', 'r') as file:
        return json.load(file)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data')
def get_data():
    data = load_data()
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)