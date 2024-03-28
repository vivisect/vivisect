import random

tips = [
    'Hold <shift> to move using the mouse in Function Graph view!',
    'You may drag rows from List Views to Memory Views',
    'You can enter any valid python expression into the expression bar at the top'
]

def getRandomTip():
    return random.choice(tips)
