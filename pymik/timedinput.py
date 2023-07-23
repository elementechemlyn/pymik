import queue
import threading

my_queue = queue.Queue()

def fill_my_queue():
    while True:
        line = input()
        my_queue.put(line)

def get_input(wait_time:int, prompt:str, default:str=None, valid_values:list = []):
    queue_filler_thread = threading.Thread(name="queue_filler", target=fill_my_queue, daemon=True)
    queue_filler_thread.start()

    print(prompt)
    try:
        result = my_queue.get(timeout=wait_time)
    except queue.Empty:
        result = default
    return result

if __name__=="__main__":
    r = get_input(5,"Is this a test (y/N)","N")
    print(r)