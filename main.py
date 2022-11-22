from multiprocessing import Queue, Process
from pokebot.simulation import Simulation


def main():
    input_queue: "Queue[int]" = Queue()
    emulator_job = Process(
        target=Simulation,
        args=("roms/heartgold.nds", input_queue),
    )
    emulator_job.start()
    emulator_job.join()


if __name__ == "__main__":
    main()
