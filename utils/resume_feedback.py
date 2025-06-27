import re
from utils.local_llm import get_completion

# Analyze key sections in resume
def analyze_resume(text):
    feedback = []
    missing_sections = []

    required_sections = ["Objective", "Education", "Experience", "Skills", "Projects"]
    for section in required_sections:
        if section.lower() not in text.lower():
            missing_sections.append(section)

    score = max(10 - len(missing_sections), 0)

    if missing_sections:
        for section in missing_sections:
            feedback.append(f"⚠️ Your resume is missing: {section}")
    else:
        feedback.append("✅ Great job! Your resume includes all key sections.")

    return {
        "score": score,
        "feedback": feedback,
        "missing_sections": missing_sections
    }

# Clean non-ASCII characters (use in PDF export if needed)
def clean_text(text):
    return re.sub(r'[^\x00-\x7F]+', ' ', text)

# Suggest improvements using LLM for top N relevant lines
def suggest_improvements(resume_text, progress_tracker=None, max_lines=6):
    # Clean and split lines
    raw_lines = [line.strip() for line in resume_text.strip().split("\n") if line.strip()]
    
    # Filter out lines that are too short or meaningless
    lines = [line for line in raw_lines if len(line.split()) > 3]

    # Sort by length (prioritize meaningful lines)
    lines.sort(key=len, reverse=True)
    selected_lines = lines[:max_lines]

    suggestions = []
    total = len(selected_lines)

    if not selected_lines:
        return [("No valid input found", "❌ No resume content was suitable for improvement.")]

    for idx, line in enumerate(selected_lines):
        prompt = f"Please suggest a professional and concise improvement for the following resume line:\n\nOriginal: {line}\nImproved:"
        try:
            print("🧠 Prompting LLM with:", prompt[:100])
            improved = get_completion(prompt)
            print("✅ Got:", improved[:80])
            improved_clean = improved.strip()

            # Optional: Remove repeated "Original:" / "Improved:" from output if LLM includes it again
            improved_clean = re.sub(r'Improved:\s*', '', improved_clean, flags=re.IGNORECASE)
            suggestions.append((line, improved_clean))
        except Exception as e:
            print("❌ ERROR:", str(e))
            suggestions.append((line, f"❌ Error improving line: {str(e)}"))

        if progress_tracker is not None:
            progress_tracker["progress"] = int(((idx + 1) / total) * 100)

    return suggestions

# Optional: extract cleaned improved line if response is numbered
def extract_improved_line(response, line_number):
    match = re.search(rf"{line_number}\.\s*(.*)", response)
    return match.group(1).strip() if match else response.strip()
