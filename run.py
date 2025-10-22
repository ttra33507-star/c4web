from app import create_app
import os
from flask import send_from_directory

app = create_app()

@app.route('/static/<path:filename>')
def custom_static(filename):
    return send_from_directory(os.path.join(app.root_path, 'static'), filename)

if __name__ == "__main__":
    app.run(debug=True)
