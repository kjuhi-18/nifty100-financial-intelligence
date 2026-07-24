import threading
import time

import requests

URL = "http://127.0.0.1:8000/api/v1/screener?min_roe=15"

times = []


def call_api():

    start = time.perf_counter()

    response = requests.get(URL)

    end = time.perf_counter()

    assert response.status_code == 200

    times.append(end - start)


def test_concurrent_requests():

    threads = []

    overall_start = time.perf_counter()

    for _ in range(10):
        t = threading.Thread(target=call_api)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    overall_end = time.perf_counter()

    total = overall_end - overall_start

    print(f"\nTotal Time: {total:.2f}s")
    print(f"Average: {sum(times)/len(times):.3f}s")

    assert total < 10
