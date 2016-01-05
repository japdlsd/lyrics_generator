#!/usr/bin/python3

import logging
import sys
import itertools
import random
import bisect
import os
import os.path

class Song:
    def __init__(self, text=None):
        self.text = text

    def get_text(self):
        if self.text is None:
            raise Exception("text isn't set")
        return self.text

    def set_text(self, text):
        self.text = text

    def __repr__(self):
        return self.text

def get_songs(directory_name):
    text_filenames = os.listdir(directory_name)
    songs = []
    for filename in text_filenames:
        logging.info("Reading file: " + filename)
        if filename[-1] == "~":
            logging.info("temp file, skipping")
            continue
        with open(os.path.join(directory_name, filename), "r") as f:
            songs.append(Song(f.read()))
    return songs

class Lyrics_generator:
    def __init__(self):
        return

    def train(self, songs):
        return

    def generate(self):
        return Song(None)


class HMM_ngrams(Lyrics_generator):
    def __init__(self, n=3):
        assert(n >= 1)
        logging.debug("n=" + str(n))
        self.n = n

    def train(self, songs):
        # state is either extremal or ngrams
        self.beginning_state = "__BEGIN__"
        self.ending_state = "__END__"
        edges = {self.beginning_state: {}, self.ending_state:{}}

        for song in songs:
            text = song.get_text()
            if len(text) < self.n:
                logging.warning("Text length is less that " + str(self.n))
                continue

            edges[self.beginning_state][text[0:self.n]] = 1 + edges[self.beginning_state].get(text[0:self.n], 0)
            for i in range(len(text) - self.n):
                edges[text[i:i+self.n]] = edges.get(text[i:i+self.n], {})
                edges[text[i:i+self.n]][text[i+1:i+self.n+1]] = 1 + edges[text[i:i+self.n]].get(text[i+1:i+self.n+1], 0)
            edges[text[-self.n:]] = edges.get(text[-self.n:], {})
            edges[text[-self.n:]][self.ending_state] = 1 + edges[text[-self.n:]].get(self.ending_state, 0)
        logging.debug("edges: " + str(edges))

        # generating intervals
        states = {}
        for source in edges:
            boundary = 0
            states[source] = [[], []] # first is boundaries array and second is targets
            for target, value in edges[source].items():
                boundary += value
                states[source][0].append(boundary)
                states[source][1].append(target)
        logging.debug("states: " + str(states))
        logging.info("States number: " + str(len(states)))
        self.states = states

    def generate(self):
        letters = []
        current_state = self.beginning_state
        is_first_state = True

        while True:
            logging.debug("Current state:" + current_state)
            x = random.randrange(self.states[current_state][0][-1])
            pos = bisect.bisect_right(self.states[current_state][0], x)
            if pos is None:
                raise Exception("x is out of range (WUT?)")
            current_state = self.states[current_state][1][pos]
            if is_first_state:
                letters.append(current_state)
                is_first_state = False
            elif current_state == self.ending_state:
                break
            else:
                letters.append(current_state[-1])
        return Song("".join(letters))


def print_usage():
    print("""Usage: ./main.py <directory_name>""")

def main():
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)

    if len(sys.argv) < 2:
        print("No directory name is set.")
        print_usage()
        exit(1)

    directory_name = sys.argv[1]


    logging.info("Getting songs...")
    songs = get_songs(directory_name)
    logging.info("Training...")
    generator = HMM_ngrams(4)
    generator.train(songs)
    logging.info("Generating new song...")
    new_song = generator.generate()
    print(new_song)

if __name__ == "__main__":
    main()