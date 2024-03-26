# Copyright (C) 2024 Warren Usui, MIT License
import json
from solver import rank_picks
from html_gen import make_html

def predictions(tourney):
    def possess(in_string):
        if in_string.endswith('s'):
            return in_string[:-1] + "'s"
        return in_string
    with open(f'{tourney}_reality.json', 'r') as fd:
        in_data = fd.read()
    reality = json.loads(in_data)
    if len(reality) not in [48, 56, 60]:
        print("Can't handle this number of games")
        return
    with open(f'{tourney}_picks.json', 'r') as fd2:
        tdata = fd2.read()
    picks = json.loads(tdata)
    return [rank_picks([reality, picks]), possess(tourney.capitalize())]

def make_page(ptype):
    with open(f'{ptype}_page.html', 'w', encoding='utf-8') as fd:
        fd.write(make_html(predictions(ptype)))

if __name__ == "__main__":
    #make_page('mens')
    make_page('womens')
