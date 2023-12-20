import threading


def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()
