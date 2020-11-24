from aqt.main import AnkiQt

def unloadProfileAndExit(self) -> None:
    new = self.col.db.first("""select count() from cards where type == 0""")
    with open('/tmp/novih', 'w') as f:
        f.write('pr_kartica=' + str(new[0]))

    all_sus_nid = self.col.db.list("""select nid from cards where queue == -1 group by nid""")
    today_cid = self.col.db.list("""select cid from revlog where id > ? """, (self.col.sched.dayCutoff-86400)*1000)
    today_nid = []
    for cid in today_cid:
        today_nid.append(self.col.db.scalar(""" select nid from cards where id == ? """, cid))
    to_sus_nid = []
    for nid in all_sus_nid:
        nid_queues = self.col.db.list("""select queue from cards where nid == """ + str(nid))
        for queue in nid_queues:
            if queue != -1:
                break
        else:
            if nid not in today_nid:
                to_sus_nid.append(nid)
    self.col.remove_notes(to_sus_nid)

    self.unloadProfile(self.cleanupAndExit)

AnkiQt.unloadProfileAndExit = unloadProfileAndExit
