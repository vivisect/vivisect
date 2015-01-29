import random

tips = [
    'Hold <shift> to move using the mouse in Function Graph view!',
    'You may drag rows from "List Views" to "Memory Views"',
]

def getRandomTip():
    return random.choice(tips)
