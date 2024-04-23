import json
from .escape_room import EscapeRoom
from .scenario import Scenario
from .object import Object
from .state import State
from .utils import Position, Size
from .precondition_tree import PreConditionOperatorAnd, PreConditionOperatorNot, PreConditionOperatorOr, PreConditionTree, PreConditionVar
from .event import Event
from .precondition import EventPreConditionAfterTime, EventPreConditionAfterEvent, EventPreConditionWhenObjectIsState, EventPreConditionItemIsInUse , EventPreConditionClickedObject, EventPreConditionClickedNotObject
from .poscondition import EventPosConditionSocketConnection, EventPosConditionTransition, EventPosConditionSlidePuzzle, EventPosConditionPuzzle, EventPosConditionSequence, EventPosConditionConnections, EventPosConditionMultipleChoice,EventPosConditionMoveObject, EventPosConditionPlaySound, EventPosConditionChangeScenario, EventPosConditionObjChangePosition, EventPosConditionObjChangeSize, EventPosConditionObjChangeState, EventPosConditionEndGame,EventPosConditionDeleteItem, EventPosConditionObjPutInventory,EventPosConditionShowMessage,EventPosConditionQuestion
from .sound import Sound
from .game_state import GameState
from .transition import Transition
import sys

def load_precondition(precondition):
    type = precondition['type']
    if type == "CLICKED_OBJECT":
        object_id = precondition['object']
        event_precondition = EventPreConditionClickedObject(object_id)
    elif type == "CLICKED_NOT_OBJECT":
        object_id = precondition['object']
        event_precondition = EventPreConditionClickedNotObject(object_id)
    elif type == "WHEN_OBJECT_IS_STATE":
        object_id = precondition['object']
        state_id = precondition['state']
        event_precondition = EventPreConditionWhenObjectIsState(object_id,state_id)
    elif type == "AFTER_EVENT":
        after_event_id = precondition['event']
        event_precondition = EventPreConditionAfterEvent(object_id,after_event_id)
    elif type == 'ITEM_IS_IN_USE':
        item_id = precondition['item']
        event_precondition = EventPreConditionItemIsInUse(item_id)
    elif type == 'AFTER_TIME':
        time = precondition['time']
        event_precondition = EventPreConditionAfterTime(time)
    
    return event_precondition

def load_preconditions(preconditions):
    if 'operator' in preconditions:
        operator = preconditions['operator']
        left = load_preconditions(preconditions['left'])
        right = load_preconditions(preconditions['right']) if 'right' in preconditions and preconditions['right'] is not None else None
        if operator == 'AND':
            return PreConditionOperatorAnd(left,right)
        elif operator == 'OR':
            return PreConditionOperatorOr(left,right)
        elif operator == 'NOT':    
            return PreConditionOperatorNot(left)
    elif 'var' in preconditions:
        var = preconditions['var']
        return PreConditionVar(load_precondition(var))

    else: 
        return None

def load_posconditions(data_posconditions):
    pos_conditions = []
    for data_action in data_posconditions:
        type = data_action['type']
        if type == "END_GAME":
            event_poscondition = EventPosConditionEndGame()
        elif type == "OBJ_CHANGE_STATE":
            object_id = data_action['object']
            state_id = data_action['state']
            event_poscondition = EventPosConditionObjChangeState(object_id,state_id)
        elif type == 'OBJ_CHANGE_POSITION':
            object_id = data_action['object']
            (pos_x,pos_y) = data_action['position']
            event_poscondition = EventPosConditionObjChangePosition(object_id,Position(pos_x,pos_y))
        elif type == 'OBJ_CHANGE_SIZE':
            object_id = data_action['object']
            (size_x,size_y) = data_action['size']
            event_poscondition = EventPosConditionObjChangeSize(object_id,Size(size_x,size_y))
        elif type == 'SHOW_MESSAGE':
            message = data_action['message']
            pos_x,pos_y = data_action['position']
            event_poscondition = EventPosConditionShowMessage(message,Position(pos_x,pos_y))
        elif type == 'QUESTION':
            code = data_action['code']
            message = data_action['message']
            sucess = data_action['sucess']
            fail = data_action['fail']
            (pos_x,pos_y) = data_action['position']
            event_poscondition = EventPosConditionQuestion(code,message,sucess,fail,Position(pos_x,pos_y))
        elif type == "OBJ_PUT_INVENTORY":
            object_id = data_action['object']
            event_poscondition = EventPosConditionObjPutInventory(object_id)
        elif type == 'CHANGE_SCENARIO':
            scenario_id = data_action['scenario']
            event_poscondition = EventPosConditionChangeScenario(scenario_id)
        elif type == "DELETE_ITEM":
            item_id = data_action['item']
            event_poscondition = EventPosConditionDeleteItem(item_id)
        elif type == 'PLAY_SOUND':
            sound_id = data_action['sound']
            source_id = data_action['source_id']
            source_type = data_action['source_type']
            event_poscondition = EventPosConditionPlaySound(sound_id,source_id,source_type)
        elif type == 'MOVE_OBJECT':
            object_id = data_action['object']
            object_trigger = data_action['object_trigger']
            sucess = data_action['sucess']
            fail = data_action['fail']
            event_poscondition = EventPosConditionMoveObject(object_id,object_trigger,sucess,fail)
        elif type == 'MULTIPLE_CHOICE':
            question = data_action['question']
            answer = data_action['answer']
            multiple_choices = data_action['multiple_choices']
            sucess = data_action['sucess']
            fail = data_action['fail']
            event_poscondition = EventPosConditionMultipleChoice(question,answer,multiple_choices,sucess,fail)
        elif type == 'CONNECTIONS':
            question = data_action['question']
            connections = data_action['connections']
            sucess = data_action['sucess']
            fail = data_action['fail']
            event_poscondition = EventPosConditionConnections(connections,question,sucess,fail)
        elif type == 'SEQUENCE':
            question = data_action['question']
            order = data_action['order']
            sucess = data_action['sucess']
            fail = data_action['fail']
            event_poscondition = EventPosConditionSequence(order,question,sucess,fail)        
        elif type == 'PUZZLE':
            image = data_action['puzzle']
            sucess = data_action['sucess']
            event_poscondition = EventPosConditionPuzzle(image,sucess)
        elif type == 'SLIDEPUZZLE':
            image = data_action['image']
            sucess = data_action['sucess']
            event_poscondition = EventPosConditionSlidePuzzle(image,sucess)
        elif type == 'TRANSITION':
            transition = data_action['transition']
            event_poscondition = EventPosConditionTransition(transition)
        elif type == 'SOCKET_CONNECTION':
            host = data_action['host']
            port = data_action['port']
            text = data_action['text']
            sucess = data_action['sucess']
            fail = data_action['fail']
            event_poscondition = EventPosConditionSocketConnection(host,port,text,sucess,fail)
        pos_conditions.append(event_poscondition)
    return pos_conditions

def load_transitions(data_transitions):
    transitions = []
    for data_transition in data_transitions:
        id = data_transition['id']
        background = data_transition['background']
        music = data_transition['music'] if 'music' in data_transition else None
        story = data_transition['story'] if 'story' in data_transition else None
        next_scenario = data_transition['next_scenario'] if 'next_scenario' in data_transition else None
        next_transition = data_transition['next_transition'] if 'next_transition' in data_transition else None
        transition = Transition(id=id,background=background,music=music,story=story,next_scenario=next_scenario,next_transition=next_transition)
        transitions.append(transition)
    return transitions


def load_sounds(data_sounds):
    sounds = []
    for data_sound in data_sounds:
        id = data_sound['id']
        src_sound = data_sound['source']
        sound = Sound(id=id, src_sound=src_sound)
        sounds.append(sound)
    return sounds


def load_events(data_events):
    events = []
    for data_event in data_events:
        id = data_event['id']
        data_preconditions = data_event['preconditions'] if 'preconditions' in data_event else {}
        data_posconditions = data_event['posconditions']
        repetitions = data_event['repetitions'] if 'repetitions' in data_event else None
        pre_conditions = PreConditionTree(load_preconditions(data_preconditions))
        pos_conditions = load_posconditions(data_posconditions)

        events.append(Event(id=id,pre_conditions=pre_conditions,pos_conditions=pos_conditions,repetitions=repetitions))

    return events

def load_state(data_state,size,position):
    id = data_state['id']
    size = Size(data_state['size'][0],data_state['size'][1]) if 'size' in data_state else size
    position = Position(data_state['position'][0],data_state['position'][1]) if 'position' in data_state else position
    repetitions = data_state['repetitions'] if 'repetitions' in data_state else 0
    time_sprite = data_state['time_sprite'] if 'time_sprite' in data_state else 0

    scr_images = data_state['images'] if 'images' in data_state else [data_state['image']]

    return State(id=id,src_images=scr_images,size=size,position=position,time_sprite=time_sprite,repeate=repetitions)


def load_object(data_object,scenario_id):
    id = data_object['id']
    position = Position(data_object['position'][0],data_object['position'][1]) if 'position' in data_object else Position(None,None)
    size = Size(data_object['size'][0],data_object['size'][1]) if 'size' in data_object else Size(None,None)

    object = Object(id=id,scenario_id=scenario_id,position=position,size=size)
    
    initial_state = data_object['initial_state'] if 'initial_state' in data_object else None

    data_states = data_object['states']
    for data_state in data_states:
        state = load_state(data_state,size,position)
        if state.id == initial_state:
            object.add_state(state=state,initial=True)
        else:
            object.add_state(state=state,initial=False)
    
    data_sounds = data_object['sounds'] if 'sounds' in data_object else []
    sounds = load_sounds(data_sounds)
    for sound in sounds:
        object.add_sound(sound=sound)

    return object

def load_scenario(data_scenario,size):
    id = data_scenario['id']
    scenario = Scenario(id=id)
    data_states = data_scenario['states']
    initial_state = data_scenario['initial_state'] if 'initial_state' in data_scenario else None

    for data_state in data_states:
        state = load_state(data_state,size,Position(0,0))
        if state.id == initial_state:
            scenario.add_state(state=state,initial=True)
        else:
            scenario.add_state(state=state,initial=False)

    data_sounds = data_scenario['sounds'] if 'sounds' in data_scenario else []
    sounds = load_sounds(data_sounds)
    for sound in sounds:
        scenario.add_sound(sound=sound)

    data_objects = data_scenario['objects']
    objects = []
    for data_object in data_objects:
        object = load_object(data_object,scenario_id=id)
        objects.append(object)

    return scenario,objects

def load_room(title,size,data_scenarios):
    game_state = GameState(Size(size[0],size[1]))
    room = EscapeRoom(title)
    
    for data_scenario in data_scenarios:
        scenario,objects = load_scenario(data_scenario,Size(size[0],size[1]))
        room.add_scenario(scenario=scenario)
        game_state.first_scenario(scenario_id=scenario.id)
        for object in objects:
            room.add_object(object=object)
    return room,game_state

def load(filename=None):
    if filename is not None:
        file = open(filename)
        escape_room_json = json.load(file)
    else:
        jsonString = sys.stdin.read()
        escape_room_json = json.loads(jsonString)
    
    title = escape_room_json['title']
    size = escape_room_json['size']
    data_scenarios = escape_room_json['scenarios'] if 'scenarios' in escape_room_json else []
    data_events = escape_room_json['events'] if 'events' in escape_room_json else []
    data_transitions = escape_room_json['transitions'] if 'transitions' in escape_room_json else []
    
    room,state = load_room(title,size,data_scenarios)

    events = load_events(data_events)
    for event in events:
        room.add_event(event)
    transitions = load_transitions(data_transitions)
    for transition in transitions:
        room.add_transition(transition)

    return room,state