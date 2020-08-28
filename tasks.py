import os
from spotdl import Spotdl
import celery
from timeloop import Timeloop
from datetime import timedelta
from Bot import WaBot


tl = Timeloop()
app = celery.Celery("tasks")

REDIS_URL = 'redis://h:pffa2ba6288eb64eebf2bff97dc93ef56f156dd8a2758163f96fb52b5db387a5f@ec2-52-72-186-42.compute-1' \
            '.amazonaws.com:27749'

app.conf.update(BROKER_URL=REDIS_URL)


@app.task
def download_audio(self, song, user):
    path = f'music/{user}'
    if not os.path.exists(path):
        print("Directory not found, Creating...")
        os.mkdir(path)
    args = {
        "song": [song],
        'output_file': path + '/{artist} - {track-name}.{output-ext}'
    }
    print(f'Downloading {song}')
    self.send_message(f'{user}"c.us', 'Downloading your song...')
    with Spotdl(args) as spotdl_handler:
        spotdl_handler.match_arguments()

    return path


@app.task
def work(json):
    bot = WaBot(json)
    return bot.processing()
