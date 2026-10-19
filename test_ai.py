import os
import docx
from google import genai

api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

WORD_DIR = r"D:\LP_Agent\word_reports"
word_files = [f for f in os.listdir(WORD_DIR) if f.endswith(".docx") and not f.startswith("~$")]

if word_files:
    sample_file = word_files[0]
    file_path = os.path.join(WORD_DIR, sample_file)
    doc = docx.Document(file_path)
    original_text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])

    prompt = (
        "You are a professional Vinyl/LP expert and music reviewer. "
        "Please rewrite and enhance the following draft report in Korean. "
        "Requirements:\n"
        "1. Enrich the album data and history.\n"
        "2. Add interesting background stories and track highlights.\n"
        "3. Add listening points for LP/audio enthusiasts.\n\n"
        f"[Draft Content]\n{original_text}"
    )

    print("Connecting to Gemini AI... Please wait.")
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
    )
    print("=" * 60)
    print("AI Report Preview:")
    print("=" * 60)
    print(response.text[:1000] + "\n\n... (truncated) ...")
else:
    print("No docx files found.")
