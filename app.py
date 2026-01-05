from flask import Flask, render_template, request, jsonify
import os
from openai import OpenAI

app = Flask(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        try:
            sugar = request.form.get("sugar")

            if not sugar or not sugar.isdigit():
                return jsonify({"error": "Invalid sugar value"})

            sugar = int(sugar)

            prompt = f"""
You are a diabetes care assistant.

User fasting blood sugar: {sugar} mg/dL

Give:
1. Meaning of this sugar value
2. Food guidance for today (bullet points)
3. Lifestyle advice
4. Clear disclaimer at end

Formatting rules:
- Each heading must be bold
- Headings must be colored using HTML <span> tags
- Disclaimer word must be RED and BOLD
"""

            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": "You are a professional diabetes educator."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )

            ai_text = response.choices[0].message.content
            return jsonify({"result": ai_text})

        except Exception as e:
            return jsonify({"error": str(e)})

    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
