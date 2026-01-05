from flask import Flask, render_template, request
from openai import OpenAI
import os

# Initialize Flask app
app = Flask(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Medical disclaimer text
MEDICAL_DISCLAIMER = (
    "\n\nDisclaimer: This tool provides general diabetes guidance and food suggestions only. "
    "It does not replace professional medical advice, diagnosis, or treatment. "
    "Always consult your doctor for personal medical concerns."
)

@app.route("/", methods=["GET", "POST"])
def tool():
    if request.method == "POST":
        # Get form values safely
        sugar = request.form.get("sugar", "").strip()
        timing = request.form.get("timing", "").strip()
        age = request.form.get("age", "").strip()
        gender = request.form.get("gender", "").strip()
        height = request.form.get("height", "").strip()
        weight = request.form.get("weight", "").strip()

        # Create prompt for AI
        prompt = f"""
User sugar reading: {sugar}
Timing: {timing}
Age: {age}
Gender: {gender}
Height: {height} cm
Weight: {weight} kg

Explain what this sugar level means in simple language and provide food guidance for today only.
"""

        # Call OpenAI API
        try:
            ai_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a diabetes education assistant. "
                            "You explain sugar readings and provide food guidance only. "
                            "Do not give diagnosis or medication advice."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3
            )

            # Extract AI reply
            reply = ai_response.choices[0].message.content + MEDICAL_DISCLAIMER

        except Exception as e:
            reply = f"An error occurred while generating the guidance: {e}"

        # Render result
        return render_template("index.html", result=reply)

    # GET request returns blank form
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
