import atexit

from apscheduler.triggers.cron import CronTrigger
from flask import Flask
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from rest.report_data import report_data
from extensions import docker_service_maintenance
from config.config import config

# Initiate logging
log_formatter = logging.Formatter("%(asctime)s [%(threadName)s] [%(levelname)s]  %(message)s")
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_handler = root_logger.handlers[0]
root_handler.setFormatter(log_formatter)
logging.getLogger("werkzeug").setLevel(logging.ERROR)
logging.getLogger('apscheduler.executors.default').propagate = False

app = Flask(__name__)
app.register_blueprint(report_data)


def close_scheduler():
    scheduler.shutdown()


def job_process_queue():
    docker_service_maintenance.process_queue()


queue_schedule: list = config.get("DEFAULT", "queue_cron_schedule").split(" ")
scheduler = BackgroundScheduler()
scheduler.add_job(func=job_process_queue,
                  name="Process queue job",
                  trigger=CronTrigger(second=queue_schedule[0], minute=queue_schedule[1], hour=queue_schedule[2], day=queue_schedule[3], month=queue_schedule[4], year=queue_schedule[5]))
scheduler.start()
atexit.register(close_scheduler)

if __name__ == '__main__':
    app.run(host="localhost", port=5090, debug=False, threaded=True)
