import threading
import time
import os
import sys
from hare import Hare
from semaphore import Semaphore
from values import (
    HARE_NUMBER,
    RACE_DISTANCE,
    MAX_REST_SECONDS
)


class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'


def main():
    countdown()

    ranking = []
    ranking_lock = threading.Lock()
    semaphore = Semaphore(1)
    race_updated = threading.Condition()

    hare_names = {
        0: 'Everton Reis',
        1: 'Riquelme Magalhães',
        2: 'Gustavo Henrique',
        3: 'Tércio',
        4: 'Programador Web'
    }

    hare_colors = {
        0: Colors.BRIGHT_RED,
        1: Colors.BRIGHT_BLUE,
        2: Colors.BRIGHT_GREEN,
        3: Colors.BRIGHT_MAGENTA,
        4: Colors.BRIGHT_YELLOW
    }

    hares, threads = create_hare_threads(
        hare_names, hare_colors, semaphore, ranking, ranking_lock, race_updated)

    monitor_thread = threading.Thread(
        target=monitor_race, args=(hares, race_updated))
    monitor_thread.start()

    start_and_join_threads(threads)
    monitor_thread.join()

    display_ranking(ranking)


def countdown():
    print(f'''{Colors.BRIGHT_CYAN}
 _   _    _    ____  _____   ____      _    ____ _____ 
| | | |  / \  |  _ \| ____| |  _ \    / \  / ___| ____|
| |_| | / _ \ | |_) |  _|   | |_) |  / _ \| |   |  _|  
|  _  |/ ___ \|  _ <| |___  |  _ <  / ___ \ |___| |___ 
|_| |_/_/   \_\_| \_\_____| |_| \_\/_/   \_\____|_____|
{Colors.RESET}''')

    for i in range(3, 0, -1):
        print(f'{Colors.BRIGHT_YELLOW}{i}{Colors.RESET}', end='... ')
        sys.stdout.flush()
        time.sleep(1)
    print(f'{Colors.BRIGHT_GREEN}{Colors.BOLD}GO!{Colors.RESET}')


def hare_behaviour(hare: Hare, semaphore: Semaphore, ranking: list, ranking_lock: threading.Lock, race_updated: threading.Condition):
    while hare.track_distance < RACE_DISTANCE:
        semaphore.acquire()

        try:
            hare.jump()

            if hare.track_distance >= RACE_DISTANCE:
                with ranking_lock:
                    ranking.append(hare)
                    break
        finally:
            with race_updated:
                race_updated.notify()

            semaphore.release()

        hare.rest()


def create_hare_threads(hare_names, hare_colors, semaphore, ranking, ranking_lock, race_updated):
    hares = []
    threads = []
    for i in range(HARE_NUMBER):
        hare = Hare(hare_names.get(i, '???'))
        hare.color = hare_colors.get(i, Colors.WHITE)
        hares.append(hare)
        t = threading.Thread(target=hare_behaviour, args=(
            hare, semaphore, ranking, ranking_lock, race_updated))
        threads.append(t)
    return hares, threads


def start_and_join_threads(threads):
    for t in threads:
        t.start()
    for t in threads:
        t.join()


def display_ranking(ranking):
    print(f'\n{Colors.BOLD}{Colors.BRIGHT_CYAN}🏆 RANKING FINAL 🏆{Colors.RESET}\n')
    position_suffixes = {1: 'st', 2: 'nd', 3: 'rd'}
    medal_colors = {1: Colors.BRIGHT_YELLOW, 2: Colors.WHITE, 3: Colors.YELLOW}
    medals = {1: '🥇', 2: '🥈', 3: '🥉'}

    for position, hare in enumerate(ranking, start=1):
        suffix = position_suffixes.get(position, 'th')
        medal = medals.get(position, '🏃')
        color = medal_colors.get(position, Colors.WHITE)
        print(f'{medal} {color}{Colors.BOLD}{position}{suffix}{Colors.RESET} - {hare.color}{hare.id}{Colors.RESET} ({Colors.CYAN}{hare.jumps} jumps{Colors.RESET})')


def print_race_state(hares: list[Hare]):
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f'{Colors.BOLD}{Colors.BRIGHT_CYAN}🐇 CORRIDA DE LEBRES 🐇{Colors.RESET}\n')

    state = ''
    for hare in hares:
        dist = int(hare.track_distance)
        dist = RACE_DISTANCE if dist > RACE_DISTANCE else dist
        dist_left = RACE_DISTANCE - dist

        progress_bar = f"{hare.color}{'█' * dist}{Colors.WHITE}{'░' * dist_left}{Colors.RESET}"
        state += f'{hare.color}{hare.id_normalized}{Colors.RESET} - {progress_bar}|{Colors.BRIGHT_GREEN}🏁{Colors.RESET}\n'

    print(state)


def monitor_race(hares: list[Hare], race_updated: threading.Condition):
    while any(hare.track_distance < RACE_DISTANCE for hare in hares):
        with race_updated:
            race_updated.wait(MAX_REST_SECONDS)
        print_race_state(hares)


if __name__ == '__main__':
    main()
