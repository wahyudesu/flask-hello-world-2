import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client, Client
from dotenv import load_dotenv
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from pinecone.grpc import PineconeGRPC as Pinecone

# Load environment variables
load_dotenv()

# Env
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
pinecone_api_key: str = os.getenv("PINECONE_API_KEY")

# Initialize
pc = Pinecone(api_key=pinecone_api_key)
supabase: Client = create_client(url, key)

# Flask setup
app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return 'Berhasil cuy!'

# Function to convert PDF to Markdown
def convert_pdf(file):
    # Inisialisasi opsi pipeline untuk OCR dan struktur tabel
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = False
    pipeline_options.do_table_structure = True
    pipeline_options.table_structure_options.do_cell_matching = True

    doc_converter = DocumentConverter(
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)}
    )

    conv_result = doc_converter.convert(file)
    
    # Export to Markdown
    result_md = conv_result.document.export_to_markdown()
    return result_md

# Route to handle PDF conversion and saving to Supabase
@app.route('/upload', methods=['POST'])
def upload_file():
    data = request.get_json()  # Mendapatkan data JSON dari request
    name_student = data.get('nameStudent')  # Mengambil nilai 'nameStudent'
    file_paths = data.get('filePaths', [])  # Mengambil nilai 'filePaths' atau default []

    try:
        for file_path in file_paths:
            # Convert PDF to Markdown
            markdown_content = convert_pdf(file_path)
            embedding = pc.inference.embed(model="multilingual-e5-large",inputs=[markdown_content], parameters={"input_type": "passage", "truncate": "END"})
            output_embedding = embedding[0]['values']
            
            # Save to Supabase
            supabase.table('documents').insert({
                'nameStudent': name_student,
                'documentUrl': file_path,
                'embedding': output_embedding 
            }).execute()
        
        # Return a successful response
        return jsonify({'message': 'File berhasil diproses dan disimpan!'}), 200

    except Exception as e:
        # Return any error that occurred during the process
        return jsonify({'error': f'Terjadi kesalahan saat memproses file: {str(e)}'}), 500

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)