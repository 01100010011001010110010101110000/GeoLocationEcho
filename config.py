import multiprocessing
import os

PORT = int(os.environ.get("PORT", 5000))
DEBUG_MODE = int(os.environ.get("DEBUG_MODE", 1))

bind = ":" + str(PORT)
workers = multiprocessing.cpu_count() * 2 + 1
