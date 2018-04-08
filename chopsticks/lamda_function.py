"""
This is a chopsticks game 
made by Alek Westover

Thank you to the Alexa team for the blueprints that I based this program off of


Information about the game:
Chopsticks is a fun game. 
Although it is often played keeping track of the state on fingers
the game is so simple (with only about about 225 possible states)
that it can easily be played vocally.
The game is both an exercise in visualization (albiet a weak one compared to playing chess in your mind)
and a fun game graph theory game

I have more projects about chopsticks on github https://github.com/AWestover/chopsticks

I strongly recommend looking at the awesome game trees in the graphics directory of the above repo

The repo also has some chopsticks versions that you can play on a computer
WARNING: the game tree for n=5 (regular) chopsticks is pretty big. 
Loading it may severly slow down your computer

"""

import csv
import os

# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }



# Chopsticks Functions------------------------------

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
is the game over?
(suicide is not allowed so we know you won't really kill 0,1...)
"""
def gameOver(state):
    if state[2]+state[3]==0 or state[0]+state[1]==0:
        return True
    else:   
        return False

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


# --------------- Functions that control the skill's behavior ------------------
# (Basically the only thing I ever need to edit)

# retrieve the table from the csv (it is small so just do it fast) 
def get_table():
    table = {}
    PATH = "table.csv"
    with open(PATH) as f:
        freader=csv.reader(f)
        first=True
        for row in freader:
            if first:
                first=False
            else:
                table[row[1]]=row[0]
    return table


def get_welcome_response(help=False):
    """ If we wanted to initialize the session to have some attributes we could
    add those here 
    """
    session_attributes = {"state":"1_1_1_1"}
    card_title = "Welcome"
    # table=get_table()
    speech_output = "Welcome to the chopsticks arena ... " \
                    "Today you will be competing against a robot in a really fun game. Please note "\
                    "my hands are allways listed first. "\
                    "You can place a move by saying something like move 1 2 1 1, "\
                    "where the numbers specify the state"
    #+table["1_1_1_1"] #+ str(os.listdir())
    
    if help:
        speech_output = "You will play chopsticks against a computer in this application" \
                        " in order to say your move say something like move 1 1 1 2" \
                        " following that I will make my move, and we will continue until the game ends "

    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please input your move with a place intent"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

# read out loud the current state
def read_state(intent, session):
    reprompt_text="Input your move with a place (place a move) intent"
    should_end_session=False
    
    session_attributes = {"state": get_state(session)}

    state = session_attributes["state"]
    table = get_table()
    recommendedMove = table[state]

    speech_output = "The current state is " + state.replace("_", " ") + " and" \
                    " the current recommended move is " + recommendedMove.replace("_"," ")
    
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))


# silently retrieves the current state from session, defaults to 1_1_1_1
def get_state(session):
    # if the attribute exists
    if session.get('attributes', {}) and "state" in session.get('attributes', {}):
        return session['attributes']['state']
    else:
        return "1_1_1_1"

# user places a move
# then  alexa automatically places a move
def place(intent, session):
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """
    should_end_session = False
    card_title = "PlaceIntent"
    session_attributes = {"state": get_state(session)}

    state = session_attributes["state"]
    table = get_table()

    # NEED TO GET NUMBERS OUT OF INTENT!!!!!!!!!!!!!!
    try:
        proposed = intent['slots']['number']['value']

        if " " not in proposed and len(proposed) == 4:
            p=list(proposed)
            proposed=" ".join(p)

        speech_output = "old is " + state.replace("_", " ") + " and new is " + proposed
        proposed = freeze(formatState(unfreeze(proposed.replace(" ", "_"))))
        nms=nextMoves(unfreeze(flip_hands(state)))
        nms= [flip_hands(nm) for nm in nms]
        if proposed in nms:
            speech_output += " and this was accepted. "

            if gameOver(unfreeze(proposed)):
                speech_output += " And so you WIN! GREAT JOB. Play again soon"
                should_end_session = True
            else:
                speech_output += "For my move I will update the current state to "
                compMove = table[proposed]
                speech_output += compMove.replace("_", " ")
                session_attributes["state"] = compMove
                if gameOver(unfreeze(compMove)):
                    speech_output+=" AND SO you lose. Play again soon."
                    should_end_session=True
                else:
                    speech_output += ". It is now your turn."
        else:

            fnms = ", ".join(nms)
            fnms = fnms.replace("_", " ")
            speech_output += " but it is not a valid move and was therefore rejected. " \
                            "Please try again. Valid moves include " + fnms


    except KeyError:
        speech_output = "input valid 4 number move"

    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Place a move"

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))
    

def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for playing chopsticks. " \
                    "Play again soon! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """
    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])

def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """
    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()

def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    if intent_name == "AMAZON.HelpIntent":
        return get_welcome_response(help=True)
        
    elif intent_name == "PlaceIntent":
        return place(intent, session)

    elif intent_name == "ReadIntent":
        return read_state(intent, session)
        
        
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])


    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])


