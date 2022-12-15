"""
    Worker Thread
"""
__author__ = ('Reza Zeiny <rezazeiny1998@gmail.com>',)

import logging
import multiprocessing
from concurrent.futures.thread import ThreadPoolExecutor
from datetime import datetime
from queue import Queue
from threading import Thread, Lock

from func_timeout import func_timeout
from func_timeout.exceptions import FunctionTimedOut

logger = logging.getLogger(__name__)


class Worker(Thread):
    """
        Thread executing tasks from a given tasks queue
    """

    def __init__(self, pool: "ThreadPool", index=None):
        name = f"{pool.name} {index}"
        Thread.__init__(self, name=name)
        self.name = name
        self.pool = pool
        self.is_working = False
        self.daemon = True
        self.start()

    def run(self):
        """
            Run
        """
        while True:
            task_detail, func, args, kwargs = self.pool.tasks.get()
            task_id = task_detail["id"]
            timeout = None
            if type(func) == tuple:
                func, timeout = func
            task_detail["start_dt"] = datetime.now()
            self.is_working = True
            if not callable(func):
                task_detail["status"] = "not_run"
                task_detail["end_dt"] = datetime.now()
                logger.info(f"Task {task_id} is not callable in {self.name}")
                continue
            try:
                task_detail["status"] = "running"
                logger.debug(f"Start running function {func.__name__} in {self.name}.")
                result = func_timeout(timeout, func=func, args=args, kwargs=kwargs)
                task_detail["status"] = "done"
                task_detail["result"] = result
            except FunctionTimedOut:
                logger.error(
                    f"Timeout in function {func.__name__} in task {task_id} thread {self.name} after {timeout}")
                task_detail["status"] = "timeout"
            except Exception as e:
                logger.exception(f"Error in function {func.__name__} in task {task_id} thread {self.name}. e: {e}")
                task_detail["status"] = "error"
            finally:
                self.pool.tasks.task_done()
                logger.debug(f"Finish running function {func.__name__} in thread {self.name}.")
                task_detail["end_dt"] = datetime.now()
                duration = task_detail["end_dt"] - task_detail["insert_dt"]
                if self.pool.log_detail:
                    logger.info(f"Task {task_id} Complete in {self.name} in {duration}")
            self.is_working = False


class ThreadPool:
    """
        Pool of threads consuming tasks from a queue
    """

    def __init__(self, worker_count: int = 4, total_queue: int = 20, *, name: str = __name__,
                 save_detail: bool = False, log_detail: bool = False):
        self.tasks = Queue(total_queue)
        self.name = name
        self.tasks_data = {}
        self.save_detail = save_detail
        self.log_detail = log_detail
        self.tasks_mutex = Lock()
        logger.info(f"{self.name} Create {worker_count} Worker With MAX_QUEUE: {total_queue}")
        self.workers = []
        for index in range(worker_count):
            self.workers.append(Worker(self, index=index))

    def add_task(self, func, *args, **kargs) -> int:
        """Add a task to the queue"""
        self.tasks_mutex.acquire()
        task_id = len(self.tasks_data.keys()) + 1
        task_detail = {
            "id": task_id,
            "status": "pending",
            "insert_dt": datetime.now()
        }
        if self.save_detail:
            self.tasks_data[task_id] = task_detail

        self.tasks.put((task_detail, func, args, kargs))
        self.tasks_mutex.release()
        return task_id

    def wait_completion(self):
        """
            Wait for completion of all the tasks in the queue
        """
        self.tasks.join()

    def get_task_data(self, task_id: int) -> dict:
        """
            Get task data
        """
        return self.tasks_data.get(task_id)

    def get_free_worker(self):
        """
            for get number of free worker
        """
        free_worker = 0
        for worker in self.workers:
            if not worker.is_working:
                free_worker += 1
        return free_worker


class ProcessThreadPool:
    """
        Combine Process and thread
    """

    def __init__(self, max_process: int = 8, max_thread: int = 20):
        self.max_process = max_process
        self.max_thread = max_thread
        self.handler = None

    def process_run(self, iterable: list, handler, job_per_process: int = None):
        """
            for run process
        """
        if not callable(handler):
            return
        self.handler = handler
        process_count = self.max_process
        chunk_size = (len(iterable) // process_count) + 1
        if job_per_process is not None:
            process_count = min(len(iterable) // job_per_process, self.max_process)
            process_count = max(process_count, 1)
            chunk_size = job_per_process

        chunk_path_list: [list] = []
        index = 0
        while index < len(iterable):
            chunk_path_list.append(iterable[index:index + chunk_size])
            index += chunk_size

        pool = multiprocessing.Pool(process_count)
        logger.info(f"start make {process_count} process")
        pool.map(func=self.thread_run, iterable=chunk_path_list)
        pool.close()
        pool.join()

    def thread_run(self, iterable: list, handler=None):
        """
            for run thread
        """
        if handler is None:
            handler = self.handler
        if not callable(handler):
            return
        with ThreadPoolExecutor(max_workers=min(len(iterable), self.max_thread)) as executor:
            executor.map(handler, iterable)
