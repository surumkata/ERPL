function load (p5,json) {
    if (!json) {
        console.log("NO JSON!")
        return undefined;
    }
    let scenarios = json.scenarios
    if (!scenarios) {
        scenarios = []
    }
    var gs = new GameState(new Size(WIDTH,HEIGHT))
    var er = new EscapeRoom(json.title)
    loadScenarios(p5,er,scenarios);
    let events = loadEvents(json.events);
    events.forEach(function(event){
        er.addEvent(event);
    })

    let transitions = json.transitions
    loadTransitions(p5,er,gs,transitions)

    let variables = json.variables ?? []
    variables.forEach(variable => {
        er.addVariable(variable.id,variable.number)
    })


    if (json.start_type == 'TRANSITION'){
        gs.activeTransitionMode(er.transitions[json.start])
    }
    else{
        gs.currentScenario = json.start
    }    

    return {
        'escapeRoom' : er,
        'gameState' : gs,
        'inventory' : new Inventory()
    }
}

function loadTransitions(p5,er,gs,transitions){
    transitions.forEach(function(transition){
        let view = transition.view;
        let turn = view.turn ?? {x: false, y: false};
        let sources = loadSources(view.sources)
        let tv = new View(p5,view.id,sources,gs.size,new Position(0,HEIGHT_INV),0,0,turn);

        let format_story = false
        let story = transition.story
        if(transition.format_story){
            format_story = true
            story = transition.format_story
        }

        var next_scenario = null;
        var next_transition = null;
        if (transition.next_type == "TRANSITION") {
            next_transition = transition.next;
        }
        else {
            next_scenario = transition.next;
        }
        let t = new Transition(transition.id,tv,story,next_scenario,next_transition,format_story);
        er.addTransition(t);
    })
}

function loadSketch(id,draws,hitboxes,hitboxesType){
    var sketch = new ViewSketch(id,hitboxes,hitboxesType);
    draws.forEach(draw => {
        const type = draw.type;
        let drawView;
        switch(type) {
            case "RECT":
                const { tl: rect_tl = 0, tr: rect_tr = 0, br: rect_br = 0, bl: rect_bl = 0 } = draw;
                drawView = new Rect(draw.id,draw.position.x,draw.position.y+HEIGHT_INV,draw.size.x,draw.size.y,rect_tl,rect_tr,rect_br,rect_bl);
                break;
            case "POLYGON":
                let points = []

                for (var i in draw.points){
                  let newx = draw.points[i].x
                  let newy = draw.points[i].y + HEIGHT_INV
                  points.push({"x" : newx, "y" : newy})
                }
                drawView = new Polygon(draw.id,points);
                break;
            case "SQUARE":
                const { tl: square_tl = 0, tr: square_tr = 0, br: square_br = 0, bl: square_bl = 0 } = draw;
                drawView = new Square(draw.id,draw.position.x,draw.position.y+HEIGHT_INV,draw.width,square_tl,square_tr,square_br,square_bl);
                break;
            case "TRIANGLE":
                drawView = new Triangle(draw.id,draw.point1.x,draw.point1.y+HEIGHT_INV,draw.point2.x,draw.point2.y+HEIGHT_INV,draw.point3.x,draw.point3.y+HEIGHT_INV);
                break;
            case "CIRCLE":
                drawView = new Circle(draw.id,draw.position.x,draw.position.y+HEIGHT_INV,draw.radius);
                break;
            case "ELLIPSE":
                drawView = new Ellipse(draw.id, draw.position.x, draw.position.y+HEIGHT_INV, draw.size.x, draw.size.y);
                break;
            case "FILL":
                let alpha = draw.alpha ?? 255;
                drawView = new Fill(draw.color, alpha);
                break;
            case "NO_FILL":
                drawView = new NoFill();
                break;
            case "STROKE":
                let alpha_stroke = draw.alpha ?? 255;
                drawView = new Stroke(draw.color,draw.w, alpha_stroke);
                break;
            case "NO_STROKE":
                drawView = new NoStroke();
                break; 
            default:
                drawView = null;
                break;
        }

        if(drawView !== null){
            sketch.addDraw(drawView);
        }
    })
    sketch.makeBBox();
    return sketch;
}

function loadAdvancedHitbox(data_hitboxes){
    var hitboxes = [];
    data_hitboxes.forEach(hitbox => {
        switch(hitbox.type) {
            case "RECT":
                hitboxes.push(new HitboxRect(hitbox.id,hitbox.position.x,hitbox.position.y+HEIGHT_INV,hitbox.size.x,hitbox.size.y));
                break;
            case "POLYGON":
                let points = []

                for (var i in hitbox.points){
                  let newx = hitbox.points[i].x
                  let newy = hitbox.points[i].y +HEIGHT_INV
                  points.push({"x" : newx, "y" : newy})
                }
                hitboxes.push(new HitboxPolygon(hitbox.id,points));
                break;
            case "SQUARE":
                hitboxes.push(new HitboxSquare(hitbox.id,hitbox.position.x,hitbox.position.y+HEIGHT_INV,hitbox.width));
                break;
            case "TRIANGLE":
                hitboxes.push(new HitboxTriangle(hitbox.id,hitbox.point1.x,hitbox.point1.y+HEIGHT_INV,hitbox.point2.x,hitbox.point2.y+HEIGHT_INV,hitbox.point3.x,hitbox.point3.y+HEIGHT_INV));
                break;
            case "CIRCLE":
                hitboxes.push(new HitboxCircle(hitbox.id,hitbox.position.x,hitbox.position.y+HEIGHT_INV,hitbox.radius));
                break;
            case "ELLIPSE":
                hitboxes.push(new HitboxEllipse(hitbox.id,hitbox.position.x,hitbox.position.y+HEIGHT_INV,hitbox.size.x,hitbox.size.y));
                break;
            default:
                break;
        }
    })
    return hitboxes;
}

function loadHitboxes(view){
    var hitboxes = [];
    switch(view.hitbox_type){
        case "NO":
            break;
        case "ADVANCED":
            hitboxes = loadAdvancedHitbox(view.hitboxes);
            break;
        default:
            switch(view.type){
                case "VIEW_IMAGE":
                    let size = view.size ? new Size(view.size.x, view.size.y) : new Size(WIDTH, HEIGHT);
                    let position = view.position ? new Position(view.position.x, view.position.y + HEIGHT_INV) : new Position(0, HEIGHT_INV);
                    hitboxes.push(new HitboxRect(view.id,position.x,position.y,size.x,size.y));
                    break;
                case "VIEW_SKETCH":
                    hitboxes = loadAdvancedHitbox(view.draws);
            }
            break;
    }
    
    return hitboxes;
}

function loadSource(source){
    switch(source[0]){
        case 'URL' :
            return source[1];
        case 'PATH' :
            return source[1];
        case 'LIB':
            return 'https://surumkata.github.io/weberpl/assets/' + source[1] + '.png'
        default:
            return null;
    }
}

function loadSources(sources){
    var result = []
    sources.forEach(source => {
        result.push(loadSource(source));
    })
    return result
    
}

function loadView(p5,view){
    let hitboxes = loadHitboxes(view);
    switch(view.type){
        case "VIEW_IMAGE":
            let sources = loadSources(view.sources)
            let time_sprite = view.time_sprite ?? 0;
            let repetitions = view.repetitions || Infinity;
            let turn = view.turn ?? {x: false, y: false};
            let size = view.size ? new Size(view.size.x, view.size.y) : new Size(WIDTH, HEIGHT);
            let position = view.position ? new Position(view.position.x, view.position.y + HEIGHT_INV) : new Position(0,HEIGHT_INV);
            let v = new View(p5,view.id,sources,size, position,time_sprite,repetitions,turn,hitboxes,view.hitbox_type);
            v.makeHitboxesBBox();
            return v
        case "VIEW_SKETCH":
            return loadSketch(view.id,view.draws,hitboxes,view.hitbox_type);
        default:
            return null;
    }
}

function loadSound(sound){
    return new Sound(sound.id,sound.sources[0][1],sound.loop);
}

function loadObject(p5,scenario_id,object){
    let o = new ObjectEr(object.id,scenario_id);
    o.currentView = object['initial_view'];
    object.views.forEach(objView => {
        o.addView(loadView(p5,objView));
    })
    if(object.sounds){
        object.sounds.forEach(objSound => {
            o.addSound(loadSound(objSound));
        })
    }
    return o;
}


function loadTexts(dataTexts){
    var texts = [];
    dataTexts.forEach(data => {
        let id = data.id;
        let color = data.color ?? "#000000";
        let width = data.width ?? 32;
        let x = data.position.x;
        let y = data.position.y + HEIGHT_INV;
        let text = data.text ?? "";
        let format_text = false;
        if(data.format_text){
            text = data.format_text;
            format_text = true;
        }
        texts.push(new Text(id,text,x,y,width,color,format_text))
    })
    return texts;
}

function loadScenarios(p5,er,scenarios){
    scenarios.forEach(function(scenario){
        let s = new Scenario(scenario.id);
        s.currentView = scenario['initial_view'];
        scenario.views.forEach(scnView => {
            s.addView(loadView(p5,scnView));
        })
        if(scenario.objects){
            scenario.objects.forEach(object => {
                er.addObject(loadObject(p5,scenario.id,object));
            })
        }
        if(scenario.hitboxes){
            s.addHitboxes(loadAdvancedHitbox(scenario.hitboxes))
        }
        if(scenario.texts){
            s.addTexts(loadTexts(scenario.texts))
        }
        if(scenario.sounds){
            scenario.sounds.forEach(scnSound => {
                s.addSound(loadSound(scnSound));
            })
        }   
        er.addScenario(s);
    })
}

function loadPrecondition(precondition) {
    const type = precondition.type;
    let eventPrecondition;

    switch (type) {
        case "CLICKED_OBJECT":
            const objectId = precondition.object;
            eventPrecondition = new EventPreConditionClickedObject(objectId);
            break;
        case "CLICKED_NOT_OBJECT":
            const clickedNotObjectId = precondition.object;
            eventPrecondition = new EventPreConditionClickedNotObject(clickedNotObjectId);
            break;
        case "CLICKED_HITBOX":
            const hitboxId = precondition.hitbox;
            eventPrecondition = new EventPreConditionClickedHitbox(hitboxId);
            break;
        case "CLICKED_NOT_HITBOX":
            const clickedNotHitboxId = precondition.hitbox;
            eventPrecondition = new EventPreConditionClickedNotHitbox(clickedNotHitboxId);
            break;
        case "WHEN_OBJECT_IS_VIEW":
            const whenObjectId = precondition.object;
            const viewId = precondition.view;
            eventPrecondition = new EventPreConditionWhenObjectIsView(whenObjectId, viewId);
            break;
        case "AFTER_EVENT":
            const afterEventId = precondition.event;
            eventPrecondition = new EventPreConditionAfterEvent(afterEventId);
            break;
        case "OBJ_IS_IN_USE":
            const itemInUseId = precondition.object;
            eventPrecondition = new EventPreConditionItemIsInUse(itemInUseId);
            break;
        case "AFTER_TIME":
            const afterTime = precondition.time;
            eventPrecondition = new EventPreConditionAfterTime(afterTime);
            break;
        case "IS_EQUAL_TO":
            eventPrecondition = new EventPreConditionIsEqualTo(precondition.variable,precondition.number);
            break;
        case "IS_GREATER_THAN":
            eventPrecondition = new EventPreConditionIsGreaterThan(precondition.variable,precondition.number);
            break;
        case "IS_LESS_THAN":
            eventPrecondition = new EventPreConditionIsLessThan(precondition.variable,precondition.number);
            break;
        case "IS_GREATER_THAN_OR_EQUAL_TO":
            eventPrecondition = new EventPreConditionIsGreaterThanOrEqualTo(precondition.variable,precondition.number);
            break;
        case "IS_LESS_THAN_OR_EQUAL_TO":
            eventPrecondition = new EventPreConditionIsLessThanOrEqualTo(precondition.variable,precondition.number);
            break;
        default:
            eventPrecondition = null;
            break;
    }

    return eventPrecondition;
}

function loadPreconditions(preconditions) {
    if (preconditions.operator) {
        const operator = preconditions.operator;
        const left = loadPreconditions(preconditions.left);
        const right = preconditions.right ? loadPreconditions(preconditions.right) : null;

        switch (operator) {
            case 'AND':
                return new PreConditionOperatorAnd(left, right);
            case 'OR':
                return new PreConditionOperatorOr(left, right);
            case 'NOT':
                return new PreConditionOperatorNot(left);
            default:
                return null;
        }
    } else {
        return new PreConditionVar(loadPrecondition(preconditions.var));
    }
}

function loadPosconditions(dataPosconditions) {
    const posConditions = [];
    dataPosconditions.forEach(dataAction => {
        const type = dataAction.type;
        let eventPoscondition;

        switch (type) {
            case "END_GAME":
                eventPoscondition = new EventPosConditionEndGame(dataAction.message);
                break;
            case "END_GAME_FORMAT_MESSAGE":
                eventPoscondition = new EventPosConditionEndGameFormatMessage(dataAction.message);
                break;
            case "OBJ_CHANGE_VIEW":
                const objectId = dataAction.object;
                const viewId = dataAction.view;
                eventPoscondition = new EventPosConditionObjChangeState(objectId, viewId);
                break;
            case "OBJ_CHANGE_POSITION":
                const objPositionObjectId = dataAction.object;
                const pos = dataAction.position;
                eventPoscondition = new EventPosConditionObjChangePosition(objPositionObjectId, new Position(pos.x,(pos.y+HEIGHT_INV)));
                break;
            case "OBJ_SCALES":
                const objSizeObjectId = dataAction.object;
                const scale = dataAction.scale;
                eventPoscondition = new EventPosConditionObjScales(objSizeObjectId, new Size(scale.x, scale.y));
                break;
            case "SHOW_MESSAGE":
                const message = dataAction.message;
                const msgpos = dataAction.position;
                eventPoscondition = new EventPosConditionShowMessage(message, new Position(msgpos.x, (msgpos.y+HEIGHT_INV)));
                break;
            case "SHOW_FORMAT_MESSAGE":
                eventPoscondition = new EventPosConditionShowFormatMessage(dataAction.message, new Position(dataAction.position.x, (dataAction.position.y+HEIGHT_INV)));
                break;
            case "OBJ_PUT_INVENTORY":
                const objInventoryObjectId = dataAction.object;
                eventPoscondition = new EventPosConditionObjPutInventory(objInventoryObjectId);
                break;
            case "CHANGE_SCENARIO":
                const scenarioId = dataAction.scenario;
                eventPoscondition = new EventPosConditionChangeScenario(scenarioId);
                break;
            case "REMOVE_OBJ":
                const objId = dataAction.object;
                eventPoscondition = new EventPosConditionRemoveObj(objId);
                break;
            case "PLAY_SOUND":
                const soundId = dataAction.sound;
                const sourceId = dataAction.source_id;
                const sourceType = dataAction.source_type;
                eventPoscondition = new EventPosConditionPlaySound(soundId, sourceId, sourceType);
                break;
            case "QUESTION":
                const question = dataAction.question;
                const answer = dataAction.answer;
                const sucess = new EventEr("sucess",{},loadPosconditions(dataAction.sucess),null);
                const fail = new EventEr("fail",{},loadPosconditions(dataAction.fail),null);
                eventPoscondition = new EventPosConditionQuestion(answer, question, sucess, fail);
                break;
            case "MULTIPLE_CHOICE":
                const mc_question = dataAction.question;
                const mc_answer = dataAction.answer;
                const multipleChoices = dataAction.choices;
                const mc_sucess = new EventEr("sucess",{},loadPosconditions(dataAction.sucess),null);
                const mc_fail = new EventEr("fail",{},loadPosconditions(dataAction.fail),null);
                eventPoscondition = new EventPosConditionMultipleChoice(mc_question,mc_answer,multipleChoices,mc_sucess,mc_fail);
                break;
            case "SEQUENCE":
                const s_question = dataAction.question;
                const sequence = dataAction.sequence;
                const s_sucess = new EventEr("sucess",{},loadPosconditions(dataAction.sucess),null);
                const s_fail = new EventEr("fail",{},loadPosconditions(dataAction.fail),null);
                eventPoscondition = new EventPosConditionSequence(s_question,sequence,s_sucess,s_fail);
                break;
            case "CONNECTIONS":
                const c_question = dataAction.question;
                const list1 = dataAction.list1;
                const list2 = dataAction.list2;
                const c_sucess = new EventEr("sucess",{},loadPosconditions(dataAction.sucess),null);
                const c_fail = new EventEr("fail",{},loadPosconditions(dataAction.fail),null);
                eventPoscondition = new EventPosConditionConnections(c_question,list1,list2,c_sucess,c_fail);
                break;
            case "TRANSITION":
                const transition_id = dataAction.transition;
                eventPoscondition = new EventPosConditionTransition(transition_id);
                break;
            case "VAR_DECREASES":
                eventPoscondition = new EventPosConditionVarDecreases(dataAction.variable,dataAction.number);
                break;
            case "VAR_INCREASES":
                eventPoscondition = new EventPosConditionVarIncreases(dataAction.variable,dataAction.number);
                break;
            case "VAR_BECOMES":
                eventPoscondition = new EventPosConditionVarBecomes(dataAction.variable,dataAction.number);
                break;   
            default:
                break;
        }

        if (eventPoscondition) {
            posConditions.push(eventPoscondition);
        }
    });

    return posConditions;
}

function loadEvents(dataEvents) {
    const events = [];

    dataEvents.forEach(dataEvent => {
        const id = dataEvent.id;
        const dataPreconditions = dataEvent.preconditions || {};
        const dataPosconditions = dataEvent.posconditions;
        const repetitions = dataEvent.repetitions || Infinity;
        const preConditions = new PreConditionTree(loadPreconditions(dataPreconditions));
        const posConditions = loadPosconditions(dataPosconditions);

        events.push(new EventEr(id, preConditions, posConditions, repetitions));
    });

    return events;
}
