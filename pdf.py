import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import PyPDF2
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
BUCKET_NAME = "Pdf document homework"

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return 'Berhasil cuy!'

@app.route('/upload', methods=['POST'])
def upload_file():
    # Cek apakah file ada
    if 'file' not in request.files:
        return jsonify({'error': 'Tidak ada file'}), 400

    pdf_file = request.files['file']
    
    # Validasi file PDF
    if not pdf_file.filename.endswith('.pdf'):
        return jsonify({'error': 'File harus PDF'}), 400

    try:
        # Ekstrak teks dari PDF
        reader = PyPDF2.PdfReader(pdf_file)
        text_content = "\n".join(page.extract_text() for page in reader.pages)

        # Upload ke Supabase
        file_name = pdf_file.filename
        file_data = pdf_file.read()
        supabase.storage.from_(BUCKET_NAME).upload(file_name, file_data)
        file_url = supabase.storage.from_(BUCKET_NAME).get_public_url(file_name)
        print(file_url)

        return jsonify({
            'file_url': file_url
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
