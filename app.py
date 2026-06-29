import os
import tempfile
from pathlib import Path

from flask import Flask, render_template_string, request
from markitdown import MarkItDown
from werkzeug.utils import secure_filename


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}
ALLOWED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".xlsx",
    ".pptx",
    ".html",
    ".csv",
    *IMAGE_EXTENSIONS,
}

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024


PAGE = """<!doctype html>
<html lang="my">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>File to Markdown Converter</title>
  <style>
    :root { color-scheme: light; font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
    body { margin: 0; background: #f6f7f9; color: #15171a; }
    main { max-width: 920px; margin: 0 auto; padding: 32px 18px 48px; }
    h1 { margin: 0 0 8px; font-size: clamp(28px, 4vw, 42px); letter-spacing: 0; }
    p { margin: 0 0 22px; color: #4f5661; line-height: 1.55; }
    form, section { background: #fff; border: 1px solid #dde1e7; border-radius: 8px; padding: 18px; }
    label { display: block; font-weight: 700; margin-bottom: 10px; }
    input[type=file] { width: 100%; padding: 12px; border: 1px dashed #aeb6c2; border-radius: 6px; background: #fbfcfd; }
    button { margin-top: 14px; border: 0; border-radius: 6px; background: #1769aa; color: #fff; padding: 10px 14px; font-weight: 700; cursor: pointer; }
    button:disabled { opacity: .65; cursor: wait; }
    .error { margin-top: 14px; color: #9b1c1c; font-weight: 700; }
    .result { margin-top: 18px; }
    textarea { box-sizing: border-box; width: 100%; min-height: 360px; resize: vertical; border: 1px solid #cbd2dc; border-radius: 6px; padding: 12px; font: 14px/1.45 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }
  </style>
</head>
<body>
  <main>
    <h1>File to Markdown Converter</h1>
    <p>Word, Excel, PowerPoint, PDF, HTML, CSV နဲ့ JPG/PNG file တွေကို Markdown အဖြစ် ပြောင်းပေးပါမယ်။</p>

    <form method="post" enctype="multipart/form-data" onsubmit="this.querySelector('button').disabled = true;">
      <label for="file">ပြောင်းလဲလိုသော file ကိုရွေးပါ</label>
      <input id="file" name="file" type="file" accept=".pdf,.docx,.xlsx,.pptx,.html,.csv,.jpg,.jpeg,.png" required>
      <button type="submit">Convert လုပ်မည်</button>
      {% if error %}<div class="error">{{ error }}</div>{% endif %}
    </form>

    {% if markdown is not none %}
      <section class="result">
        <label for="markdown">Markdown ရလဒ်</label>
        <textarea id="markdown" spellcheck="false">{{ markdown }}</textarea>
        <button type="button" onclick="downloadMarkdown()">Markdown File ကို Download ဆွဲမည်</button>
      </section>
      <script>
        function downloadMarkdown() {
          const blob = new Blob([document.getElementById("markdown").value], { type: "text/markdown" });
          const link = document.createElement("a");
          link.href = URL.createObjectURL(blob);
          link.download = {{ download_name|tojson }};
          link.click();
          URL.revokeObjectURL(link.href);
        }
      </script>
    {% endif %}
  </main>
</body>
</html>"""


def convert_upload(uploaded_file):
    filename = secure_filename(uploaded_file.filename or "")
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise ValueError("ဒီ file type ကို မထောက်ပံ့သေးပါ။")

    temp_file_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            uploaded_file.save(temp_file)
            temp_file_path = temp_file.name

        markdown = MarkItDown().convert(temp_file_path).text_content
        if not markdown.strip() and suffix in IMAGE_EXTENSIONS:
            return (
                f"# {filename}\n\n"
                "ဓာတ်ပုံ metadata မတွေ့ပါ။ ဓာတ်ပုံထဲကစာ/အကြောင်းအရာကို ဖတ်ချင်ရင် OCR သို့မဟုတ် Vision LLM ချိတ်ရန်လိုပါသည်။"
            )
        return markdown
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)


@app.route("/", methods=["GET", "POST"])
def index():
    error = None
    markdown = None
    download_name = "converted.md"

    if request.method == "POST":
        uploaded_file = request.files.get("file")
        if not uploaded_file or not uploaded_file.filename:
            error = "File တစ်ခု ရွေးပေးပါ။"
        else:
            try:
                markdown = convert_upload(uploaded_file)
                download_name = f"{secure_filename(uploaded_file.filename)}.md"
            except Exception as exc:
                error = f"Error ဖြစ်နေပါသည်: {exc}"

    return render_template_string(
        PAGE,
        error=error,
        markdown=markdown,
        download_name=download_name,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))
