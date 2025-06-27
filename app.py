from flask import Flask, render_template, request, send_file, jsonify
from utils.resume_parser import parse_resume
from utils.resume_feedback import analyze_resume, suggest_improvements
from utils.pdf_generator import generate_feedback_pdf, generate_advice_pdf
from utils.models import save_resume_to_db, get_all_resumes, save_career_query_to_db
from utils.local_llm import get_llm_response
import threading
from datetime import datetime
from markdown import markdown


app = Flask(__name__)
last_career_query = {"prompt": "", "response": "", "timestamp": ""}

# === Global Stores ===
last_resume_text = ""
last_feedback = []
last_suggestions = []
progress_tracker = {"progress": 0}  # For progress bar

# === Emoji Enhancer ===
def add_emojis_to_advice(advice):
    emojis = {
        "software": "💻",
        "developer": "👨‍💻",
        "engineering": "🛠️",
        "design": "🎨",
        "management": "📊",
        "marketing": "📣",
        "data": "📈",
        "ai": "🤖",
        "machine learning": "🧠",
        "finance": "💰",
        "internship": "🧑‍🎓",
        "job": "🧳",
        "startup": "🚀",
        "research": "🔬",
        "career": "🎯",
        "success": "🏆",
        "skills": "🧰",
        "future": "🔮",
        "confidence": "💪",
        "growth": "🌱"
    }
    for keyword, emoji in emojis.items():
        if keyword.lower() in advice.lower():
            advice += f" {emoji}"
    return advice

# === Page Routes ===
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/career')
def career():
    return render_template('career.html')

@app.route('/resume')
def resume():
    return render_template('resume.html')

@app.route('/roadmap')
def roadmap():
    return render_template('roadmap.html')

@app.route('/resources')
def resources():
    return render_template('resources.html')

@app.route('/resume_checker')
def resume_checker():
    return render_template('resume_checker.html')

# === Career Advice (LLM) ===
@app.route('/career-advice', methods=['POST'])
def career_advice():
    global last_career_query

    user_input = request.form.get('career_query')
    if not user_input:
        return render_template('career.html', advice="Please enter something.")

    prompt = f"""You are a professional career advisor. A student has asked the following question:\n\n"{user_input}"\n\nGive a clear, practical career suggestion in 100 words."""

    try:
        advice = get_llm_response(prompt)
        advice_with_emojis = add_emojis_to_advice(advice)

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        last_career_query = {
            "prompt": user_input,
            "response": advice,
            "timestamp": timestamp
        }

        save_career_query_to_db(prompt, advice, timestamp)

    except Exception as e:
        advice_with_emojis = f"⚠️ Error generating advice: {str(e)}"

    return render_template('career.html', advice=advice_with_emojis, advice_prompt=user_input)

@app.route('/career-roadmap', methods=['POST'])
def career_roadmap():
    try:
        original_prompt = request.form.get('original_prompt', '')
        if not original_prompt:
            return render_template("roadmap_result.html", roadmap="❌ Error: No prompt received.")

        prompt = f"Create a step-by-step career roadmap for: {original_prompt}"
        roadmap = get_llm_response(prompt)

        return render_template("roadmap_result.html", roadmap=roadmap)
    except Exception as e:
        return render_template("roadmap_result.html", roadmap=f"❌ Error: {str(e)}")

# === Resume Analysis ===
@app.route('/result', methods=['POST'])
def result():
    if 'resume_file' not in request.files:
        return "No file uploaded", 400

    file = request.files['resume_file']
    parsed_text = parse_resume(file.stream)
    result_data = analyze_resume(parsed_text)

    score = result_data["score"]
    feedback = result_data["feedback"]
    missing_sections = result_data["missing_sections"]

    global last_resume_text, last_feedback, progress_tracker, last_suggestions
    last_resume_text = parsed_text
    last_feedback = feedback
    last_suggestions = []
    progress_tracker["progress"] = 0

    save_resume_to_db(parsed_text, feedback, score)

    return render_template(
        "result.html",
        score=score,
        resume_text=parsed_text,
        feedback=feedback,
        suggestions=[],
        missing_sections=missing_sections
    )

# === Suggestion Generator (LLM with Progress Tracking) ===
@app.route('/get_suggestions', methods=['GET'])
def get_suggestions():
    global last_suggestions, progress_tracker

    try:
        def run_suggestions():
            suggestions = suggest_improvements(last_resume_text, progress_tracker)
            last_suggestions[:] = suggestions
            progress_tracker["progress"] = 100

        thread = threading.Thread(target=run_suggestions)
        thread.start()

        return jsonify([])  # Immediate response
    except Exception as e:
        return jsonify([{"error": str(e)}])

@app.route('/get_progress')
def get_progress():
    return jsonify({"progress": progress_tracker.get("progress", 0)})

@app.route('/get_final_suggestions')
def get_final_suggestions():
    return jsonify(last_suggestions)

# === PDF Download Routes ===
@app.route('/download_feedback')
def download_feedback():
    try:
        pdf_buffer = generate_feedback_pdf(last_resume_text, last_suggestions or last_feedback)
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name='resume_feedback.pdf',
            mimetype='application/pdf'
        )
    except Exception as e:
        return f"Error generating PDF: {str(e)}"

@app.route('/download_career_advice')
def download_career_advice():
    try:
        pdf_buffer = generate_advice_pdf(
            last_career_query.get("prompt", "No question."),
            last_career_query.get("response", "No advice available."),
            last_career_query.get("timestamp", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        )
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name='career_advice.pdf',
            mimetype='application/pdf'
        )
    except Exception as e:
        return f"Error generating PDF: {str(e)}"

@app.route('/generate_roadmap', methods=['POST'])
def generate_roadmap():
    try:
        goal = request.form.get("goal", "")
        level = request.form.get("level", "")
        field = request.form.get("field", "")

        if not goal or not level or not field:
            return render_template("roadmap.html", roadmap="❌ Please fill in all fields.")

        # LLaMA prompt
        prompt = f"""You are a helpful AI assistant. A student wants a custom learning roadmap.
Their goal: {goal}
Current skill level: {level}
Field of interest: {field}

Generate a detailed step-by-step roadmap with stages and resources. Make it concise, structured, and useful for Indian students."""

        roadmap = get_llm_response(prompt)

        return render_template("roadmap.html", roadmap=markdown(roadmap))

    except Exception as e:
        return render_template("roadmap.html", roadmap=f"❌ Error: {str(e)}")

# === Roadmap Formatter ===
def format_roadmap(text):
    lines = text.strip().split("\n")
    formatted = ""
    for line in lines:
        line = line.strip()
        if line.endswith(":"):
            formatted += f"<h3>{line}</h3>\n"
        elif line and (line[0].isdigit() or line.startswith("-")):
            formatted += f"<li>{line}</li>\n"
        elif line:
            formatted += f"<p>{line}</p>\n"
    return f"<ul>{formatted}</ul>"

# === Run the App ===
if __name__ == '__main__':
    app.run(debug=True)
