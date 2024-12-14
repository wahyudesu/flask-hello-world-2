from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# Set folder for uploads
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

folders_list = []

@app.route('/')
def home():
    return 'API Berjalan dengan baik!'

# Create Folder
@app.route('/folders', methods=['POST'])
def create_folder():
    data = request.json
    folder_name = data.get('name')

    if not folder_name or '/' in folder_name or '\\' in folder_name:
        return jsonify({'error': 'Invalid folder name'}), 400

    folder_path = os.path.join(UPLOAD_FOLDER, folder_name)
    if os.path.exists(folder_path):
        return jsonify({'error': 'Folder already exists'}), 400

    try:
        os.makedirs(folder_path)
        folders_list.append(folder_name)
        return jsonify({'message': 'Folder created successfully', 'folders': folders_list}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# List Folders
@app.route('/folders', methods=['GET'])
def list_folders():
    try:
        folders = [f for f in os.listdir(UPLOAD_FOLDER) if os.path.isdir(os.path.join(UPLOAD_FOLDER, f))]
        return jsonify({'folders': folders}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Update Folder
@app.route('/folders/<old_name>', methods=['PUT'])
def update_folder(old_name):
    data = request.json
    new_name = data.get('new_name')

    if not new_name or '/' in new_name or '\\' in new_name:
        return jsonify({'error': 'Invalid new folder name'}), 400

    old_path = os.path.join(UPLOAD_FOLDER, old_name)
    new_path = os.path.join(UPLOAD_FOLDER, new_name)

    if not os.path.exists(old_path):
        return jsonify({'error': 'Folder does not exist'}), 404

    if os.path.exists(new_path):
        return jsonify({'error': 'New folder name already exists'}), 400

    try:
        os.rename(old_path, new_path)
        return jsonify({'message': 'Folder updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Delete Folder
@app.route('/folders/<folder_name>', methods=['DELETE'])
def delete_folder(folder_name):
    folder_path = os.path.join(UPLOAD_FOLDER, folder_name)

    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        return jsonify({'error': 'Folder does not exist'}), 404

    try:
        os.rmdir(folder_path)
        return jsonify({'message': 'Folder deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': 'Make sure the folder is empty'}), 500

# Upload File
@app.route('/files/<folder_name>', methods=['POST'])
def upload_file(folder_name):
    folder_path = os.path.join(UPLOAD_FOLDER, folder_name)
    if not os.path.exists(folder_path):
        return jsonify({'error': 'Folder does not exist'}), 404

    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    file_path = os.path.join(folder_path, file.filename)
    try:
        file.save(file_path)
        return jsonify({'message': 'File uploaded successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# List Files in Folder
@app.route('/files/<folder_name>', methods=['GET'])
def list_files(folder_name):
    folder_path = os.path.join(UPLOAD_FOLDER, folder_name)
    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        return jsonify({'error': 'Folder does not exist'}), 404

    try:
        files = [{'name': f, 'size': os.path.getsize(os.path.join(folder_path, f))}
                 for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        return jsonify({'files': files}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Delete File
@app.route('/files/<folder_name>/<file_name>', methods=['DELETE'])
def delete_file(folder_name, file_name):
    folder_path = os.path.join(UPLOAD_FOLDER, folder_name)
    file_path = os.path.join(folder_path, file_name)

    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        return jsonify({'error': 'File does not exist'}), 404

    try:
        os.remove(file_path)
        return jsonify({'message': f'File {file_name} deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
