from flask import Flask, jsonify, request
import yt_dlp
import requests
import threading
import os
import time

app = Flask(__name__)

# Función para subir archivo a Catbox
def upload_to_catbox(file_path, time="1h"):
    url = "https://litterbox.catbox.moe/resources/internals/api.php"
    with open(file_path, 'rb') as file:
        files = {
            'reqtype': (None, 'fileupload'),
            'time': (None, time),
            'fileToUpload': (file_path, file)
        }
        response = requests.post(url, files=files)
        if response.status_code == 200:
            return response.text  # Retorna el enlace de descarga
        else:
            raise Exception(f"Error uploading to Catbox: {response.status_code} - {response.text}")

# Función para eliminar el archivo después de 5 minutos
def delete_file_after_delay(file_path):
    time.sleep(300)  # Espera 5 minutos (300 segundos)
    try:
        os.remove(file_path)
        print(f"Archivo eliminado: {file_path}")
    except Exception as e:
        print(f"Error al eliminar el archivo: {e}")

@app.route('/download_and_upload_music/<path:video_url>', methods=['GET'])
def download_and_upload_music(video_url):
    try:
        # Configuración de yt-dlp para extraer solo el audio
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',  # Convertir a MP3
                'preferredquality': '192',  # Calidad del audio
            }],
            'outtmpl': '/tmp/%(title)s.%(ext)s',  # Guarda el archivo temporalmente
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            file_path = ydl.prepare_filename(info)
            # Cambiar la extensión del archivo a .mp3
            base, _ = os.path.splitext(file_path)
            mp3_file_path = f"{base}.mp3"

        # Subir el archivo descargado a Catbox
        catbox_url = upload_to_catbox(mp3_file_path)

        # Programar la eliminación del archivo local después de 5 minutos
        threading.Thread(target=delete_file_after_delay, args=(mp3_file_path,)).start()

        # Retornar el enlace de Catbox
        return jsonify({
            "message": "Audio uploaded successfully",
            "catbox_url": catbox_url,
            "local_file": mp3_file_path,
            "deletion_time": "El archivo local se eliminará en 5 minutos"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
