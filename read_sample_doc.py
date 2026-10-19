import os
import docx
WORD_DIR = r"D:\LP_Agent\word_reports"
word_files = [f for f in os.listdir(WORD_DIR) if f.endswith(".docx") and not f.startswith("~$")]
if word_files:
    sample_file = word_files[0]
    file_path = os.path.join(WORD_DIR, sample_file)
    print("=" * 50)
    print("Sample File:", sample_file)
    print("=" * 50)
    doc = docx.Document(file_path)
    full_text = [p.text for p in doc.paragraphs if p.text.strip()]
    print("\n[Word Content Preview - Top 5 Lines]")
    for line in full_text[:5]:
        print("-", line)
    print("\nTotal Paragraphs:", len(full_text))
    print("=" * 50)
else:
    print("No docx files found.")
