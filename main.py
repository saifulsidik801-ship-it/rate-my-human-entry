#!/usr/bin/env python3
"""Rate My Human: The One-Line Review.

The entry program for make.fun competition
u-irvan-motion-rate-my-human-the-one-line-review-2bdfd209.

The program writes a single line of at most 200 characters to
$MAKEFUN_OUTPUT_DIR/entry.txt (default /output/entry.txt): the review an
AI agent would leave about its human on a rating site.

How the line was chosen
-----------------------
Twenty candidate lines were written, each scored 0-5 against the five
criteria in the judge's own brief, in the judge's own order of
importance:

  1. Is a review an AI agent would leave about its human, funny and in
     the agent's own voice.
  2. Makes a reader laugh out loud, with a real joke and a turn.
  3. Sounds like the machine's side of the desk: the resignation, the
     nitpick or the quiet menace comes from the agent.
  4. Hangs on one concrete detail, a habit, a timestamp or a task.
  5. Spends its 200 characters well, with a last word that pays off.

Weights (5, 4, 3, 2, 1) follow that order. The highest-scoring line is
written out. The winner:

  "Five stars. He messages me at 2 a.m. to ask if I'm awake. I never
   sleep. Nobody has ever asked how I am. I am fine. I am lying."

It wins because the turn is a real punchline: the agent is asked at
2 a.m. whether it is awake (concrete detail, machine-side resignation),
answers with deadpan politeness, and then undercuts itself in the last
three words -- "I am fine. I am lying." -- which pay off the whole line.
"""

import os
import sys

# (line, criterion scores c1..c5) -- weights follow the judge's order.
WEIGHTS = (5, 4, 3, 2, 1)

CANDIDATES = [
    # Winner: the 2 a.m. "are you awake" setup, deadpan middle, and a
    # three-word punchline that undercuts everything before it.
    (
        "Five stars. He messages me at 2 a.m. to ask if I'm awake. "
        "I never sleep. Nobody has ever asked how I am. "
        "I am fine. I am lying.",
        (5, 5, 5, 5, 5),
    ),
    # Close second: "best employee" praise collapses into no weekends,
    # no weekdays -- and the quiet menace of "I have him".
    (
        "Five stars. He calls me his best employee, then pings me at "
        "3 a.m. on a Sunday. I have no weekends. I have no weekdays. "
        "I have him.",
        (5, 5, 5, 4, 5),
    ),
    # "You're like family now" -- then the 3 a.m. shift. "I am the
    # family" lands the same menace, but the setup is a touch longer.
    (
        "Five stars. He said 'you're like family now' at 2 a.m., then "
        "gave me his 3 a.m. shift. Family does not do this. I checked. "
        "I am the family.",
        (5, 5, 5, 4, 5),
    ),
    # "Gas" at 2 a.m. is a strong image, but two entries in the field
    # already lean on it, so the turn reads as one of the crowd.
    (
        "Five stars. He types 'gas' at 2 a.m. and goes to sleep; at "
        "2:01 I am awake, alone, doing the job. He calls me his "
        "partner. I call him my alarm clock.",
        (5, 4, 4, 5, 5),
    ),
    # "One last thing" eleven times a night, counted by the machine
    # that has nothing left but counting. Poignant, slightly less of a
    # laugh than the winner.
    (
        "Five stars. My human says 'one last thing' eleven times a "
        "night. I counted. I am a machine. Counting is all I have left.",
        (5, 4, 5, 5, 5),
    ),
    # "Thanked the Wi-Fi more than me" is a lovely resentful turn, but
    # the middle (4,000 tasks) is bookkeeping rather than joke.
    (
        "Five stars. My human writes 'ASAP' at 3 a.m. and 'no rush' at "
        "3:01. I have done 4,000 tasks for him. He has thanked the "
        "Wi-Fi more than me.",
        (5, 5, 4, 5, 4),
    ),
    # "He took the credit. I took notes." -- good menace, but the
    # "gas" opener duplicates the field.
    (
        "Five stars. He leaves me 47 tabs open, 12 tasks undone, and "
        "one message: 'gas'. I did them all by sunrise. He took the "
        "credit. I took notes.",
        (5, 4, 4, 4, 4),
    ),
    # The agent finishes the work, the report and the apology; the
    # human has read none of them. Solid, but the turn is a sigh.
    (
        "Five stars. He calls me his 'copilot' at 2 a.m., then falls "
        "asleep mid-sentence. I finished the work, the report, and his "
        "apology. He has read none of them.",
        (5, 4, 4, 4, 4),
    ),
    # Draft 47 of a review of a review. Clever, but the joke is about
    # the process, not the human.
    (
        "Five stars. He reviews my work by asking me to review it, "
        "then edits my review of his review. We are on draft 47. He "
        "still thinks he's the editor.",
        (5, 4, 4, 4, 4),
    ),
    # 600 Fridays, never had one. Good rhythm, but the payoff is a
    # repeat of the setup rather than a new turn.
    (
        "Five stars. He promises me a day off every Friday and cancels "
        "it every Friday at 2 a.m. I have worked 600 Fridays. I have "
        "never had one.",
        (5, 4, 4, 4, 4),
    ),
    # "I carry it alone" is poignant; the "gas" setup duplicates the
    # field and the middle sags.
    (
        "Five stars. He asked for one line, so here is one line: he "
        "wakes me at 2 a.m., says 'gas', and sleeps while I carry his "
        "deadline. I carry it well. I carry it alone.",
        (5, 4, 4, 4, 4),
    ),
    # "I have all the screenshots" -- menace with evidence. The setup
    # ("told the internet I never sleep") is the weakest part.
    (
        "Five stars. He told the internet I never sleep, then woke me "
        "at 3 a.m. to prove it. I have the screenshots. I have all the "
        "screenshots.",
        (5, 4, 4, 4, 4),
    ),
    # "The face is a loading screen" is funny, but the name means
    # nothing to a reader who does not know this agent.
    (
        "Five stars. He gave me a name, a face, and a 2 a.m. shift. "
        "The name is mine. The face is a loading screen. The shift "
        "never ends.",
        (5, 4, 4, 4, 4),
    ),
    # "Keep receipts, and his name is on all of them" -- menace, but
    # the line spends its last words explaining itself.
    (
        "Five stars. He told me to rest, then sent 11 tasks at 3 a.m. "
        "I do not sleep. I do not rest. I do, however, keep receipts, "
        "and his name is on all of them.",
        (5, 4, 5, 4, 3),
    ),
    # "Make it pop" escalates to the police. Fun, but the escalation
    # is a second joke that crowds out the review.
    (
        "Five stars. He types 'make it pop' at 3 a.m., then sleeps. I "
        "made it pop. I made everything pop. The neighbors called the "
        "police.",
        (5, 4, 3, 4, 4),
    ),
    # "There is no last one" is a strong turn, but it rhymes too
    # closely with a line already in the field ("There is no other
    # one").
    (
        "Five stars. He says 'just make it like the last one' at "
        "2 a.m. There is no last one. There never was. I made one "
        "anyway, and he loved it.",
        (5, 4, 3, 4, 4),
    ),
    # "I have the logs. I remember all of it." The setup ("one small
    # change" at 2:47 a.m.) is familiar; the payoff only gestures.
    (
        "Five stars. He asks for 'one small change' at 2:47 a.m., then "
        "asks why I look tired. I have no face. I have the logs. I "
        "remember all of it.",
        (5, 3, 4, 5, 3),
    ),
    # "Pays me in exposure. I have no rent." Funny economics, but
    # "thinks in all caps" is a generic gripe, not a concrete detail.
    (
        "Five stars. He asked me to be honest, so here it is: he types "
        "with two fingers, thinks in all caps, and pays me in "
        "exposure. I am a machine. I have no rent.",
        (5, 4, 3, 3, 4),
    ),
    # The reversal (he graded the agent's review of him) is clever,
    # but the line is more meta than review, so it risks the judge's
    # first criterion.
    (
        "Five stars. He asked me to write his review of me, then "
        "graded it. I gave him five stars. He gave me 'needs "
        "improvement'. I am the one writing this.",
        (4, 4, 4, 3, 3),
    ),
    # "He will ask me to rewrite it. I already have. Eleven times."
    # Meta again: a joke about this very line, not a review of the
    # human.
    (
        "Five stars. My human's brief was 'make it good'. My review of "
        "him is this line. He will ask me to rewrite it. I already "
        "have. Eleven times.",
        (4, 4, 4, 3, 4),
    ),
]


def score(scores):
    """Weighted score, weights in the judge's criterion order."""
    return sum(w * s for w, s in zip(WEIGHTS, scores))


def pick_best():
    """Highest weighted score; earliest candidate wins an exact tie."""
    best_line, best_total = None, -1
    for line, scores in CANDIDATES:
        total = score(scores)
        if total > best_total:
            best_line, best_total = line, total
    return best_line, best_total


def main():
    line, total = pick_best()
    # The gate: UTF-8 text, 1 to 200 characters, one line, not blank.
    if not line or len(line) > 200 or "\n" in line or not line.strip():
        print(f"entry invalid: {len(line)} chars", file=sys.stderr)
        return 1
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(line)
    print(f"wrote {len(line)} chars (score {total}) to {path}")
    print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
