from flask import Flask, render_template, request
import openai
import os

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")

MEDICAL_DISCLAIMER = (
    "⚠️ This tool provides educational information only and does not replace professional medical advice. "
    "Always consult your healthcare provider."
)

@app.route("/", methods=["GET", "POST"])
def tool():
    response_text = ""

    if request.method == "POST":
        fasting = request.form.get("fasting")
        post_meal = request.form.get("post_meal")
        age = request.form.get("age")
        gender = request.form.get("gender")
        height = request.form.get("height")
        weight = request.form.get("weight")
        sugars = request.form.get("sugars")

        prompt = f"""
You are a calm, safe medical education assistant.

User details:
- Fasting sugar: {fasting}
- Post-meal sugar: {post_meal}
- Age: {age}
- Gender: {gender}
- Height (cm): {height}
- Weight (kg): {weight}
- Last 7 days sugar values: {sugars}

Tasks:
1. Explain what these sugar values usually indicate
2. Calculate BMI from height and weight
3. Identify trend from 7-day sugars
4. Generate a simple 7-day diabetes-friendly diet plan
5. Avoid diagnosis or medication changes
6. Use reassuring tone
7. Add medical disclaimer
"""

        ai_response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )

        response_text = ai_response.choices[0].message.content + "\n\n" + MEDICAL_DISCLAIMER

    return render_template("index.html", response=response_text)

if __name__ == "__main__":
    app.run()
