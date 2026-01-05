from flask import Flask, render_template, request
import os
import openai

app = Flask(__name__)

# Make sure you set your OPENAI_API_KEY as environment variable on Render
openai.api_key = os.getenv("OPENAI_API_KEY")

MEDICAL_DISCLAIMER = "<strong style='color:red;'>Disclaimer:</strong> This tool provides general diabetes guidance and food suggestions only. It does not replace professional medical advice, diagnosis, or treatment. Always consult your doctor for personal medical concerns."

def format_ai_response(ai_response_text):
    lines = ai_response_text.split('\n')
    formatted_lines = []
    colors = ['#2563EB', '#10B981', '#F59E0B', '#8B5CF6', '#EF4444', '#3B82F6']
    color_index = 0

    for line in lines:
        line = line.strip()
        if line.startswith(tuple(str(i) for i in range(1, 10))) and ':' in line:
            tip_num, rest = line.split(':', 1)
            formatted_line = f"<strong style='color:{colors[color_index % len(colors)]};'>{tip_num}:</strong>{rest}"
            color_index += 1
        else:
            formatted_line = line
        formatted_lines.append(formatted_line)

    formatted_lines.append(MEDICAL_DISCLAIMER)
    return "<br>".join(formatted_lines)

@app.route("/", methods=["GET", "POST"])
def tool():
    result = None
    if request.method == "POST":
        sugar = request.form.get("sugar")
        timing = request.form.get("timing")
        age = request.form.get("age")
        gender = request.form.get("gender")
        height = request.form.get("height")
        weight = request.form.get("weight")

        prompt = f"""
        You are a professional diabetes consultant AI. 
        User data:
        Blood Sugar: {sugar} mg/dL
        Timing: {timing}
        Age: {age}
        Gender: {gender}
        Height: {height} cm
        Weight: {weight} kg

        1. Analyze the sugar value and timing.
        2. Provide actionable food guidance tips numbered 1-6.
        3. Each tip heading should be bold and different color (format in HTML later).
        4. Include a Disclaimer at the end.
        """

        try:
            # ✅ New OpenAI API v1 syntax
            ai_response = openai.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            ai_text = ai_response.choices[0].message["content"]
            result = format_ai_response(ai_text)
        except Exception as e:
            result = f"<strong style='color:red;'>Error:</strong> {str(e)}"

    return render_template("index.html", result=result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
