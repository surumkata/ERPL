def start(self,start):
    '''start         : er imports? decls? python_block?'''
    children = start.children

def er(self,er):
    '''er            : "EscapeRoom(" er_parameters ")"'''
    children = er.children

def er_parameters(self,er_parameters):
    '''er_parameters : param_title "," param_scenarios "," param_events "," param_transitions "," param_start'''
    children = er_parameters.children

def imports(self,imports):
    '''imports       : import_obj+'''
    children = imports.children

def import_obj(self,import_obj):
    '''import_obj    : "import Object." ID'''
    children = import_obj.children

def decls(self,decls):
    '''decls         : (var|decl)+'''
    children = decls.children

def decl(self,decl):
    '''decl          : add_view|add_object|add_sound'''
    children = decl.children

def add_view(self,add_view):
    '''add_view   : ID         ".add_View"   "(" view   ")"'''
    children = add_view.children

def add_sound(self,add_sound):
    '''add_sound  : ID         ".add_Sound"  "(" sound  ")"'''
    children = add_sound.children

def add_object(self,add_object):
    '''add_object : cenario_id ".add_Object" "(" object ")"'''
    children = add_object.children

def var(self,var):
    '''var   : ID "=" value'''
    children = var.children

def value(self,value):
    '''value : ID|python_call|list_text_constructor|text_constructor|size_constructor|position_constructor|number_constructor|view_constructor|object_constructor|object_imported|sound_constructor|cenario_constructor|event_constructor|challenge_constructor|transition_constructor|draw_constructor'''
    children = value.children

def python_call(self,python_call):
    '''python_call           : python_local|python_function'''
    children = python_call.children

def python_local(self,python_local):
    '''python_local          : "Python.Local." ID'''
    children = python_local.children

def python_function(self,python_function):
    '''python_function       : "Python.Function." FUNC'''
    children = python_function.children

def list_text(self,list_text):
    '''list_text             : list_text_arg|list_text_constructor|list_text_python_call'''
    children = list_text.children

def list_text_arg(self,list_text_arg):
    '''list_text_arg         : ID'''
    children = list_text_arg.children

def list_text_python_call(self,list_text_python_call):
    '''list_text_python_call : python_call'''
    children = list_text_python_call.children

def list_text_constructor(self,list_text_constructor):
    '''list_text_constructor : "[" text ("," text)* "]"'''
    children = list_text_constructor.children

def text(self,text):
    '''text                  : text_arg|text_constructor|text_python_call'''
    children = text.children

def text_arg(self,text_arg):
    '''text_arg              : ID'''
    children = text_arg.children

def text_python_call(self,text_python_call):
    '''text_python_call      : python_call'''
    children = text_python_call.children

def text_constructor(self,text_constructor):
    '''text_constructor      : TEXTO'''
    children = text_constructor.children

def size(self,size):
    '''size                  : size_arg|size_constructor|size_python_call'''
    children = size.children

def size_arg(self,size_arg):
    '''size_arg              : ID'''
    children = size_arg.children

def size_python_call(self,size_python_call):
    '''size_python_call      : python_call'''
    children = size_python_call.children

def size_constructor(self,size_constructor):
    '''size_constructor      : "[" number "," number "]"'''
    children = size_constructor.children

def positions(self,positions):
    '''positions             : "[" position "," position "," position "," position ("," position)* "]"'''
    children = positions.children

def position(self,position):
    '''position              : position_arg|position_constructor|position_python_call'''
    children = position.children

def position_arg(self,position_arg):
    '''position_arg          : ID'''
    children = position_arg.children

def position_python_call(self,position_python_call):
    '''position_python_call  : python_call'''
    children = position_python_call.children

def position_constructor(self,position_constructor):
    '''position_constructor  : "(" number "," number ")"'''
    children = position_constructor.children

def number(self,number):
    '''number                : number_arg|number_constructor|number_python_call'''
    children = number.children

def number_arg(self,number_arg):
    '''number_arg            : ID'''
    children = number_arg.children

def number_python_call(self,number_python_call):
    '''number_python_call    : python_call'''
    children = number_python_call.children

def number_constructor(self,number_constructor):
    '''number_constructor    : NUM'''
    children = number_constructor.children

def integer(self,integer):
    '''integer               : integer_arg|integer_constructor|integer_python_call'''
    children = integer.children

def integer_arg(self,integer_arg):
    '''integer_arg           : ID'''
    children = integer_arg.children

def interger_python_call(self,interger_python_call):
    '''interger_python_call  : python_call'''
    children = interger_python_call.children

def integer_constructor(self,integer_constructor):
    '''integer_constructor   : INT'''
    children = integer_constructor.children

def angle(self,angle):
    '''angle                 : angle_arg|angle_constructor|angle_python_call'''
    children = angle.children

def angle_arg(self,angle_arg):
    '''angle_arg             : ID'''
    children = angle_arg.children

def angle_constructor(self,angle_constructor):
    '''angle_constructor     : python_call'''
    children = angle_constructor.children

def angle_python_call(self,angle_python_call):
    '''angle_python_call     : NUM ("rad"|"°C")'''
    children = angle_python_call.children

def color(self,color):
    '''color                 : color_arg|color_constructor|color_python_call'''
    children = color.children

def color_arg(self,color_arg):
    '''color_arg             : ID'''
    children = color_arg.children

def color_python_call(self,color_python_call):
    '''color_python_call     : python_call'''
    children = color_python_call.children

def color_constructor(self,color_constructor):
    '''color_constructor     : "#" HEXCODE'''
    children = color_constructor.children

def views(self,views):
    '''views                 : "[" view ("," view)* "]"'''
    children = views.children

def view(self,view):
    '''view                  : view_arg|view_constructor_id|view_python_call'''
    children = view.children

def view_arg(self,view_arg):
    '''view_arg              : ID'''
    children = view_arg.children

def view_id(self,view_id):
    '''view_id               : ID'''
    children = view_id.children

def view_python_call(self,view_python_call):
    '''view_python_call      : python_call'''
    children = view_python_call.children

def view_constructor(self,view_constructor):
    '''view_constructor      : view_static|view_animated|view_sketch'''
    children = view_constructor.children

def view_constructor_id(self,view_constructor_id):
    '''view_constructor_id   : view_static_id|view_animated_id|view_sketch_id'''
    children = view_constructor_id.children

def view_static(self,view_static):
    '''view_static           : "View.Static"       "(" param_image ("," param_position)? ("," param_size)? ")"'''
    children = view_static.children

def view_animated(self,view_animated):
    '''view_animated         : "View.Animated"     "(" param_images "," param_repetitions "," param_time_sprite ("," param_position)? ("," param_size)? ")"'''
    children = view_animated.children

def view_sketch(self,view_sketch):
    '''view_sketch           : "View.Sketch"       "(" param_draws ")"'''
    children = view_sketch.children

def view_static_id(self,view_static_id):
    '''view_static_id        : "View.Static." ID   "(" param_image ("," param_position)? ("," param_size)? ")"'''
    children = view_static_id.children

def view_animated_id(self,view_animated_id):
    '''view_animated_id      : "View.Animated." ID "(" param_images "," param_repetitions "," param_time_sprite ("," param_position)? ("," param_size)? ")"'''
    children = view_animated_id.children

def view_sketch_id(self,view_sketch_id):
    '''view_sketch_id        : "View.Sketch." ID "(" param_draws ")"'''
    children = view_sketch_id.children

def draws(self,draws):
    '''draws                 : "[" draw ("," draw)* "]"'''
    children = draws.children

def draw(self,draw):
    '''draw                  : draw_arg|draw_constructor_id|draw_python_call'''
    children = draw.children

def draw_arg(self,draw_arg):
    '''draw_arg              : ID'''
    children = draw_arg.children

def draw_id(self,draw_id):
    '''draw_id               : ID'''
    children = draw_id.children

def draw_python_call(self,draw_python_call):
    '''draw_python_call      : python_call'''
    children = draw_python_call.children

def draw_constructor(self,draw_constructor):
    '''draw_constructor      : draw_rect | draw_polygon | draw_square | draw_circle | draw_line | draw_ellipse | draw_arc | draw_triangle | draw_fill'''
    children = draw_constructor.children

def draw_constructor_id(self,draw_constructor_id):
    '''draw_constructor_id   : draw_rect_id | draw_polygon_id | draw_square_id | draw_circle_id | draw_line_id | draw_ellipse_id | draw_arc_id | draw_triangle_id | draw_fill_id'''
    children = draw_constructor_id.children

def draw_rect(self,draw_rect):
    '''draw_rect             : "Draw.Rect"         "(" param_position "," param_size "," param_tl "," param_tr "," param_bl "," param_br  ")"'''
    children = draw_rect.children

def draw_polygon(self,draw_polygon):
    '''draw_polygon          : "Draw.Polygon"      "(" param_points                                                                       ")"'''
    children = draw_polygon.children

def draw_triangle(self,draw_triangle):
    '''draw_triangle         : "Draw.Triangle"     "(" param_point1   "," param_point2 "," param_point3                                   ")"'''
    children = draw_triangle.children

def draw_line(self,draw_line):
    '''draw_line             : "Draw.Line"         "(" param_point1   "," param_point2                                                    ")"'''
    children = draw_line.children

def draw_ellipse(self,draw_ellipse):
    '''draw_ellipse          : "Draw.Ellipse"      "(" param_position "," param_size                                                      ")"'''
    children = draw_ellipse.children

def draw_arc(self,draw_arc):
    '''draw_arc              : "Draw.Arc"          "(" param_position "," param_size "," param_arcstart "," param_arcstop                 ")"'''
    children = draw_arc.children

def draw_circle(self,draw_circle):
    '''draw_circle           : "Draw.Circle"       "(" param_position "," param_radius                                                    ")"'''
    children = draw_circle.children

def draw_square(self,draw_square):
    '''draw_square           : "Draw.Square"       "(" param_position "," param_width "," param_tl "," param_tr "," param_bl "," param_br ")"'''
    children = draw_square.children

def draw_fill(self,draw_fill):
    '''draw_fill             : "Draw.Fill"         "(" param_color                                                                        ")"'''
    children = draw_fill.children

def draw_rect_id(self,draw_rect_id):
    '''draw_rect_id          : "Draw.Rect." ID     "(" param_position "," param_size "," param_tl "," param_tr "," param_bl "," param_br  ")"'''
    children = draw_rect_id.children

def draw_polygon_id(self,draw_polygon_id):
    '''draw_polygon_id       : "Draw.Polygon." ID  "(" param_points                                                                       ")"'''
    children = draw_polygon_id.children

def draw_triangle_id(self,draw_triangle_id):
    '''draw_triangle_id      : "Draw.Triangle." ID "(" param_point1   "," param_point2 "," param_point3                                   ")"'''
    children = draw_triangle_id.children

def draw_line_id(self,draw_line_id):
    '''draw_line_id          : "Draw.Line." ID     "(" param_point1   "," param_point2                                                    ")"'''
    children = draw_line_id.children

def draw_ellipse_id(self,draw_ellipse_id):
    '''draw_ellipse_id       : "Draw.Ellipse." ID  "(" param_position "," param_size                                                      ")"'''
    children = draw_ellipse_id.children

def draw_arc_id(self,draw_arc_id):
    '''draw_arc_id           : "Draw.Arc." ID      "(" param_position "," param_size "," param_arcstart "," param_arcstop                 ")"'''
    children = draw_arc_id.children

def draw_circle_id(self,draw_circle_id):
    '''draw_circle_id        : "Draw.Circle." ID   "(" param_position "," param_radius                                                    ")"'''
    children = draw_circle_id.children

def draw_square_id(self,draw_square_id):
    '''draw_square_id        : "Draw.Square." ID   "(" param_position "," param_width "," param_tl "," param_tr "," param_bl "," param_br ")"'''
    children = draw_square_id.children

def draw_fill_id(self,draw_fill_id):
    '''draw_fill_id          : "Draw.Fill"         "(" param_color                                                                        ")"'''
    children = draw_fill_id.children

def sounds(self,sounds):
    '''sounds                : "[" sound ("," sound)* "]"'''
    children = sounds.children

def sound(self,sound):
    '''sound                 : sound_arg|sound_constructor_id|sound_python_call'''
    children = sound.children

def sound_arg(self,sound_arg):
    '''sound_arg             : ID'''
    children = sound_arg.children

def sound_id(self,sound_id):
    '''sound_id              : ID'''
    children = sound_id.children

def sound_python_call(self,sound_python_call):
    '''sound_python_call     : python_call'''
    children = sound_python_call.children

def sound_constructor(self,sound_constructor):
    '''sound_constructor     : "Sound" "(" param_source ("," param_loop)?  ")"'''
    children = sound_constructor.children

def sound_constructor_id(self,sound_constructor_id):
    '''sound_constructor_id  : "Sound." ID "(" param_source ("," param_loop)? ")"'''
    children = sound_constructor_id.children

def objects(self,objects):
    '''objects               : "[" object ("," object)* "]"'''
    children = objects.children

def object(self,object):
    '''object                : object_imported_id|object_arg|object_constructor_id|object_python_call'''
    children = object.children

def object_arg(self,object_arg):
    '''object_arg            : ID'''
    children = object_arg.children

def object_id(self,object_id):
    '''object_id             : ID'''
    children = object_id.children

def object_python_call(self,object_python_call):
    '''object_python_call    : python_call'''
    children = object_python_call.children

def object_imported(self,object_imported):
    '''object_imported       : "Object." ID ("(" (param_position|param_size|(param_position "," param_size)) ")")?'''
    children = object_imported.children

def object_constructor(self,object_constructor):
    '''object_constructor    : "Object" "(" (param_view_inicial ",")? param_views ("," param_position)? ("," param_position_reference)? ("," param_size)? ("," param_sounds)? ")"'''
    children = object_constructor.children

def object_imported_id(self,object_imported_id):
    '''object_imported_id    : "Object." ID "." ID ("(" (param_position|param_size|(param_position "," param_size)) ")")?'''
    children = object_imported_id.children

def object_constructor_id(self,object_constructor_id):
    '''object_constructor_id : "Object." ID "(" (param_view_inicial ",")? param_views ("," param_position)? ("," param_position_reference)? ("," param_size)? ("," param_sounds)? ")"'''
    children = object_constructor_id.children

def scenarios(self,scenarios):
    '''scenarios               : "[" cenario ("," cenario)* "]"'''
    children = scenarios.children

def cenario(self,cenario):
    '''cenario                 : cenario_arg|cenario_constructor_id|cenario_python_call'''
    children = cenario.children

def cenario_arg(self,cenario_arg):
    '''cenario_arg             : ID'''
    children = cenario_arg.children

def cenario_id(self,cenario_id):
    '''cenario_id              : ID'''
    children = cenario_id.children

def cenario_python_call(self,cenario_python_call):
    '''cenario_python_call     : python_call'''
    children = cenario_python_call.children

def cenario_constructor(self,cenario_constructor):
    '''cenario_constructor     : "Scenario"     "(" param_view_inicial "," param_views "," param_objects ("," param_sounds)? ("," param_floor)? ("," param_ceil)? ")"'''
    children = cenario_constructor.children

def cenario_constructor_id(self,cenario_constructor_id):
    '''cenario_constructor_id  : "Scenario." ID "(" param_view_inicial "," param_views "," param_objects ("," param_sounds)? ("," param_floor)? ("," param_ceil)? ")"'''
    children = cenario_constructor_id.children

def transitions(self,transitions):
    '''transitions               : "[" transition ("," transition)* "]"'''
    children = transitions.children

def transition(self,transition):
    '''transition                : transition_arg|transition_constructor_id|transition_python_call'''
    children = transition.children

def transition_arg(self,transition_arg):
    '''transition_arg            : ID'''
    children = transition_arg.children

def transition_id(self,transition_id):
    '''transition_id             : ID'''
    children = transition_id.children

def transition_python_call(self,transition_python_call):
    '''transition_python_call    : python_call'''
    children = transition_python_call.children

def transition_constructor(self,transition_constructor):
    '''transition_constructor    : "Transition"     "(" param_background "," param_music "," param_story "," (param_next_scene|param_next_trans)")"'''
    children = transition_constructor.children

def transition_constructor_id(self,transition_constructor_id):
    '''transition_constructor_id : "Transition." ID "(" param_background "," param_music "," param_story "," (param_next_scene|param_next_trans)")"'''
    children = transition_constructor_id.children

def challenge(self,challenge):
    '''challenge                    : challenge_arg|challenge_constructor_id|challenge_python_call'''
    children = challenge.children

def challenge_arg(self,challenge_arg):
    '''challenge_arg                : ID'''
    children = challenge_arg.children

def challenge_python_call(self,challenge_python_call):
    '''challenge_python_call        : python_call'''
    children = challenge_python_call.children

def challenge_constructor(self,challenge_constructor):
    '''challenge_constructor        : challenge_question|challenge_motion|challenge_multiple_choice|challenge_connection|challenge_sequence|challenge_puzzle|challenge_slidepuzzle|challenge_socket'''
    children = challenge_constructor.children

def challenge_question(self,challenge_question):
    '''challenge_question           : "Challenge.Question"         "(" param_question      "," param_answer         "," param_sucess  "," param_fail                  ")"'''
    children = challenge_question.children

def challenge_motion(self,challenge_motion):
    '''challenge_motion             : "Challenge.Motion"           "(" param_motion_object "," param_trigger_object "," param_sucess  "," param_fail                  ")"'''
    children = challenge_motion.children

def challenge_multiple_choice(self,challenge_multiple_choice):
    '''challenge_multiple_choice    : "Challenge.Multiple_Choice"  "(" param_question      "," param_choices        "," param_answer  "," param_sucess "," param_fail ")"'''
    children = challenge_multiple_choice.children

def challenge_connection(self,challenge_connection):
    '''challenge_connection         : "Challenge.Connection"       "(" param_question      "," param_list1          "," param_list2   "," param_sucess "," param_fail ")"'''
    children = challenge_connection.children

def challenge_sequence(self,challenge_sequence):
    '''challenge_sequence           : "Challenge.Sequence"         "(" param_question      "," param_sequence       "," param_sucess  "," param_fail                  ")"'''
    children = challenge_sequence.children

def challenge_puzzle(self,challenge_puzzle):
    '''challenge_puzzle             : "Challenge.Puzzle"           "(" param_image         "," param_sucess                                                           ")"'''
    children = challenge_puzzle.children

def challenge_slidepuzzle(self,challenge_slidepuzzle):
    '''challenge_slidepuzzle        : "Challenge.SlidePuzzle"      "(" param_image         "," param_sucess                                                           ")"'''
    children = challenge_slidepuzzle.children

def challenge_socket(self,challenge_socket):
    '''challenge_socket             : "Challenge.Socket"           "(" param_host          "," param_port           "," param_message "," param_sucess "," param_fail ")"'''
    children = challenge_socket.children

def challenge_constructor_id(self,challenge_constructor_id):
    '''challenge_constructor_id     : challenge_question_id|challenge_motion_id|challenge_multiple_choice_id|challenge_connection_id|challenge_sequence_id|challenge_puzzle_id|challenge_slidepuzzle_id|challenge_socket_id'''
    children = challenge_constructor_id.children

def challenge_question_id(self,challenge_question_id):
    '''challenge_question_id        : "Challenge.Question."         ID "(" param_question      "," param_answer         "," param_sucess   "," param_fail                  ")"'''
    children = challenge_question_id.children

def challenge_motion_id(self,challenge_motion_id):
    '''challenge_motion_id          : "Challenge.Motion."           ID "(" param_motion_object "," param_trigger_object "," param_sucess   "," param_fail                  ")"'''
    children = challenge_motion_id.children

def challenge_multiple_choice_id(self,challenge_multiple_choice_id):
    '''challenge_multiple_choice_id : "Challenge.Multiple_Choice."  ID "(" param_question      "," param_choices        "," param_answer   "," param_sucess "," param_fail ")"'''
    children = challenge_multiple_choice_id.children

def challenge_connection_id(self,challenge_connection_id):
    '''challenge_connection_id      : "Challenge.Connection."       ID "(" param_question      "," param_list1          "," param_list2    "," param_sucess "," param_fail ")"'''
    children = challenge_connection_id.children

def challenge_sequence_id(self,challenge_sequence_id):
    '''challenge_sequence_id        : "Challenge.Sequence."         ID "(" param_question      "," param_sequence       "," param_sucess   "," param_fail                  ")"'''
    children = challenge_sequence_id.children

def challenge_puzzle_id(self,challenge_puzzle_id):
    '''challenge_puzzle_id          : "Challenge.Puzzle."           ID "(" param_image         "," param_sucess                                                            ")"'''
    children = challenge_puzzle_id.children

def challenge_slidepuzzle_id(self,challenge_slidepuzzle_id):
    '''challenge_slidepuzzle_id     : "Challenge.SlidePuzzle."      ID "(" param_image         "," param_sucess                                                            ")"'''
    children = challenge_slidepuzzle_id.children

def challenge_socket_id(self,challenge_socket_id):
    '''challenge_socket_id          : "Challenge.Socket."           ID "(" param_host          "," param_port           "," param_message  "," param_sucess "," param_fail ")"'''
    children = challenge_socket_id.children

def events(self,events):
    '''events               : "[" event ("," event)* "]"'''
    children = events.children

def event(self,event):
    '''event                : event_arg|event_constructor_id|event_python_call'''
    children = event.children

def event_arg(self,event_arg):
    '''event_arg            : ID'''
    children = event_arg.children

def event_id(self,event_id):
    '''event_id             : ID'''
    children = event_id.children

def event_python_call(self,event_python_call):
    '''event_python_call    : python_call'''
    children = event_python_call.children

def event_constructor(self,event_constructor):
    '''event_constructor    : "Event"     "(" param_if "," param_then ("," param_repetitions)? ")"'''
    children = event_constructor.children

def event_constructor_id(self,event_constructor_id):
    '''event_constructor_id : "Event." ID "(" param_if "," param_then ("," param_repetitions)? ")"'''
    children = event_constructor_id.children

def param_answer(self,param_answer):
    '''param_answer             : ("answer"             "=" )? text'''
    children = param_answer.children

def param_background(self,param_background):
    '''param_background         : ("background"         "=" )? view'''
    children = param_background.children

def param_choices(self,param_choices):
    '''param_choices            : ("choices"            "=" )? list_text'''
    children = param_choices.children

def param_events(self,param_events):
    '''param_events             : ("events"             "=" )? events'''
    children = param_events.children

def param_ceil(self,param_ceil):
    '''param_ceil               : ("ceil"               "=" )? number'''
    children = param_ceil.children

def param_floor(self,param_floor):
    '''param_floor              : ("floor"              "=" )? number'''
    children = param_floor.children

def param_fail(self,param_fail):
    '''param_fail               : ("fail"               "=" )? posconditions'''
    children = param_fail.children

def param_host(self,param_host):
    '''param_host               : ("host"               "=" )? text'''
    children = param_host.children

def param_if(self,param_if):
    '''param_if                 : ("if"                 "=" )? preconditions'''
    children = param_if.children

def param_image(self,param_image):
    '''param_image              : ("image"              "=" )? text'''
    children = param_image.children

def param_images(self,param_images):
    '''param_images             : ("images"             "=" )? list_text'''
    children = param_images.children

def param_list1(self,param_list1):
    '''param_list1              : ("list1"              "=" )? list_text'''
    children = param_list1.children

def param_list2(self,param_list2):
    '''param_list2              : ("list2"              "=" )? list_text'''
    children = param_list2.children

def param_message(self,param_message):
    '''param_message            : ("message"            "=" )? text'''
    children = param_message.children

def param_motion_object(self,param_motion_object):
    '''param_motion_object      : ("motion_object"      "=" )? object_id'''
    children = param_motion_object.children

def param_music(self,param_music):
    '''param_music              : ("music"              "=" )? sound'''
    children = param_music.children

def param_next_scene(self,param_next_scene):
    '''param_next_scene         : ("next_scenario"      "=" )? cenario_id'''
    children = param_next_scene.children

def param_next_trans(self,param_next_trans):
    '''param_next_trans         : ("next_transition"    "=" )? transition_id'''
    children = param_next_trans.children

def param_objects(self,param_objects):
    '''param_objects            : ("objects"            "=" )? objects'''
    children = param_objects.children

def param_port(self,param_port):
    '''param_port               : ("port"               "=" )? integer'''
    children = param_port.children

def param_position(self,param_position):
    '''param_position           : ("position"           "=" )? position'''
    children = param_position.children

def param_position_reference(self,param_position_reference):
    '''param_position_reference : ("position_reference" "=" )? POS_REF'''
    children = param_position_reference.children

def param_question(self,param_question):
    '''param_question           : ("question"           "=" )? text'''
    children = param_question.children

def param_repetitions(self,param_repetitions):
    '''param_repetitions        : ("repetitions"        "=" )? integer'''
    children = param_repetitions.children

def param_scenarios(self,param_scenarios):
    '''param_scenarios          : ("scenarios"          "=" )? scenarios'''
    children = param_scenarios.children

def param_sequence(self,param_sequence):
    '''param_sequence           : ("sequence"           "=" )? list_text'''
    children = param_sequence.children

def param_size(self,param_size):
    '''param_size               : ("size"               "=" )? size'''
    children = param_size.children

def param_sounds(self,param_sounds):
    '''param_sounds             : ("sounds"             "=" )? sounds'''
    children = param_sounds.children

def param_source(self,param_source):
    '''param_source             : ("source"             "=" )? text'''
    children = param_source.children

def param_start(self,param_start):
    '''param_start              : ("start"              "=" )? ID'''
    children = param_start.children

def param_story(self,param_story):
    '''param_story              : ("story"              "=" )? list_text'''
    children = param_story.children

def param_sucess(self,param_sucess):
    '''param_sucess             : ("sucess"             "=" )? posconditions'''
    children = param_sucess.children

def param_then(self,param_then):
    '''param_then               : ("then"               "=" )? posconditions'''
    children = param_then.children

def param_time_sprite(self,param_time_sprite):
    '''param_time_sprite        : ("time_sprite"        "=" )? integer'''
    children = param_time_sprite.children

def param_title(self,param_title):
    '''param_title              : ("title"              "=" )? text'''
    children = param_title.children

def param_transitions(self,param_transitions):
    '''param_transitions        : ("transitions"        "=" )? transitions'''
    children = param_transitions.children

def param_trigger_object(self,param_trigger_object):
    '''param_trigger_object     : ("trigger_object"     "=" )? object_id'''
    children = param_trigger_object.children

def param_view_inicial(self,param_view_inicial):
    '''param_view_inicial       : ("initial_view"       "=" )? view_id'''
    children = param_view_inicial.children

def param_views(self,param_views):
    '''param_views              : ("views"              "=" )? views'''
    children = param_views.children

def param_loop(self,param_loop):
    '''param_loop               : ("loop"               "=" )? BOOLEAN'''
    children = param_loop.children

def param_draws(self,param_draws):
    '''param_draws              : ("draws"              "=" )? draws'''
    children = param_draws.children

def param_tl(self,param_tl):
    '''param_tl                 : ("tl"                 "=" )? number'''
    children = param_tl.children

def param_tr(self,param_tr):
    '''param_tr                 : ("tr"                 "=" )? number'''
    children = param_tr.children

def param_bl(self,param_bl):
    '''param_bl                 : ("bl"                 "=" )? number'''
    children = param_bl.children

def param_br(self,param_br):
    '''param_br                 : ("br"                 "=" )? number'''
    children = param_br.children

def param_point1(self,param_point1):
    '''param_point1             : ("point1"             "=" )? position'''
    children = param_point1.children

def param_point2(self,param_point2):
    '''param_point2             : ("point2"             "=" )? position'''
    children = param_point2.children

def param_point3(self,param_point3):
    '''param_point3             : ("point3"             "=" )? position'''
    children = param_point3.children

def param_width(self,param_width):
    '''param_width              : ("width"              "=" )? number'''
    children = param_width.children

def param_radius(self,param_radius):
    '''param_radius             : ("radius"             "=" )? number'''
    children = param_radius.children

def param_points(self,param_points):
    '''param_points             : ("points"             "=" )? positions'''
    children = param_points.children

def param_arcstart(self,param_arcstart):
    '''param_arcstart           : ("arc_start"          "=" )? angle'''
    children = param_arcstart.children

def param_arcstop(self,param_arcstop):
    '''param_arcstop            : ("arc_stop"           "=" )? angle'''
    children = param_arcstop.children

def param_color(self,param_color):
    '''param_color              : ("color"              "=" )? color'''
    children = param_color.children

def preconditions(self,preconditions):
    '''preconditions  : precondition|preconds_and|preconds_ou|preconds_not|preconds_group'''
    children = preconditions.children

def preconds_and(self,preconds_and):
    '''preconds_and   : preconditions "and" preconditions '''
    children = preconds_and.children

def preconds_ou(self,preconds_ou):
    '''preconds_ou    : preconditions "or" preconditions'''
    children = preconds_ou.children

def preconds_not(self,preconds_not):
    '''preconds_not   : "not" preconditions            '''
    children = preconds_not.children

def preconds_group(self,preconds_group):
    '''preconds_group : "(" preconditions ")"          '''
    children = preconds_group.children

def precondition(self,precondition):
    '''precondition            : precond_click_obj | precond_click_not_obj | precond_obj_is_view | precond_ev_already_hap | precond_obj_in_use | precond_already_passed'''
    children = precondition.children

def precond_click_obj(self,precond_click_obj):
    '''precond_click_obj       : "click" object_id                                '''
    children = precond_click_obj.children

def precond_click_not_obj(self,precond_click_not_obj):
    '''precond_click_not_obj   : "click not" object_id                           '''
    children = precond_click_not_obj.children

def precond_obj_is_view(self,precond_obj_is_view):
    '''precond_obj_is_view     : object_id "is" view_id                               '''
    children = precond_obj_is_view.children

def precond_ev_already_hap(self,precond_ev_already_hap):
    '''precond_ev_already_hap  : event_id "already happened"'''
    children = precond_ev_already_hap.children

def precond_obj_in_use(self,precond_obj_in_use):
    '''precond_obj_in_use      : object_id "is in use"           '''
    children = precond_obj_in_use.children

def precond_already_passed(self,precond_already_passed):
    '''precond_already_passed  : number "seconds have already passed"                '''
    children = precond_already_passed.children

def posconditions(self,posconditions):
    '''posconditions         : poscondition ("and" poscondition)*'''
    children = posconditions.children

def poscondition(self,poscondition):
    '''poscondition          : poscond_obj_muda_view|poscond_obj_vai_inv|poscond_fim_de_jogo|poscond_mostra_msg|poscond_obj_muda_tam|poscond_obj_muda_pos|poscond_muda_cena|poscond_remove_obj|poscond_play_sound|poscond_comeca_des|poscond_trans'''
    children = poscondition.children

def poscond_obj_muda_view(self,poscond_obj_muda_view):
    '''poscond_obj_muda_view : object_id "change to" view_id                  '''
    children = poscond_obj_muda_view.children

def poscond_obj_vai_inv(self,poscond_obj_vai_inv):
    '''poscond_obj_vai_inv   : object_id "goes to inventory"         '''
    children = poscond_obj_vai_inv.children

def poscond_fim_de_jogo(self,poscond_fim_de_jogo):
    '''poscond_fim_de_jogo   : "end of game"                      '''
    children = poscond_fim_de_jogo.children

def poscond_mostra_msg(self,poscond_mostra_msg):
    '''poscond_mostra_msg    : "show message" text "in" position'''
    children = poscond_mostra_msg.children

def poscond_obj_muda_tam(self,poscond_obj_muda_tam):
    '''poscond_obj_muda_tam  : object_id "scales into" size     '''
    children = poscond_obj_muda_tam.children

def poscond_obj_muda_pos(self,poscond_obj_muda_pos):
    '''poscond_obj_muda_pos  : object_id "move to" position     '''
    children = poscond_obj_muda_pos.children

def poscond_muda_cena(self,poscond_muda_cena):
    '''poscond_muda_cena     : "change to scenario" cenario_id                '''
    children = poscond_muda_cena.children

def poscond_remove_obj(self,poscond_remove_obj):
    '''poscond_remove_obj    : object_id "is removed"           '''
    children = poscond_remove_obj.children

def poscond_play_sound(self,poscond_play_sound):
    '''poscond_play_sound    : "play" sound_id "of" ID                        '''
    children = poscond_play_sound.children

def poscond_comeca_des(self,poscond_comeca_des):
    '''poscond_comeca_des    : "start challenge" challenge_arg                '''
    children = poscond_comeca_des.children

def poscond_trans(self,poscond_trans):
    '''poscond_trans         : "transition" transition_id'''
    children = poscond_trans.children

def python_block(self,python_block):
    '''python_block : "__Python__" PYTHON_CODE'''
    children = python_block.children

def INICIAL(self,INICIAL):
    '''INICIAL : /inicial/'''
    children = INICIAL.children

def REVERSE(self,REVERSE):
    '''REVERSE : /\.reverse\(\)/'''
    children = REVERSE.children

def ID(self,ID):
    '''ID            : /[a-z][\w\-_]*/'''
    children = ID.children

def VAR(self,VAR):
    '''VAR           : /\.[a-z][\w\-_]*/'''
    children = VAR.children

def ARGN(self,ARGN):
    '''ARGN          : /\$\d+/'''
    children = ARGN.children

def PYTHON_CODE(self,PYTHON_CODE):
    '''PYTHON_CODE   : /(.|\n)+/'''
    children = PYTHON_CODE.children

def FUNC(self,FUNC):
    '''FUNC          : /\w+\((?:[^()]*|\([^()]*\))*\)/'''
    children = FUNC.children

def BOOLEAN(self,BOOLEAN):
    '''BOOLEAN       : /yes|no/'''
    children = BOOLEAN.children

def POS_REF(self,POS_REF):
    '''POS_REF       : /floor|ceil/'''
    children = POS_REF.children

def HEXCODE(self,HEXCODE):
    '''HEXCODE       : /[0-9a-fA-F]{6}/'''
    children = HEXCODE.children

def INT(self,INT):
    '''INT           : /(-|\+)?\d+/'''
    children = INT.children

def COMMENT(self,COMMENT):
    '''COMMENT: /#[^\n]*/'''
    children = COMMENT.children

