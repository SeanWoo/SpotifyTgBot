import time
time.sleep(5)#ожидание запуска бд на докере

from SpotifyBot.app import *

app = create_app()

app.run(host='0.0.0.0', port=5000)