from flask import Flask, render_template_string, request, send_file, jsonify
from flask_cors import CORS
import yt_dlp
import os

app = Flask(__name__)
CORS(app)

DOWNLOAD_FOLDER = 'downloads'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="am">
<head>
    <link rel="manifest" href="/static/manifest.json">
    <meta name="theme-color" content="#e11d48">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Social Media Downloader Pro</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen flex flex-col items-center py-8 px-4">
    <div class="w-full max-w-xl bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl">
        <h1 class="text-2xl font-black text-center mb-1 text-transparent bg-clip-text bg-gradient-to-r from-rose-500 to-indigo-500">Social Downloader Pro</h1>
        <p class="text-slate-400 text-xs text-center mb-6">ፌስቡክ፣ ቲክቶክ እና ሌሎች ቪዲዮዎችን በከፍተኛ ጥራት ያውርዱ</p>

        <form id="downloadForm" class="space-y-4">
            <div>
                <label class="block text-xs font-semibold text-slate-300 mb-1">የቪዲዮ ሊንክ (URL)</label>
                <div class="flex gap-2">
                    <input
                        type="text"
                        id="urlInput"
                        name="url"
                        placeholder="https://..."
                        required
                        class="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl focus:outline-none focus:border-rose-500 text-sm"
                    />
                    <button
                        type="button"
                        id="pasteBtn"
                        class="px-4 bg-slate-700 hover:bg-slate-600 rounded-xl text-xs font-medium transition cursor-pointer"
                    >
                        Paste
                    </button>
                </div>
            </div>

            <div>
                <label class="block text-xs font-semibold text-slate-300 mb-1">የጥራት ምርጫ</label>
                <select
                    name="format"
                    class="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl focus:outline-none focus:border-rose-500 text-sm"
                >
                    <option value="best">ምርጥ ጥራት (Best Video - MP4)</option>
                    <option value="audio">ድምፅ ብቻ (MP3 Audio)</option>
                </select>
            </div>

            <button
                type="submit"
                id="submitBtn"
                class="w-full py-3 bg-gradient-to-r from-rose-600 to-indigo-600 hover:from-rose-500 hover:to-indigo-500 transition font-bold rounded-xl text-sm shadow-lg shadow-rose-600/20 cursor-pointer"
            >
                ቪዲዮ አውርድ
            </button>
        </form>

        <div id="statusMsg" class="mt-4 p-3 bg-slate-800 border border-slate-700 rounded-xl text-xs text-center text-slate-300 hidden"></div>

        <!-- Download History Section -->
        <div class="mt-8 border-t border-slate-800 pt-5">
            <h2 class="text-base font-bold mb-3 text-slate-200">የወረዱ ፋይሎች ታሪክ (History)</h2>
            <div id="historyList" class="space-y-2 max-h-64 overflow-y-auto pr-1">
                <p class="text-xs text-slate-500 text-center py-2">እስካሁን የወረደ ፋይል የለም</p>
            </div>
        </div>
    </div>

    <!-- Video Player Modal / Preview Area -->
    <div id="playerModal" class="fixed inset-0 bg-black/80 hidden flex items-center justify-center p-4 z-50">
        <div class="bg-slate-900 border border-slate-800 w-full max-w-lg rounded-2xl p-4 relative">
            <button id="closeModal" class="absolute top-3 right-3 text-slate-400 hover:text-white font-bold text-lg">✕</button>
            <h3 id="modalTitle" class="text-sm font-bold text-slate-200 mb-3 truncate pr-6">ማጫወቻ</h3>
            <div id="mediaContainer" class="flex justify-center">
                <!-- Dynamic Media Element -->
            </div>
        </div>
    </div>

    <script>
        const pasteBtn = document.getElementById('pasteBtn');
        const urlInput = document.getElementById('urlInput');
        const downloadForm = document.getElementById('downloadForm');
        const statusMsg = document.getElementById('statusMsg');
        const submitBtn = document.getElementById('submitBtn');
        const historyList = document.getElementById('historyList');
        const playerModal = document.getElementById('playerModal');
        const closeModal = document.getElementById('closeModal');
        const modalTitle = document.getElementById('modalTitle');
        const mediaContainer = document.getElementById('mediaContainer');

        // Paste functionality
        pasteBtn.addEventListener('click', async () => {
            try {
                const text = await navigator.clipboard.readText();
                urlInput.value = text;
            } catch (err) {
                alert('ክሊፕቦርድ ማንበብ አልተቻለም');
            }
        });

        // Load History
        async function loadHistory() {
            try {
                const res = await fetch('/history');
                const files = await res.json();
                if (files.length > 0) {
                    historyList.innerHTML = files.map(file => `
                        <div class="flex items-center justify-between bg-slate-800/80 p-3 rounded-xl border border-slate-700/50 text-xs">
                            <span class="truncate max-w-[180px] text-slate-300 font-medium" title="${file}">${file}</span>
                            <div class="flex gap-2">
                                <button onclick="openMedia('${file}')" class="px-2.5 py-1.5 bg-rose-600 hover:bg-rose-500 rounded-lg font-semibold transition text-white cursor-pointer">ጫወት / ክፈት</button>
                                <a href="/downloads/${encodeURIComponent(file)}" download class="px-2.5 py-1.5 bg-indigo-600 hover:bg-indigo-500 rounded-lg font-semibold transition text-white">አውርድ</a>
                            </div>
                        </div>
                    `).join('');
                }
            } catch (e) {
                console.error(e);
            }
        }
        loadHistory();

        // Open Media Modal
        function openMedia(filename) {
            modalTitle.innerText = filename;
            const fileUrl = `/downloads/${encodeURIComponent(filename)}`;
            const ext = filename.split('.').pop().toLowerCase();

            if (['mp3', 'wav', 'm4a'].includes(ext)) {
                mediaContainer.innerHTML = `<audio controls class="w-full"><source src="${fileUrl}" type="audio/${ext}">ብራውዘርዎ ኦዲዮውን መደገፍ አልቻለም።</audio>`;
            } else {
                mediaContainer.innerHTML = `<video controls class="w-full max-h-[350px] rounded-lg"><source src="${fileUrl}" type="video/mp4">ብራውዘርዎ ቪዲዮውን መደገፍ አልቻለም።</video>`;
            }
            playerModal.classList.remove('hidden');
        }

        closeModal.addEventListener('click', () => {
            playerModal.classList.add('hidden');
            mediaContainer.innerHTML = '';
        });

        // Handle Download Form
        downloadForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new URLSearchParams(new FormData(downloadForm));
            
            submitBtn.disabled = true;
            submitBtn.innerText = 'በማውረድ ላይ...';
            statusMsg.classList.remove('hidden');
            statusMsg.innerText = 'ቪዲዮው ከሰርቨር በመውረድ ላይ ነው፣ እባክዎ ይጠብቁ...';

            try {
                const response = await fetch('/download', {
                    method: 'POST',
                    body: formData
                });

                if (response.ok) {
                    statusMsg.innerText = 'ቪዲዮው በስኬት ወርዷል!';
                    loadHistory();
                    urlInput.value = '';
                } else {
                    statusMsg.innerText = 'ማውረድ አልተቻለም። ሊንኩን ወይም ኔትወርክዎን ያረጋግጡ።';
                }
            } catch (err) {
                statusMsg.innerText = 'ስህተት ተፈጥሯል!';
            } finally {
                submitBtn.disabled = false;
                submitBtn.innerText = 'ቪዲዮ አውርድ';
            }
        });
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/history')
def history():
    files = os.listdir(DOWNLOAD_FOLDER)
    files = [f for f in files if not f.startswith('.')]
    return jsonify(sorted(files, reverse=True))

@app.route('/downloads/<path:filename>')
def serve_file(filename):
    return send_file(os.path.join(DOWNLOAD_FOLDER, filename), as_attachment=True)

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    format_type = request.form.get('format', 'best')
    
    ydl_opts = {
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
    }
    
    if format_type == 'audio':
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    else:
        ydl_opts['format'] = 'best'

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if format_type == 'audio':
                filename = os.path.splitext(filename)[0] + '.mp3'
        return jsonify({"status": "success", "filename": os.path.basename(filename)})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
