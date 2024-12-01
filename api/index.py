from flask import Flask, request, jsonify
from flask_cors import CORS
import PyPDF2

app = Flask(__name__)
CORS(app)


@app.route('/')
def home():
    return 'Berhasil cuy!'

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    pdf_file = request.files['file']

    try:
        # Parse the PDF file
        reader = PyPDF2.PdfReader(pdf_file)
        text_content = ""

        # Extract text from each page
        for page in reader.pages:
            text_content += page.extract_text() + "\n"

        # Convert the extracted text to a simple Markdown format
        markdown_text = f"### Extracted Text from PDF\n\n{text_content}"

        return jsonify({'markdown': markdown_text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Program sedang berjalan...")  # Tambahkan pesan
    app.run(debug=True)
