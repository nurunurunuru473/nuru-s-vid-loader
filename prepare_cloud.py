# requirements.txt መፍጠር
with open('requirements.txt', 'w') as f:
    f.write("flask==3.0.2\nflask-cors==4.0.0\nyt-dlp==2026.8.19\ngunicorn==21.2.0\n")

# Procfile መፍጠር (ለሰርቨር ማስነሻ)
with open('Procfile', 'w') as f:
    f.write("web: gunicorn app:app\n")

print("✓ requirements.txt እና Procfile በስኬት ተፈጥረዋል!")
