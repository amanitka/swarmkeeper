import atexit
from flask import Flask
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from report_data_api import report_data_api
from extensions import docker_service_maintenance

# Initiate logging
log_formatter = logging.Formatter("%(asctime)s [%(threadName)s] [%(levelname)s]  %(message)s")
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_handler = root_logger.handlers[0]
root_handler.setFormatter(log_formatter)
logging.getLogger("werkzeug").setLevel(logging.ERROR)


app = Flask(__name__)
app.register_blueprint(report_data_api)


def close_scheduler():
    scheduler.shutdown()


def job_process_queue():
    logging.info("Execute job")
    docker_service_maintenance.process_queue()


scheduler = BackgroundScheduler()
scheduler.add_job(job_process_queue, 'interval', seconds=10)  # Run the job every 10 minutes
scheduler.start()
atexit.register(close_scheduler)


if __name__ == '__main__':
    app.run(host="localhost", port=8090, debug=False, threaded=True)
