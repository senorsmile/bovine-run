from app import app
import json

stash = {
    'app_ver': '0.0.1',
    'log_directory': '~/.ansible/bovine_run/',
    'endpoints': {
        'get_jobs': {
            'get_jobs&most_recent=10': {},
        },
        'get_jobs': {
            'get_jobs&job_number=XX': {},
            'get_job&job_number=XX&from=STARTLINE&until=ENDLINE': {},
        },
    },
}

@app.route('/')
@app.route('/index')
@app.route('/index.html')
def index():
    return json.dumps(
        {
            "stash": stash 
        }
    )

@app.route('/get_job')
def get_job():
    return 'Not yet implemented!'

@app.route('/get_jobs')
def get_jobs():
    return json.dumps(
        {
            "recent_jobs": [
                {   "sample job 1": {
                        "hosts": {
                            "host1": {
                                "changed": 1,
                                "failures": 1,
                                "ok": 1,
                                "skipped": 0,
                                "unreachable": 0,
                            },
                            "host2": {
                                "changed": 0,
                                "failures": 0,
                                "ok": 5,
                                "skipped": 0,
                                "unreachable": 0,
                            },
                        },

                    } 
                },
                {   "sample job 2": {
                        "hosts": {
                            "host1": {
                                "changed": 1,
                                "failures": 1,
                                "ok": 1,
                                "skipped": 0,
                                "unreachable": 0,
                            },
                            "host2": {
                                "changed": 0,
                                "failures": 0,
                                "ok": 5,
                                "skipped": 0,
                                "unreachable": 0,
                            },
                        },

                    } 
                },
                {   "sample job 3": {
                        "hosts": {
                            "host1": {
                                "changed": 1,
                                "failures": 1,
                                "ok": 1,
                                "skipped": 0,
                                "unreachable": 0,
                            },
                            "host2": {
                                "changed": 0,
                                "failures": 0,
                                "ok": 5,
                                "skipped": 0,
                                "unreachable": 0,
                            },
                        },

                    } 
                },
            ]
        }
    )

    return json.dumps( recent_jobs() )
