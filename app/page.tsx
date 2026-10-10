'use client';

import { useState } from 'react';

export default function Home() {
  const [url, setUrl] = useState('');
  const [format, setFormat] = useState('best');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleDownload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url) return;

    setLoading(true);
    setMessage('ቪዲዮው በማውረድ ላይ ነው፣ እባክዎ ትንሽ ይጠብቁ...');

    try {
      // ከ Python/Flask ሰርቨር ጋር መገናኘት (Port 5000)
      const response = await fetch('http://localhost:5000/download', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `url=${encodeURIComponent(url)}&format=${format}`,
      });

      if (response.ok) {
        const blob = await response.blob();
        const downloadUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = downloadUrl;
        a.download = 'video';
        document.body.appendChild(a);
        a.click();
        a.remove();
        setMessage('ቪዲዮው በስኬት ወርዷል!');
      } else {
        setMessage('ማውረድ አልተቻለም። ሊንኩን ወይም የዕድሜ ገደቡን ያረጋግጡ።');
      }
    } catch (error) {
      setMessage('ስህተት ተፈጥሯል: ከሰርቨር ጋር መገናኘት አልተቻለም።');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gray-950 text-white flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-md bg-gray-900 border border-gray-800 rounded-2xl p-6 shadow-2xl">
        <h1 className="text-2xl font-bold text-center mb-2 text-rose-500">Social Media Downloader</h1>
        <p className="text-gray-400 text-sm text-center mb-6">የፌስቡክ፣ ቲክቶክ እና ሌሎች ሊንኮችን እዚህ በመለጠፍ ያውርዱ</p>

        <form onSubmit={handleDownload} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-gray-400 mb-1">የቪዲዮ ሊንክ (URL)</label>
            <input
              type="text"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://..."
              required
              className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-xl focus:outline-none focus:border-rose-500 text-sm"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-400 mb-1">የፎርማት ምርጫ</label>
            <select
              value={format}
              onChange={(e) => setFormat(e.target.value)}
              className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-xl focus:outline-none focus:border-rose-500 text-sm"
            >
              <option value="best">ምርጥ ጥራት (Best Video)</option>
              <option value="audio">ድምፅ ብቻ (MP3 Audio)</option>
            </select>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-rose-600 hover:bg-rose-700 transition font-semibold rounded-xl text-sm disabled:opacity-50 cursor-pointer shadow-lg shadow-rose-600/20"
          >
            {loading ? 'በማውረድ ላይ...' : 'ቪዲዮ አውርድ'}
          </button>
        </form>

        {message && (
          <div className="mt-4 p-3 bg-gray-800 border border-gray-700 rounded-xl text-xs text-center text-gray-300">
            {message}
          </div>
        )}
      </div>
    </main>
  );
}
