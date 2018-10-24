"""
This is a math app
made by Alek Westover

Cross some vectors!

"""

# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': output
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



# Crypto Functions------------------------------

# like the whole thing...
def cross(a1,a2,a3,b1,b2,b3):
    i = a2*b3-a3*b2
    j = a3*b1-a1*b3
    k = a1*b2-a2*b1
    return i,j,k

# --------------- Functions that control the skill's behavior ------------------
# (Basically the only thing I ever need to edit)

def get_welcome_response(help=False):
    """ If we wanted to initialize the session to have some attributes we could
    add those here

    Note: This will reset the game...
    """
    session_attributes = {"v1": [], "v2": []}
    card_title = "Welcome"
    speech_output = "Welcome to the Cross product skill. "\
        "I can take the cross product of two vectors. "\
        "Tell me your vectors."

    if help:
        speech_output = "I will take the cross product of the vectors that you provide,"\
        "input three components for the first vector and then three for the second vector."

    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please tell me what your vectors are so that I can take their cross product."
    should_end_session = False

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

# changes vector attributes
def set_vector(intent, session):
    card_title = "Reading vector"
    should_end_session = False  # might change...

    cv1 = get_vector(session, 'v1')
    try:
        a = int(intent['slots']['a']['value'])
        b = int(intent['slots']['b']['value'])
        c = int(intent['slots']['c']['value'])
    except:
        session_attributes = {"v1": cv1, "v2": []}
        speech_output="please input a vector"
        reprompt_text="please input a vector"
        return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

    if a and b and c and a != "?" and b != "?" and c != "?":
        if cv1:
            cv2 = [a,b,c]
            crossed = cross(cv1[0], cv1[1], cv1[2], cv2[0], cv2[1], cv2[2])
            speech_output = "OK. Your cross product is {} {} {}. Thank you".format(crossed[0], crossed[1], crossed[2])
            reprompt_text = "Done."
            should_end_session = True
        else:
            cv1 = [a,b,c]
            cv2 = []
            speech_output = "input your second vector"
            reprompt_text = "input your second vector"
    else:
        cv2 = []
        speech_output = "Please try again"
        reprompt_text = "please try to input your second vector again"

    session_attributes = {"v1":cv1, "v2":cv2}

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


# silently retrieves a vector (v='v1' or 'v2') from session, defaults to ""
def get_vector(session, vn):
    # if the attribute exists
    if session.get('attributes', {}) and vn in session.get('attributes', {}):
        return session['attributes'][vn]
    else:
        return []

def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for coming. " \
                    "Come again soon! "
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

    if intent_name == "AMAZON.HelpIntent" or intent_name == "AMAZON.FallbackIntent" or intent_name=="AMAZON.NavigateHomeIntent":
        return get_welcome_response(help=True)

    elif intent_name == "SetVectorIntent":
        return set_vector(intent, session)

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
