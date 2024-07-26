import threading
from queue import Queue
from concurrent.futures import Future


class TaskQueue:
    def __init__(self):
        self.queue = Queue()
        self.worker_thread = threading.Thread(target=self._worker)
        self.worker_thread.daemon = True
        self.worker_thread.start()

    def add_task(self, task):
        future = Future()
        self.queue.put((task, future))
        return future

    def _worker(self):
        while True:
            task, future = self.queue.get()
            try:
                result = task()
                future.set_result(result)
            except Exception as e:
                future.set_exception(e)
            finally:
                self.queue.task_done()


global_task_queue = TaskQueue()


def method_wrapper(instance, method, *args, **kwargs):
    def task():
        print(
            f"Executing {method.__name__} for instance {id(instance)} with args: {args} and kwargs: {kwargs}"
        )
        return method(*args, **kwargs)

    return global_task_queue.add_task(task)


def queue_decorator(func):
    def wrapper(self, *args, **kwargs):
        return method_wrapper(self, func, self, *args, **kwargs)

    return wrapper
