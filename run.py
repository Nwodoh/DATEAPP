from app import create_app
from flask_cors import CORS

flask_app = create_app()

if __name__ == '__main__':
    flask_app.run(debug=True) # 'debug=True' Only in development