import os
from spotdl import Spotdl
import celery
from timeloop import Timeloop
from datetime import timedelta
from Bot import WaBot


tl = Timeloop()
app = celery.Celery("tasks")

REDIS_URL = 'redis://h:p19ab68194c2bd67b1f15134ed24d3a4fc0464585da96534f61f933ffb0007495@ec2-23-23-149-97.compute-1' \
            '.amazonaws.com:27019 '

app.conf.update(BROKER_URL=REDIS_URL,
                CELERY_RESULT_BACKEND=REDIS_URL)


bot = WaBot({"messages": ['1', '2']})


@tl.job(interval=timedelta(seconds=53))
def job_every_minute():
    bot.send_message('254745021668@c.us', '.')


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
def work():
    try:
        tl.start(block=True)
    except RuntimeError:
        pass
