"""
This is a cryptography app 
made by Alek Westover

Caesar cipher your text!

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
def shift(t, x):  # shift all characters
    o = ""
    for c in t.lower():
        v = ord(c)-ord('a')
        if 0 <= v <= 25:
            o += chr(((v+x)%26)+ord('a')) 
        else:
            o += c
    return o

# make it long
def longify(t):
    return ", ".join(list(t))


# --------------- Functions that control the skill's behavior ------------------
# (Basically the only thing I ever need to edit)

def get_welcome_response(help=False):
    """ If we wanted to initialize the session to have some attributes we could
    add those here 

    Note: This will reset the game...
    """
    session_attributes = {"key": False, "msg": False}
    card_title = "Welcome"
    speech_output = "Welcome to the Caesar Cipher skill. "\
        "I can encrypt your text or decrypt it. "\
        "Tell me your message and the shift key."

    if help:
        speech_output = "I shift the letters in your message by a number,"\
        " cycling back from z to a when i overflow. In otherwords this happens in modulus 26."\
        "please input a message and a key. By saying my key is 1, or my message is bob."

    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Say something to encrypt, or say your key!"
    should_end_session = False

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

# read encryption

# changes key attribute
def set_key(intent, session):
    card_title = "Reading key"
    should_end_session=False  # might change...

    cmsg = get_msg(session)
    try:
    	ckey = int(intent['slots']['num']['value'])
    except KeyError:
    	session_attributes = {"key":False, "msg":cmsg}
    	speech_output="please input a key"
    	reprompt_text="please input a key"
    	return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

    if cmsg and ckey:
        scmsg = shift(cmsg, ckey)
        speech_output = "OK. Your encrypted message is " + scmsg + ". Once again, your message is " + longify(scmsg) + ". Thank you"
        reprompt_text = "Done."
        should_end_session = True
    else:
        speech_output = "Your key is " + str(ckey) + ". Now input a message"
        reprompt_text = "Now input a message"

    session_attributes = {"key":ckey, "msg":cmsg}

    # session_attributes["key"] = ckey

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

# changes message attribute
def set_msg(intent, session):
    card_title = "Reading message"
    should_end_session = False  # might be changed if key and message are both fulfilled

    ckey = get_key(session)
    try:
    	cmsg = intent['slots']['msg']['value']
    except KeyError:
    	session_attributes = {"key":ckey, "msg":False}
    	speech_output="please input a message"
    	reprompt_text="please input a message"
    	return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

    if cmsg and ckey:
        scmsg=shift(cmsg, ckey)
        speech_output = "OK. Your encrypted message is " + scmsg + ". Once again, your message is " + ",".join(list(scmsg)) + ". Thank you"
        reprompt_text = "done"
        should_end_session = True
    else:
        speech_output = "Your message is " + cmsg + ". Now input a key"
        reprompt_text = "Now input a key"

    session_attributes = {"key":ckey, "msg":cmsg}

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


# silently retrieves the current text from session, defaults to ""
def get_key(session):
    # if the attribute exists
    if session.get('attributes', {}) and "key" in session.get('attributes', {}):
        return session['attributes']['key']
    else:
        return False

# silently retrieves the current message from session if it is there
def get_msg(session):
    # if the attribute exists
    if session.get('attributes', {}) and "msg" in session.get('attributes', {}):
        return session['attributes']['msg']
    else:
        return False

def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for coming. " \
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

    if intent_name == "AMAZON.HelpIntent" or intent_name == "AMAZON.FallbackIntent":
        return get_welcome_response(help=True)

    elif intent_name == "SetMsgIntent":
        return set_msg(intent, session)

    elif intent_name == "SetKeyIntent":
        return set_key(intent, session)
        
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



