from flask import Flask, render_template, request, jsonify, send_file
from g4f.client import Client
import g4f
import os

app = Flask(__name__)
client = Client()
messages = []


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/check-grammar", methods=["POST"])
def check_grammar():
    input_text = request.form.get("text", "")
    try:
        prompt = "Check the grammar in the following sentence and return only the corrected version."
        combined_input = f"{prompt} {input_text}"

        response = client.chat.completions.create(
            model=g4f.models.gpt_35_turbo,
            messages=[{"role": "user", "content": combined_input}],
        )

        corrected_text = response.choices[0].message.content
        return jsonify({"corrected_text": corrected_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/translate", methods=["POST"])
def translate_text():
    input_text = request.form.get("text", "")
    target_language = request.form.get("language", "")

    if not target_language:
        return jsonify({"error": "No target language provided"}), 400

    try:
        prompt = f"Translate the following sentence to {target_language}: {input_text}"

        response = client.chat.completions.create(
            model=g4f.models.gpt_35_turbo,
            messages=[{"role": "user", "content": prompt}],
        )

        translated_text = response.choices[0].message.content
        return jsonify({"translated_text": translated_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/bug-control", methods=["POST"])
def bug_control():
    description_input = request.form.get("description", "")
    prompt = (
        "Check and improve the following bug description. Provide a corrected version with title, priority (1-5), "
        "and severity (1-5). Priority 1 is highest. Please do not write anything and just send me what you changed. "
        "Do not use ** "
    )
    combined_input = f"{prompt}\n\n{description_input}"

    try:
        response = client.chat.completions.create(
            model=g4f.models.gpt_4,
            messages=[{"role": "user", "content": combined_input}],
        )

        result = response.choices[0].message.content
        return jsonify({"bug_description": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/generate-image", methods=["POST"])
def generate_image():
    user_prompt = request.form.get("prompt", "")

    if not user_prompt:
        return jsonify({"error": "Prompt is required"}), 400

    try:
        response = client.images.generate(
            model="flux", prompt=user_prompt, response_format="url"
        )

        image_url = response.data[0].url
        return jsonify({"image_url": image_url})
    except Exception as e:
        return jsonify({"error": f"Error generating image: {str(e)}"}), 500


@app.route("/analyze-image", methods=["POST"])
def analyze_image():
    try:
        if "image" not in request.files:
            return jsonify({"error": "No image file provided"}), 400

        image_file = request.files["image"]
        image_path = os.path.join("temp", image_file.filename)
        image_file.save(image_path)

        with open(image_path, "rb") as file:
            response = client.chat.completions.create(
                model=g4f.models.gemini_pro,
                messages=[
                    {"role": "user", "content": "What can you see in this image?"}
                ],
                image=file,
            )

        analysis_result = response.choices[0].message.content

        os.remove(image_path)

        return jsonify({"analysis": analysis_result})
    except Exception as e:
        return jsonify({"error": f"Error analyzing image: {str(e)}"}), 500


@app.route("/interactive-chat", methods=["POST"])
def interactive_chat():
    global messages
    user_input = request.form.get("message", "").strip()

    if user_input.lower() == "exit":
        return jsonify({"response": "Exiting chat...", "exit": True})

    try:
        messages.append({"role": "user", "content": user_input})

        if "image" in request.files:
            image_file = request.files["image"]
            image_path = os.path.join("temp", image_file.filename)
            image_file.save(image_path)

            with open(image_path, "rb") as file:
                response = client.chat.completions.create(
                    messages=messages,
                    model=g4f.models.gemini_pro,
                    image=file,
                )

            os.remove(image_path)
        else:
            response = client.chat.completions.create(
                messages=messages,
                model=g4f.models.gpt_4,
            )

        gpt_response = response.choices[0].message.content
        messages.append({"role": "assistant", "content": gpt_response})
        return jsonify({"response": gpt_response})
    except Exception as e:
        return jsonify({"error": f"Error during interactive chat: {str(e)}"}), 500

@app.route("/add-testcases", methods=["POST"])
def add_testcase():
    input_text = request.form.get("text", "")
    try:
        prompt = "Add new test cases for the following code to cover all branches. Provide them as TC-1, TC-2, etc."
        combined_input = f"{prompt} {input_text}"

        response = client.chat.completions.create(
            model=g4f.models.gpt_4,
            messages=[{"role": "user", "content": combined_input}],
        )

        corrected_text = response.choices[0].message.content
        return jsonify({"test_cases": corrected_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/how-to-reply", methods=["POST"])
def how_to_reply():
    input_text = request.form.get("text", "")
    try:
        prompt = "Reply to the following sentence and return only the answer. "
        combined_input = f"{prompt} {input_text}"

        response = client.chat.completions.create(
            model=g4f.models.gpt_4,
            messages=[{"role": "user", "content": combined_input}],
        )

        corrected_text = response.choices[0].message.content
        return jsonify({"Reply": corrected_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/process-requirements-and-code", methods=["POST"])
def process_requirements_and_code():
    requirements = request.form.get("requirements", "")
    code = request.form.get("code", "")

    try:
        predefined_instruction = (
            "Analyze the requirements and code below. Validate if the requirements are fulfilled by the code "
            "and provide suggestions for improvement or missing elements. Return only the answer. "
        )
        combined_input = f"{predefined_instruction}\n\nRequirements:\n{requirements}\n\nCode:\n{code}"

        response = client.chat.completions.create(
            model=g4f.models.gpt_4,
            messages=[{"role": "user", "content": combined_input}],
        )

        analysis_result = response.choices[0].message.content
        return jsonify({"analysis": analysis_result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
