import os

# 1. 1. static ፎልደር መፍጠር እና manifest.json ማስቀመጥ
os.makedirs('static', exist_ok=True)

manifest_content = '''{
  "name": "Nuru's Video Downloader",
  "short_name": "VideoDownloader",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#030712",
  "theme_color": "#e11d48",
  "icons": [
    {
      "src": "https://img.icons8.com/fluency/96/download.png",
      "sizes": "96x96",
      "type": "image/png"
    },
    {
      "src": "https://img.icons8.com/fluency/512/download.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}
'''

with open('static/manifest.json', 'w', encoding='utf-8') as f:
    f.write(manifest_content)

print("✓ manifest.json በስኬት ተፈጥሯል!")

# 2. app.py ፋይል ውስጥ የ PWA ሜታ ታጎችን ማካተት
if os.path.exists('app.py'):
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # ከ <head> በኋላ የ PWA ኮዶችን ማስገባት
    pwa_meta = '''    <link rel="manifest" href="/static/manifest.json">
    <meta name="theme-color" content="#e11d48">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">'''

    if '<link rel="manifest"' not in content:
        if '<head>' in content:
            content = content.replace('<head>', f'<head>\n{pwa_meta}')
            with open('app.py', 'w', encoding='utf-8') as f:
                f.write(content)
            print("✓ app.py ፋይል በ PWA ታጎች ተዘምኗል!")
        else:
            print("! ማስጠንቀቂያ: በ app.py ውስጥ <head> መለያ አልተገኘም አብነትዎን ያረጋግጡ።")
    else:
        print("i PWA ታጎች አስቀድሞ በ app.py ውስጥ ተካትተዋል።")
else:
    print("! app.py ፋይል አልተገኘም።")
