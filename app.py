from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import threading
import io
from PIL import Image, ImageDraw, ImageFont
from g4f.client import Client
import g4f

app = Flask(__name__)
client = Client()


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/check-grammar', methods=['POST'])
def check_grammar():
    input_text = request.form.get('text', '')
    try:
        prompt = "Check the grammar in the following sentence and return only the corrected version."
        combined_input = f"{prompt} {input_text}"

        response = client.chat.completions.create(
            model=g4f.models.gpt_35_turbo,
            messages=[{"role": "user", "content": combined_input}]
        )

        corrected_text = response.choices[0].message.content
        return jsonify({'corrected_text': corrected_text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/translate', methods=['POST'])
def translate_text():
    input_text = request.form.get('text', '')
    target_language = request.form.get('language', '')

    if not target_language:
        return jsonify({'error': 'No target language provided'}), 400

    try:
        prompt = f"Translate the following sentence to {target_language}: {input_text}"

        response = client.chat.completions.create(
            model=g4f.models.gpt_35_turbo,
            messages=[{"role": "user", "content": prompt}]
        )

        translated_text = response.choices[0].message.content
        return jsonify({'translated_text': translated_text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/bug-control', methods=['POST'])
def bug_control():
    description_input = request.form.get('description', '')
    prompt = (
        "Check and improve the following bug description. Provide a corrected version with title, priority (1-5), "
        "and severity (1-5). Priority 1 is highest. Please do not write anything and just send me what you changed. "
        "Do not use ** "
    )
    combined_input = f"{prompt}\n\n{description_input}"

    try:
        response = client.chat.completions.create(
            model=g4f.models.gpt_4,
            messages=[{"role": "user", "content": combined_input}]
        )

        result = response.choices[0].message.content
        return jsonify({'bug_description': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
