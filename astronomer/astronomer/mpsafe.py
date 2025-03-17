from contextlib import contextmanager


@contextmanager
def managed_status(
    event_queue,
    status: str,
    initial_state=True,
    final_state=False
):
    event_queue.put(('light', status, initial_state))
    def _callback(state):
        event_queue.put(('light', status, state))

    try:
        yield _callback
    finally:
        event_queue.put(('light', status, final_state))
