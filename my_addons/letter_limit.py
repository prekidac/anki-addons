from aqt.main import AnkiQt
from aqt.reviewer import Reviewer
from aqt.utils import tooltip
from typing import Union, Tuple, Any
from anki.utils import stripHTML
import re, html

try:
    with open('/tmp/norma', 'r') as norma:
        limit = int(norma.readline().strip())
except:
    print("Nema normu")
    limit = 5

limit = limit * 300

def letter_count(field_num: int, answers: str) -> int:
    po = re.compile(r"{{c" + str(field_num + 1) + r"::" + r"([\w\d\s,;.\-()'\"]*)")
    match_list = po.findall(answers)
    num = 0
    for match in match_list:
        num += len(match)
    return num

def answers_from_fields(fields: str) -> str:
    """
    Uklanja HTML iz note
    """
    fields = re.sub("(\n|<br ?/?>|</?div>)+", " ", fields)
    fields = stripHTML(fields)
    # ensure we don't chomp multiple whitespace
    fields = fields.replace(" ", "&nbsp;")
    fields = html.unescape(fields)
    fields = fields.replace("\xa0", " ")
    return fields.strip()

def check_time_moveToState(func: callable) -> callable:
    def wrapper(self, state: str, *args, **kwargs):
        today_cards = self.col.db.list("""select cid from revlog
            where id > ? """, (self.col.sched.dayCutoff-86400)*1000)
        
        suma = 0
        for card in today_cards:
            field_num = self.col.db.scalar("""select ord from cards where id == ? """, card)
            nid = self.col.db.scalar("""select nid from cards where id == ? """, card)
            fields = self.col.db.scalar("""select flds from notes where id == ?""", nid)

            answers = answers_from_fields(self.col.media.strip(fields))
            suma += letter_count(field_num, answers)
            
            print(suma)
        
        if suma >= limit:
            if state == "overview":
                state = "deckBrowser"
                tooltip("Zavrsio.")
        func(self, state, *args, **kwargs)
    return wrapper

def check_time_nextCard(func: callable) -> callable:
    def wrapper(self, *args, **kwargs):
        today_cards = self.mw.col.db.list("""select cid from revlog
            where id > ? """, (self.mw.col.sched.dayCutoff-86400)*1000)
        
        suma = 0
        for card in today_cards:
            field_num = self.mw.col.db.scalar("""select ord from cards where id == ? """, card)
            nid = self.mw.col.db.scalar("""select nid from cards where id == ? """, card)
            fields = self.mw.col.db.scalar("""select flds from notes where id == ?""", nid)

            answers = answers_from_fields(self.mw.col.media.strip(fields))
            suma += letter_count(field_num, answers)

        if suma >= limit:
            self.mw.moveToState("deckBrowser")

        func(self, *args, **kwargs)
    return wrapper

AnkiQt.moveToState = check_time_moveToState(AnkiQt.moveToState)
Reviewer.nextCard = check_time_nextCard(Reviewer.nextCard)