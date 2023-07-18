import json
from flask import request, Blueprint
from extensions import task_queue

report_data_api = Blueprint('report_data_api', __name__)


@report_data_api.route('/api/status/container', methods=['POST'])
def report_container_status() -> json:
    # Enqueue data for processing
    print(request.json)
    task_queue.put(request.json)
    # Return a response
    return {"status": "success"}
