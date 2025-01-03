import json
from .escape_room import EscapeRoom
from .scenario import Scenario
from .object import Object
from .view import View,ViewSketch,Rect,Triangle,Circle,Polygon,Ellipse,Square
from .hitbox import HitboxRect, HitboxTriangle, HitboxCircle, HitboxPolygon, HitboxEllipse, HitboxSquare
from .utils import Position, Size, HEIGHT_INV, Text
from .precondition_tree import PreConditionOperatorAnd, PreConditionOperatorNot, PreConditionOperatorOr, PreConditionTree, PreConditionVar
from .event import Event
from .precondition import EventPreConditionClickedHitbox,EventPreConditionClickedNotHitbox, EventPreConditionAfterTime, EventPreConditionAfterEvent, EventPreConditionWhenObjectIsView, EventPreConditionItemIsInUse , EventPreConditionClickedObject, EventPreConditionClickedNotObject, EventPreConditionIsEqualTo,  EventPreConditionIsGreaterThan, EventPreConditionIsLessThan, EventPreConditionIsGreaterThanOrEqualTo, EventPreConditionIsLessThanOrEqualTo
from .poscondition import EventPosConditionEndGameFormatMessage, EventPosConditionSocketConnection, EventPosConditionTransition, EventPosConditionSlidePuzzle, EventPosConditionPuzzle, EventPosConditionSequence, EventPosConditionConnections, EventPosConditionMultipleChoice,EventPosConditionMoveObject, EventPosConditionPlaySound, EventPosConditionChangeScenario, EventPosConditionObjChangePosition, EventPosConditionObjScale, EventPosConditionObjChangeState, EventPosConditionEndGame,EventPosConditionDeleteItem, EventPosConditionObjPutInventory,EventPosConditionShowMessage,EventPosConditionShowFormatMessage,EventPosConditionQuestion,EventPosConditionVarDecreases,EventPosConditionVarIncreases,EventPosConditionVarBecomes
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
    if type == "CLICKED_HITBOX":
        hitbox_id = precondition['hitbox']
        event_precondition = EventPreConditionClickedHitbox(hitbox_id)
    elif type == "CLICKED_NOT_HITBOX":
        hitbox_id = precondition['hitbox']
        event_precondition = EventPreConditionClickedNotHitbox(hitbox_id)
    elif type == "WHEN_OBJECT_IS_VIEW":
        object_id = precondition['object']
        view_id = precondition['view']
        event_precondition = EventPreConditionWhenObjectIsView(object_id,view_id)
    elif type == "AFTER_EVENT":
        after_event_id = precondition['event']
        event_precondition = EventPreConditionAfterEvent(object_id,after_event_id)
    elif type == 'OBJ_IS_IN_USE':
        item_id = precondition['object']
        event_precondition = EventPreConditionItemIsInUse(item_id)
    elif type == 'AFTER_TIME':
        time = precondition['time']
        event_precondition = EventPreConditionAfterTime(time)
    elif type == 'IS_EQUAL_TO':
        variable = precondition['variable']
        number = precondition['number']
        event_precondition = EventPreConditionIsEqualTo(variable,number)
    elif type == 'IS_GREATER_THAN':
        variable = precondition['variable']
        number = precondition['number']
        event_precondition = EventPreConditionIsGreaterThan(variable,number)
    elif type == 'IS_LESS_THAN':
        variable = precondition['variable']
        number = precondition['number']
        event_precondition = EventPreConditionIsLessThan(variable,number)
    elif type == 'IS_GREATER_THAN_OR_EQUAL_TO':
        variable = precondition['variable']
        number = precondition['number']
        event_precondition = EventPreConditionIsGreaterThanOrEqualTo(variable,number)
    elif type == 'IS_LESS_THAN_OR_EQUAL_TO':
        variable = precondition['variable']
        number = precondition['number']
        event_precondition = EventPreConditionIsLessThanOrEqualTo(variable,number)
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
            message = data_action['message']
            event_poscondition = EventPosConditionEndGame(message)
        if type == "END_GAME_FORMAT_MESSAGE":
            message = data_action['message']
            event_poscondition = EventPosConditionEndGameFormatMessage(message)
        elif type == "OBJ_CHANGE_VIEW":
            object_id = data_action['object']
            view_id = data_action['view']
            event_poscondition = EventPosConditionObjChangeState(object_id,view_id)
        elif type == 'OBJ_CHANGE_POSITION':
            object_id = data_action['object']
            (pos_x,pos_y) = (data_action['position']["x"],data_action['position']["y"]+HEIGHT_INV)
            event_poscondition = EventPosConditionObjChangePosition(object_id,Position(pos_x,pos_y))
        elif type == 'OBJ_SCALE':
            object_id = data_action['object']
            (scale_x,scale_y) = (data_action['scale']["x"],data_action['scale']["y"])
            event_poscondition = EventPosConditionObjScale(object_id,Size(scale_x,scale_y))
        elif type == 'SHOW_MESSAGE':
            message = data_action['message']
            (pos_x,pos_y) = (data_action['position']["x"],data_action['position']["y"]+HEIGHT_INV)
            event_poscondition = EventPosConditionShowMessage(message,Position(pos_x,pos_y))
        elif type == 'SHOW_FORMAT_MESSAGE':
            message = data_action['message']
            (pos_x,pos_y) = (data_action['position']["x"],data_action['position']["y"]+HEIGHT_INV)
            event_poscondition = EventPosConditionShowFormatMessage(message,Position(pos_x,pos_y))
        elif type == 'QUESTION':
            question = data_action['question']
            answer = data_action['answer']
            sucess = Event(id="sucess",pre_conditions={},pos_conditions=load_posconditions(data_action['sucess']),repetitions=1)
            fail = Event(id="fail",pre_conditions={},pos_conditions=load_posconditions(data_action['fail']),repetitions=1)
            fail = data_action['fail']
            event_poscondition = EventPosConditionQuestion(answer,question,sucess,fail)
        elif type == "OBJ_PUT_INVENTORY":
            object_id = data_action['object']
            event_poscondition = EventPosConditionObjPutInventory(object_id)
        elif type == 'CHANGE_SCENARIO':
            scenario_id = data_action['scenario']
            event_poscondition = EventPosConditionChangeScenario(scenario_id)
        elif type == "REMOVE_OBJ":
            item_id = data_action['object']
            event_poscondition = EventPosConditionDeleteItem(item_id)
        elif type == 'PLAY_SOUND':
            sound_id = data_action['sound']
            source_id = data_action['source_id']
            source_type = data_action['source_type']
            event_poscondition = EventPosConditionPlaySound(sound_id,source_id,source_type)
        elif type == 'MOTION_OBJECT':
            object_id = data_action['motion_object']
            trigger_object = data_action['trigger_object']
            sucess = Event(id="sucess",pre_conditions={},pos_conditions=load_posconditions(data_action['sucess']),repetitions=1)
            fail = Event(id="fail",pre_conditions={},pos_conditions=load_posconditions(data_action['fail']),repetitions=1)
            event_poscondition = EventPosConditionMoveObject(object_id,trigger_object,sucess,fail)
        elif type == 'MULTIPLE_CHOICE':
            question = data_action['question']
            answer = data_action['answer']
            multiple_choices = data_action['choices']
            sucess = Event(id="sucess",pre_conditions={},pos_conditions=load_posconditions(data_action['sucess']),repetitions=1)
            fail = Event(id="fail",pre_conditions={},pos_conditions=load_posconditions(data_action['fail']),repetitions=1)
            event_poscondition = EventPosConditionMultipleChoice(question,answer,multiple_choices,sucess,fail)
        elif type == 'CONNECTIONS':
            question = data_action['question']
            list1 = data_action['list1']
            list2 = data_action['list2']
            sucess = Event(id="sucess",pre_conditions={},pos_conditions=load_posconditions(data_action['sucess']),repetitions=1)
            fail = Event(id="fail",pre_conditions={},pos_conditions=load_posconditions(data_action['fail']),repetitions=1)
            event_poscondition = EventPosConditionConnections(list1,list2,question,sucess,fail)
        elif type == 'SEQUENCE':
            question = data_action['question']
            sequence = data_action['sequence']
            sucess = Event(id="sucess",pre_conditions={},pos_conditions=load_posconditions(data_action['sucess']),repetitions=1)
            fail = Event(id="fail",pre_conditions={},pos_conditions=load_posconditions(data_action['fail']),repetitions=1)
            event_poscondition = EventPosConditionSequence(sequence,question,sucess,fail)        
        elif type == 'PUZZLE':
            image = load_source(data_action['sources'])[0]
            sucess = Event(id="sucess",pre_conditions={},pos_conditions=load_posconditions(data_action['sucess']),repetitions=1)
            event_poscondition = EventPosConditionPuzzle(image,sucess)
        elif type == 'SLIDEPUZZLE':
            image = load_source(data_action['sources'])[0]
            sucess = Event(id="sucess",pre_conditions={},pos_conditions=load_posconditions(data_action['sucess']),repetitions=1)
            event_poscondition = EventPosConditionSlidePuzzle(image,sucess)
        elif type == 'TRANSITION':
            transition = data_action['transition']
            event_poscondition = EventPosConditionTransition(transition)
        elif type == 'SOCKET_CONNECTION':
            host = data_action['host']
            port = data_action['port']
            message = data_action['message']
            sucess = Event(id="sucess",pre_conditions={},pos_conditions=load_posconditions(data_action['sucess']),repetitions=1)
            fail = Event(id="fail",pre_conditions={},pos_conditions=load_posconditions(data_action['fail']),repetitions=1)
            event_poscondition = EventPosConditionSocketConnection(host,port,message,sucess,fail)
        elif type == 'VAR_DECREASES':
            variable = data_action['variable']
            number = data_action['number']
            event_poscondition = EventPosConditionVarDecreases(variable,number)
        elif type == 'VAR_INCREASES':
            variable = data_action['variable']
            number = data_action['number']
            event_poscondition = EventPosConditionVarIncreases(variable,number)
        elif type == 'VAR_BECOMES':
            variable = data_action['variable']
            number = data_action['number']
            event_poscondition = EventPosConditionVarBecomes(variable,number)
        pos_conditions.append(event_poscondition)
    return pos_conditions


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

def load_transitions(data_transitions):
    transitions = []
    for data_transition in data_transitions:
        id = data_transition['id']
        background = load_view(data_transition['view'])
        music = data_transition['music']['sources'][0][1] if 'music' in data_transition else None
        if 'format_story' in data_transition:
            story = data_transition['format_story']
            format_story = True
        else:
            story = data_transition['story'] if 'story' in data_transition else None
            format_story = False
        next_type = data_transition['next_type']
        next_scenario = None
        next_transition = None
        if next_type=="SCENARIO":
            next_scenario = data_transition['next']
        else:
            next_transition = data_transition['next']
        transition = Transition(id=id,background=background,music=music,story=story,next_scenario=next_scenario,next_transition=next_transition,format_story=format_story)
        transitions.append(transition)
    return transitions


def load_sounds(data_sounds):
    sounds = []
    for data_sound in data_sounds:
        id = data_sound['id']
        src_sound = load_source(data_sound['sources'])[0]
        loop = data_sound['loop']
        sound = Sound(id=id, src_sound=src_sound, loop=loop)
        sounds.append(sound)
    return sounds


def load_view_sketch(data_view, hitboxes):
    sketch = ViewSketch(data_view['id'],hitboxes)
    data_draws = data_view['draws']
    color = "0x000000"
    for data in data_draws:
        draw_type = data['type']
        if(draw_type == 'FILL'):
            color = data['color'].replace('#','0x')
        elif(draw_type == 'RECT'):
            tl = data['tl'] if 'tl' in data else 0
            tr = data['tr'] if 'tr' in data else 0
            bl = data['bl'] if 'bl' in data else 0
            br = data['br'] if 'br' in data else 0
            (x,y) = (data['position']["x"],data['position']["y"]+HEIGHT_INV)
            (w,h) = (data['size']["x"],data['size']["y"])
            rect = Rect(x,y,w,h,tl,tr,br,bl,color)
            sketch.add_draw(rect)
        elif(draw_type == 'CIRCLE'):
            (x,y) = (data['position']["x"],data['position']["y"]+HEIGHT_INV)
            radius = data['radius']
            circle = Circle(x,y,radius,color)
            sketch.add_draw(circle)
        elif(draw_type == 'TRIANGLE'):
            x1,y1 = (data['point1']["x"],data['point1']["y"]+HEIGHT_INV)
            x2,y2 = (data['point2']["x"],data['point2']["y"]+HEIGHT_INV)
            x3,y3 = (data['point3']["x"],data['point3']["y"]+HEIGHT_INV)
            triangle = Triangle(x1,y1,x2,y2,x3,y3,color)
            sketch.add_draw(triangle)
        elif(draw_type == 'POLYGON'):
            points = []
            for point in data['points']:
                points.append({"x" : point.x, "y" : point.y + HEIGHT_INV})
            polygon = Polygon(data['points'],color)
            sketch.add_draw(polygon)
        elif(draw_type == 'SQUARE'):
            tl = data['tl'] if 'tl' in data else 0
            tr = data['tr'] if 'tr' in data else 0
            bl = data['bl'] if 'bl' in data else 0
            br = data['br'] if 'br' in data else 0
            (x,y) = (data['position']["x"],data['position']["y"]+HEIGHT_INV)
            width = data['width']
            square = Square(x,y,width,tl,tr,br,bl,color)
            sketch.add_draw(square)
        elif(draw_type == 'ELLIPSE'):
            (x,y) = (data['position']["x"],data['position']["y"]+HEIGHT_INV)
            (w,h) = (data['size']["x"],data['size']["y"])
            ellipse = Ellipse(x,y,w,h,color)
            sketch.add_draw(ellipse)

    sketch.make_bbox()
    return sketch

def load_texts(data_texts):
    texts = []
    for data in data_texts:
        color = data['color'].replace('#','0x') if 'color' in data else "0x000000"
        width = data['width'] if 'width' in data else 32
        (x,y) = (data['position']["x"],data['position']["y"]+HEIGHT_INV)
        if 'format_text' in data:
            text = data['format_text']
            format_text = True
        else:
            text = data['text'] if 'text' in data else ""
            format_text = False
        texts.append(Text(text,x,y,width,color,format_text))
    return texts
        

def load_advanced_hitboxes(data_hitboxes):
    hitboxes = []
    for data in data_hitboxes:
        id = data['id'] if 'id' in data else '_'
        type = data['type']
        if type == 'RECT':
            (x,y) = (data['position']["x"],data['position']["y"]+HEIGHT_INV)
            (w,h) = (data['size']["x"],data['size']["y"])
            rect = HitboxRect(id,x,y,w,h)
            hitboxes.append(rect)
        elif type == 'CIRCLE':
            (x,y) = (data['position']["x"],data['position']["y"]+HEIGHT_INV)
            radius = data['radius']
            circle = HitboxCircle(id,x,y,radius)
            hitboxes.append(circle)
        elif type == 'TRIANGLE':
            x1,y1 = (data['point1']["x"],data['point1']["y"]+HEIGHT_INV)
            x2,y2 = (data['point2']["x"],data['point2']["y"]+HEIGHT_INV)
            x3,y3 = (data['point3']["x"],data['point3']["y"]+HEIGHT_INV)
            triangle = HitboxTriangle(id,x1,y1,x2,y2,x3,y3)
            hitboxes.append(triangle)
        elif type == 'POLYGON':
            points = []
            for point in data['points']:
                points.append({"x" : point.x, "y" : point.y + HEIGHT_INV})
            polygon = HitboxPolygon(id,data['points'])
            hitboxes.append(polygon)
        elif type == 'SQUARE':
            (x,y) = (data['position']["x"],data['position']["y"]+HEIGHT_INV)
            width = data['width']
            square = HitboxSquare(id,x,y,width)
            hitboxes.append(square)
        elif type == 'ELLIPSE':
            (x,y) = (data['position']["x"],data['position']["y"]+HEIGHT_INV)
            (w,h) = (data['size']["x"],data['size']["y"])
            ellipse = HitboxEllipse(id,x,y,w,h)
            hitboxes.append(ellipse)
    return hitboxes 

def load_hitboxes(data_view):
    type = data_view['hitbox_type']
    if type == 'NO':
        return []
    elif type == 'ADVANCED':
        return load_advanced_hitboxes(data_view['hitboxes'])
    else:
        if data_view['type'] == 'VIEW_IMAGE':
            id = data_view['id']
            (x,y) = (data_view['position']["x"],data_view['position']["y"]+HEIGHT_INV) if 'position' in data_view else (0,HEIGHT_INV)
            (w,h) = (data_view['size']["x"],data_view['size']["y"]) if 'size' in data_view else (1280,720)
            hitbox = HitboxRect(id,x,y,w,h)
            return [hitbox]
        elif data_view['type'] == 'VIEW_SKETCH':
            return load_advanced_hitboxes(data_view['draws'])

def load_source(data_sources):
    sources = []
    for data_source in data_sources:
        type = data_source[0]
        if(type == 'URL'):
            sources.append(data_source[1])
        elif(type == 'LIB'):
            sources.append('https://surumkata.github.io/weberpl/assets/' + data_source[1] + '.png')
        elif(type == 'PATH'):
            sources.append(data_source[1])
    return sources

def load_view(data_view):
    id = data_view['id']
    type = data_view['type']
    hitboxes = load_hitboxes(data_view)
    if (type == 'VIEW_IMAGE'):
        size = Size(data_view['size']["x"],data_view['size']["y"]) if 'size' in data_view else Size(1280,720)
        position = Position(data_view['position']["x"],data_view['position']["y"]+HEIGHT_INV) if 'position' in data_view else Position(0,HEIGHT_INV)
        repetitions = data_view['repetitions'] if 'repetitions' in data_view else 0
        time_sprite = data_view['time_sprite'] if 'time_sprite' in data_view else 0
        src_images = load_source(data_view['sources'])
        return View(id=id,src_images=src_images,size=size,position=position,time_sprite=time_sprite,repeate=repetitions,hitboxes=hitboxes)
    elif (type == 'VIEW_SKETCH'):
        return load_view_sketch(data_view, hitboxes)
        


def load_object(data_object,scenario_id):
    id = data_object['id']

    object = Object(id=id,scenario_id=scenario_id)
    
    initial_view = data_object['initial_view'] if 'initial_view' in data_object else None

    data_views = data_object['views']
    for data_view in data_views:
        view = load_view(data_view)
        if view.id == initial_view:
            object.add_view(view=view,initial=True)
        else:
            object.add_view(view=view,initial=False)
    
    data_sounds = data_object['sounds'] if 'sounds' in data_object else []
    sounds = load_sounds(data_sounds)
    for sound in sounds:
        object.add_sound(sound=sound)

    return object

def load_scenario(data_scenario):
    id = data_scenario['id']
    scenario = Scenario(id=id)
    data_views = data_scenario['views']
    initial_view = data_scenario['initial_view'] if 'initial_view' in data_scenario else None

    for data_view in data_views:
        view = load_view(data_view)
        if view.id == initial_view:
            scenario.add_view(view=view,initial=True)
        else:
            scenario.add_view(view=view,initial=False)

    data_sounds = data_scenario['sounds'] if 'sounds' in data_scenario else []
    sounds = load_sounds(data_sounds)
    for sound in sounds:
        scenario.add_sound(sound=sound)

    data_objects = data_scenario['objects'] if 'objects' in data_scenario else []
    data_hitboxes = data_scenario['hitboxes'] if 'hitboxes' in data_scenario else []
    data_texts = data_scenario['texts'] if 'texts' in data_scenario else []
    objects = []
    for data_object in data_objects:
        object = load_object(data_object,scenario_id=id)
        objects.append(object)
    hitboxes = load_advanced_hitboxes(data_hitboxes)
    scenario.add_hitboxes(hitboxes)

    texts = load_texts(data_texts)
    scenario.add_texts(texts)

    return scenario,objects

def load_room(title,size,data_scenarios):
    game_state = GameState(Size(size["x"],size["y"]))
    room = EscapeRoom(title)
    
    for data_scenario in data_scenarios:
        scenario,objects = load_scenario(data_scenario)
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
    size = {"x" : 1280, "y": 720}
    data_scenarios = escape_room_json['scenarios'] if 'scenarios' in escape_room_json else []
    data_events = escape_room_json['events'] if 'events' in escape_room_json else []
    data_transitions = escape_room_json['transitions'] if 'transitions' in escape_room_json else []
    data_variables = escape_room_json['variables'] if 'variables' in escape_room_json else []
    
    
    room,state = load_room(title,size,data_scenarios)

    for data_variable in data_variables:
        variable = data_variable['id']
        number = data_variable['number']
        room.add_variable(variable,number)


    start_id = escape_room_json['start']
    start_type = escape_room_json['start_type']

    events = load_events(data_events)
    for event in events:
        room.add_event(event)

    transitions = load_transitions(data_transitions)
    for transition in transitions:
        room.add_transition(transition)

    if start_type == 'TRANSITION':
        state.active_transition_mode(room.transitions[start_id])
    else:
        state.current_scenario = start_id

    return room,state