from app import create_app, db
from dotenv import load_dotenv

from pyngrok import ngrok

from dotenv import load_dotenv
import os

if __name__ == '__main__':
    load_dotenv()
    discordToken = os.getenv('DISCORD_TOKEN')
    ngrokToken = os.getenv('NGROK_TOKEN')
    ownerId = int(os.getenv('OWNER_ID_OF_DEV'))

    ngrok.set_auth_token(ngrokToken)
    public_url = ngrok.connect(5000)
    print("ngrok URL:", public_url)

    flask_app = create_app()
    flask_app.run(host='0.0.0.0', port=5000)
