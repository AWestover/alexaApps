"""
Code by Alek Westover

This will generate the look up table that will be used by the aws 
lambda function in aws to respond to board states

Note 15 possible hands per player makes 225 possible states
(And even this is overcounting a bit, because 0_0 states get counted 29 times)
"""

"""
libraries
and constants
"""
from pdb import set_trace as tr
import pandas as pd
import os

TABLE_PATH = "table.csv" 


"""
all states must be in this format!!!
Also note it is allways my turn and my hand is listed first
"""
def formatState(state):
	fstate = []
	for i in range(0, len(state)//2):
		fstate += [min(state[i*2 : i*2+2]), max(state[i*2 : i*2+2])]
	return fstate

"""
flips the hand order
"""
def flip_hands(state):
	cur_state = unfreeze(state)
	out = cur_state[2:4] + cur_state[0:2]
	return freeze(out)

"""
turns a list into a standard readable format (formatted too) that is hashable
"""
def freeze(arr):
	a = [str(ai) for ai in formatState(arr)]
	return "_".join(a)

"""
reverts frozen string to list
"""
def unfreeze(frozen):
	out = frozen.split("_")
	out = [int(o) for o in out]
	return out

"""
join 2 hands
"""
def concatHands(h1, h2):
	return h1 + "_" + h2

"""
what are all the possible next moves?
"""
def nextMoves(state):
	moves = set()
	
	# hits
	for i in range(0, 2):
		for j in range(0, 2):
			if state[j]!= 0 and state[2+i]!=0:  # can't hit or get hit with a zero
				cur = state[:]
				cur[2+i] = (cur[2+i] + cur[j]) % 5  # add hands mod 5
				moves.add(freeze(cur))

	# splits
	for j in range(0, 2):
		for off in range(1, state[j]+1):
			cur = state[:]
			cur[j] -= off
			cur[(j+1)%2] += off
			# print(off, cur)
			if cur[(j+1)%2] < 5:  # can't split over 5
				cf = freeze(cur)
				if cf != freeze(state):  # no duplicates!!!!!
					moves.add(cf)

	return list(moves)

# tr()
# nextMoves([1,2,1,2])

"""
is the game over?
(suicide is not allowed so we know you won't really kill 0,1...)
"""
def gameOver(state):
	if state[2]+state[3]==0 or state[0]+state[1]==0:
		return True
	else:	
		return False

"""
are there any win states in an array of states?
-1 means not over
other integer is index of a win
"""
def isWin(states):
	for i in range(0, len(states)):
		if gameOver(unfreeze(states[i])):
			return i 
	return -1

"""
updates the table
"""
def updateTable(prev_s, next_s):
	new_df = {"previous":[], "next": []}
	if os.path.exists(TABLE_PATH):
		old_df = pd.read_csv(TABLE_PATH)
		for key in old_df:
			new_df[key]=list(old_df[key])

	new_df["previous"].append(prev_s)
	new_df["next"].append(next_s)

	new_df = pd.DataFrame.from_dict(new_df)
	new_df.to_csv(TABLE_PATH, index=False)

"""
what hands are possible
"""
possible_hands = []
for i in range(0, 5):
	for j in range(0, 5):
		cf = freeze([i, j])
		if cf not in possible_hands:
			possible_hands.append(cf)

"""
Look at all possible states
"""
ct=0
lastCt= 116

for i in possible_hands:
	for j in possible_hands:
		cur_state = unfreeze(concatHands(i, j))
		if not gameOver(cur_state):

			ct+=1
			print("\n\n\n\n\nCount is ", ct)
			print(concatHands(i, j))
			print("-"*30)
			
			if ct >= lastCt:

				cNexts = nextMoves(cur_state)
				pr = [cNexts[i]+"\t\t\t\t" + str(i) +"\n" for i in range(0, len(cNexts))]
				print("\n".join(pr))

				if len(cNexts) == 1:
					move = 0
				else:
					# 0 indexed choice
					if isWin(cNexts) == -1:
						move = int(input("Move?\t\t").strip())
					else:
						# gets the index of a win
						move = isWin(cNexts)

				updateTable(freeze(cur_state), cNexts[move])

				print(move)


