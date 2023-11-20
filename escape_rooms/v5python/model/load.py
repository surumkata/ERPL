import json
from model.escape_room import EscapeRoom
from model.scene import Scene
from model.object import Object
from model.state import State
from model.utils import __images, Position, Size
from model.precondition_tree import PreConditionOperatorAnd, PreConditionOperatorNot, PreConditionOperatorOr, PreConditionTree, PreConditionVar
from model.event import Event
from model.precondition import EventPreConditionClickAfterEvent, EventPreConditionActiveWhenState, EventPreConditionActiveWhenItemInUse , EventPreConditionActiveWhenItemNotInUse, EventPreConditionActiveWhenNotState, EventPreConditionClick, EventPreConditionClickNot
from model.poscondition import EventPosConditionChangeScene, EventPosConditionChangePosition, EventPosConditionChangeSize, EventPosConditionChangeState, EventPosConditionEndGame,EventPosConditionDeleteItem, EventPosConditionPutInventory,EventPosConditionShowMessage,EventPosConditionAskCode
import sys

def load_precondition(precondition):
    type = precondition['type']
    if type == "Click":
        object_id = precondition['object']
        event_precondition = EventPreConditionClick(object_id)
    elif type == "ClickNot":
        object_id = precondition['object']
        event_precondition = EventPreConditionClickNot(object_id)
    elif type == "WhenStateObject":
        object_id = precondition['object']
        state_id = precondition['state']
        event_precondition = EventPreConditionActiveWhenState(object_id,state_id)
    elif type == "WhenNotStateObject":
        object_id = precondition['object']
        state_id = precondition['state']
        event_precondition = EventPreConditionActiveWhenNotState(object_id,state_id)
    elif type == "ClickAfterEvent":
        object_id = precondition['object']
        after_event_id = precondition['event']
        event_precondition = EventPreConditionClickAfterEvent(object_id,after_event_id)
    elif type == 'ItemNotActived':
        item_id = precondition['item']
        event_precondition = EventPreConditionActiveWhenItemNotInUse(item_id)
    elif type == 'ItemActived':
        item_id = precondition['item']
        event_precondition = EventPreConditionActiveWhenItemInUse(item_id)
    
    return event_precondition

def load_preconditions(preconditions):
    if 'operator' in preconditions:
        operator = preconditions['operator']
        left = load_preconditions(preconditions['left'])
        right = load_preconditions(preconditions['right']) if 'right' in preconditions and preconditions['right'] is not None else None
        if operator == 'e':
            return PreConditionOperatorAnd(left,right)
        elif operator == 'ou':
            return PreConditionOperatorOr(left,right)
        elif operator == 'nao':    
            return PreConditionOperatorNot(left)
    elif 'variavel' in preconditions:
        variavel = preconditions['variavel']
        return PreConditionVar(load_precondition(variavel))

    else: 
        return None

def load_events(room, data_events):
    for event_id, data_event in data_events.items():
        data_preconditions = data_event['precondicoes'] if 'precondicoes' in data_event else {}
        data_posconditions = data_event['poscondicoes']
        repeatable = data_event['repetivel']
        pre_conditions = PreConditionTree(load_preconditions(data_preconditions))
        pos_conditions = []

        for data_action in data_posconditions:
            type = data_action['type']
            if type == "ChangeState":
                object_id = data_action['object']
                state_id = data_action['state']
                event_poscondition = EventPosConditionChangeState(object_id,state_id)
            elif type == "EndGame":
                event_poscondition = EventPosConditionEndGame()
            elif type == "PutInInventory":
                object_id = data_action['object']
                event_poscondition = EventPosConditionPutInventory(object_id)
            elif type == "DeleteItem":
                item_id = data_action['item']
                event_poscondition = EventPosConditionDeleteItem(item_id)
            elif type == 'ShowMessage':
                message = data_action['message']
                (msg_pos_x,msg_pos_y) = data_action['position']
                event_poscondition = EventPosConditionShowMessage(Position(msg_pos_x,msg_pos_y),message)
            elif type == 'AskCode':
                code = data_action['code']
                message = data_action['message']
                sucess_event = data_action['sucess_event']
                fail_event = data_action['fail_event']
                event_poscondition = EventPosConditionAskCode(code,message,sucess_event,fail_event)
            elif type == 'ChangeSize':
                object_id = data_action['object']
                (size_x,size_y) = data_action['size']
                event_poscondition = EventPosConditionChangeSize(object_id,Size(size_x,size_y))
            elif type == 'ChangePosition':
                object_id = data_action['object']
                (pos_x,pos_y) = data_action['position']
                event_poscondition = EventPosConditionChangePosition(object_id,Position(pos_x,pos_y))
            elif type == 'ChangeScene':
                scene_id = data_action['scene']
                event_poscondition = EventPosConditionChangeScene(scene_id)
            pos_conditions.append(event_poscondition)

        linked = 'linked' in data_event and data_event['linked']

        room.add_event(Event(event_id,pre_conditions,pos_conditions,repeatable, linked))

def load_room(room_id,data_room):
    (size_x,size_y) = data_room['size']
    scenes = data_room['scenes']
    room = EscapeRoom(room_id)
    for scene_id,data_scene in scenes.items():
        scene = Scene(scene_id)
        scene_states = data_scene['states']
        for ss_id,ss in scene_states.items():
            ss_filename = __images + ss['filename']
            ss_initial = ss['initial']
            scene.add_state(State(ss_id,[ss_filename],Size(size_x,size_y),Position(0,0)),ss_initial)
        room.add_scene(scene)
        objects = data_scene['objects']
        for object_id,data_object in objects.items():
            (obj_size_x,obj_size_y) = data_object['size'] if 'size' in data_object else (None,None)
            (obj_pos_x,obj_pos_y) = data_object['position'] if 'position' in data_object else (None,None)
            obj_states = data_object['states']
            object = Object(object_id, scene_id, Position(obj_pos_x,obj_pos_y),Size(obj_size_x,obj_size_y))
            for os_id,os in obj_states.items():
                os_filename = __images + os['filename']
                os_initial = os['initial']
                (os_size_x,os_size_y) =  os['size'] if 'size' in os else (obj_size_x,obj_size_y)
                (os_pos_x,os_pos_y) =  os['position'] if 'position' in os else (obj_pos_x,obj_pos_y)
                object.add_state(State(os_id,[os_filename],Size(os_size_x,os_size_y),Position(os_pos_x,os_pos_y)),os_initial) #TODO: estado para items
            room.add_object(object)
    return room

def load(filename=None):
    if filename is not None:
        file = open(filename)
        escape_room_json = json.load(file)
    else:
        jsonString = sys.stdin.read()
        escape_room_json = json.loads(jsonString)
    
    data_map = escape_room_json['map']
    data_events = escape_room_json['events']


    (room_id,data_room) = [(room_id,data_room) for (room_id,data_room) in data_map.items()][0]

    room = load_room(room_id,data_room)
    load_events(room, data_events)

    return room