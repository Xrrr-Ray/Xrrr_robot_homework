import threading
import time
import hiwonder.ActionGroupControl as AGC

class WalkController(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name
        self._run_event = threading.Event()
        self._run_event.set()
        self._stop_event = threading.Event()

    def run(self):
        while not self._stop_event.is_set():
            if self._run_event.wait():
                AGC.runActionGroup('go_forward_one_step')

    def pause(self):
        self._run_event.clear()
        AGC.stopActionGroup()

    def resume(self):
        self._run_event.set()

    def stop(self):
        self._stop_event.set()
        self._run_event.set()


if __name__ == "__main__":
    walk_controller = WalkController("WalkController")
    walk_controller.start()
    time.sleep(3)
    walk_controller.pause()
    time.sleep(2)
    walk_controller.resume()
    time.sleep(3)
    walk_controller.stop()
