from lark.visitors import Interpreter
from lark import Lark

class Interpreter(Interpreter):
    def __init__(self):
        pass

    def start(self,start):
        '''start : er imps? atrbs? python_block?'''
        elems = start.children

    def er(self,er):
        '''er : "EscapeRoom(" er_parameters ")"'''
        elems = er.children

    def er_parameters(self,er_parameters):
        '''er_parameters : param_titulo "," param_tamanho "," param_cenarios "," param_eventos "," param_transicoes'''
        elems = er_parameters.children

    def imps(self,imps):
        '''imps : import_obj+'''
        elems = imps.children

    def import_obj(self,import_obj):
        '''import_obj : "importa Objeto." ID'''
        elems = import_obj.children

    def atrbs(self,atrbs):
        '''atrbs : atrb+'''
        elems = atrbs.children

    def atrb(self,atrb):
        '''atrb : ARG "=" value'''
        elems = atrb.children

    def value(self,value):
        '''value : ID|python_call|lista_texto_constructor|texto_constructor|tamanho_constructor|posicao_constructor|numero_constructor|estado_constructor|objeto_constructor|som_constructor|cenario_constructor|evento_constructor|desafio_constructor|transicao_constructor'''
        elems = value.children

    def python_call(self,python_call):
        '''python_call : python_local|python_function'''
        elems = python_call.children

    def python_local(self,python_local):
        '''python_local : "Python.Local." ID'''
        elems = python_local.children

    def python_function(self,python_function):
        '''python_function : "Python.Function." FUNC'''
        elems = python_function.children

    def lista_texto(self,lista_texto):
        '''lista_texto : lista_texto_arg|lista_texto_constructor|lista_texto_python_call'''
        elems = lista_texto.children

    def lista_texto_arg(self,lista_texto_arg):
        '''lista_texto_arg : ID'''
        elems = lista_texto_arg.children

    def lista_texto_python_call(self,lista_texto_python_call):
        '''lista_texto_python_call : python_call'''
        elems = lista_texto_python_call.children

    def lista_texto_constructor(self,lista_texto_constructor):
        '''lista_texto_constructor : "[" texto ("," texto)* "]"'''
        elems = lista_texto_constructor.children

    def texto(self,texto):
        '''texto : texto_arg|texto_constructor|texto_python_call'''
        elems = texto.children

    def texto_arg(self,texto_arg):
        '''texto_arg : ID'''
        elems = texto_arg.children

    def texto_python_call(self,texto_python_call):
        '''texto_python_call : python_call'''
        elems = texto_python_call.children

    def texto_constructor(self,texto_constructor):
        '''texto_constructor : TEXTO'''
        elems = texto_constructor.children

    def tamanho(self,tamanho):
        '''tamanho : tamanho_arg|tamanho_constructor|tamanho_python_call'''
        elems = tamanho.children

    def tamanho_arg(self,tamanho_arg):
        '''tamanho_arg : ID'''
        elems = tamanho_arg.children

    def tamanho_python_call(self,tamanho_python_call):
        '''tamanho_python_call : python_call'''
        elems = tamanho_python_call.children

    def tamanho_constructor(self,tamanho_constructor):
        '''tamanho_constructor : "[" NUM "," NUM "]"'''
        elems = tamanho_constructor.children

    def posicao(self,posicao):
        '''posicao : posicao_arg|posicao_constructor|posicao_python_call'''
        elems = posicao.children

    def posicao_arg(self,posicao_arg):
        '''posicao_arg : ID'''
        elems = posicao_arg.children

    def posicao_python_call(self,posicao_python_call):
        '''posicao_python_call : python_call'''
        elems = posicao_python_call.children

    def posicao_constructor(self,posicao_constructor):
        '''posicao_constructor : "(" NUM "," NUM ")"'''
        elems = posicao_constructor.children

    def numero(self,numero):
        '''numero : numero_arg|numero_constructor|numero_python_call'''
        elems = numero.children

    def numero_arg(self,numero_arg):
        '''numero_arg : ID'''
        elems = numero_arg.children

    def numero_python_call(self,numero_python_call):
        '''numero_python_call : python_call'''
        elems = numero_python_call.children

    def numero_constructor(self,numero_constructor):
        '''numero_constructor : NUM'''
        elems = numero_constructor.children

    def estados(self,estados):
        '''estados : "[" estado ("," estado)* "]"'''
        elems = estados.children

    def estado(self,estado):
        '''estado : estado_arg|estado_constructor|estado_python_call'''
        elems = estado.children

    def estado_arg(self,estado_arg):
        '''estado_arg : ID'''
        elems = estado_arg.children

    def estado_python_call(self,estado_python_call):
        '''estado_python_call : python_call'''
        elems = estado_python_call.children

    def estado_constructor(self,estado_constructor):
        '''estado_constructor : estado_estatico|estado_dinamico'''
        elems = estado_constructor.children

    def estado_estatico(self,estado_estatico):
        '''estado_estatico : "Estado.Estático" "(" param_imagem ("," param_posicao)? ("," param_tamanho)? ")"'''
        elems = estado_estatico.children

    def estado_dinamico(self,estado_dinamico):
        '''estado_dinamico : "Estado.Dinâmico" "(" param_imagens "," param_repeticoes "," param_time_sprite ("," param_posicao)? ("," param_tamanho)? ")"'''
        elems = estado_dinamico.children

    def sons(self,sons):
        '''sons : "[" som ("," som)* "]"'''
        elems = sons.children

    def som(self,som):
        '''som : som_arg|som_constructor|som_python_call'''
        elems = som.children

    def som_arg(self,som_arg):
        '''som_arg : ID'''
        elems = som_arg.children

    def som_python_call(self,som_python_call):
        '''som_python_call : python_call'''
        elems = som_python_call.children

    def som_constructor(self,som_constructor):
        '''som_constructor : "Som" "(" param_fonte ")"'''
        elems = som_constructor.children

    def objetos(self,objetos):
        '''objetos : "[" objeto ("," objeto)* "]"'''
        elems = objetos.children

    def objeto(self,objeto):
        '''objeto : objeto_arg|objeto_constructor|objeto_python_call'''
        elems = objeto.children

    def objeto_arg(self,objeto_arg):
        '''objeto_arg : ID'''
        elems = objeto_arg.children

    def objeto_python_call(self,objeto_python_call):
        '''objeto_python_call : python_call'''
        elems = objeto_python_call.children

    def objeto_constructor(self,objeto_constructor):
        '''objeto_constructor : "Objeto" "(" (param_estado_inicial ",")? param_estados ("," param_posicao)? ("," param_tamanho)? ("," param_sons)? ")"'''
        elems = objeto_constructor.children

    def cenarios(self,cenarios):
        '''cenarios : "[" cenario ("," cenario)* "]"'''
        elems = cenarios.children

    def cenario(self,cenario):
        '''cenario : cenario_arg|cenario_constructor|cenario_python_call'''
        elems = cenario.children

    def cenario_arg(self,cenario_arg):
        '''cenario_arg : ID'''
        elems = cenario_arg.children

    def cenario_python_call(self,cenario_python_call):
        '''cenario_python_call : python_call'''
        elems = cenario_python_call.children

    def cenario_constructor(self,cenario_constructor):
        '''cenario_constructor : "Cenário" "(" param_estado_inicial "," param_estados "," param_objetos ("," param_sons)? ")"'''
        elems = cenario_constructor.children

    def transicoes(self,transicoes):
        '''transicoes : "[" transicao ("," transicao)* "]"'''
        elems = transicoes.children

    def transicao(self,transicao):
        '''transicao : transicao_arg|transicao_constructor|transicao_python_call'''
        elems = transicao.children

    def transicao_arg(self,transicao_arg):
        '''transicao_arg : ID'''
        elems = transicao_arg.children

    def transicao_python_call(self,transicao_python_call):
        '''transicao_python_call : python_call'''
        elems = transicao_python_call.children

    def transicao_constructor(self,transicao_constructor):
        '''transicao_constructor : "Transição" "(" param_fundo "," param_musica "," param_historia "," (param_prox_cena|param_prox_trans)")"'''
        elems = transicao_constructor.children

    def desafio(self,desafio):
        '''desafio : desafio_arg|desafio_constructor|desafio_python_call'''
        elems = desafio.children

    def desafio_arg(self,desafio_arg):
        '''desafio_arg : ID'''
        elems = desafio_arg.children

    def desafio_python_call(self,desafio_python_call):
        '''desafio_python_call : python_call'''
        elems = desafio_python_call.children

    def desafio_constructor(self,desafio_constructor):
        '''desafio_constructor : desafio_pergunta|desafio_arrasta|desafio_escolha_multipla|desafio_conexao|desafio_sequencia|desafio_puzzle|desafio_slidepuzzle|desafio_socket'''
        elems = desafio_constructor.children

    def desafio_pergunta(self,desafio_pergunta):
        '''desafio_pergunta : "Desafio.Pergunta" "(" param_pergunta "," param_resposta "," param_acerto "," param_falha ")"'''
        elems = desafio_pergunta.children

    def desafio_arrasta(self,desafio_arrasta):
        '''desafio_arrasta : "Desafio.Arrasta" "(" param_objeto "," param_acerto "," param_falha ")"'''
        elems = desafio_arrasta.children

    def desafio_escolha_multipla(self,desafio_escolha_multipla):
        '''desafio_escolha_multipla : "Desafio.Escolha_Múltipla" "(" param_pergunta "," param_escolhas "," param_resposta "," param_acerto "," param_falha ")"'''
        elems = desafio_escolha_multipla.children

    def desafio_conexao(self,desafio_conexao):
        '''desafio_conexao : "Desafio.Conexão" "(" param_pergunta "," param_lista1 "," param_lista2 "," param_acerto "," param_falha ")"'''
        elems = desafio_conexao.children

    def desafio_sequencia(self,desafio_sequencia):
        '''desafio_sequencia : "Desafio.Sequência" "(" param_pergunta "," param_sequencia "," param_acerto "," param_falha ")"'''
        elems = desafio_sequencia.children

    def desafio_puzzle(self,desafio_puzzle):
        '''desafio_puzzle : "Desafio.Puzzle" "(" param_imagem "," param_acerto ")"'''
        elems = desafio_puzzle.children

    def desafio_slidepuzzle(self,desafio_slidepuzzle):
        '''desafio_slidepuzzle : "Desafio.SlidePuzzle" "(" param_imagem "," param_acerto ")"'''
        elems = desafio_slidepuzzle.children

    def desafio_socket(self,desafio_socket):
        '''desafio_socket : "Desafio.Socket" "(" param_host "," param_port "," param_mensagem "," param_acerto "," param_falha ")"'''
        elems = desafio_socket.children

    def eventos(self,eventos):
        '''eventos : "[" evento ("," evento)* "]"'''
        elems = eventos.children

    def evento(self,evento):
        '''evento : evento_arg|evento_constructor|evento_python_call'''
        elems = evento.children

    def evento_arg(self,evento_arg):
        '''evento_arg : ID'''
        elems = evento_arg.children

    def evento_python_call(self,evento_python_call):
        '''evento_python_call : python_call'''
        elems = evento_python_call.children

    def evento_constructor(self,evento_constructor):
        '''evento_constructor : "Evento" "(" (param_se ",")? param_entao ("," param_repeticoes)? ")"'''
        elems = evento_constructor.children

    def param_acerto(self,param_acerto):
        '''param_acerto : "acerto" "=" evento_arg'''
        elems = param_acerto.children

    def param_cenarios(self,param_cenarios):
        '''param_cenarios : "cenários" "=" cenarios'''
        elems = param_cenarios.children

    def param_entao(self,param_entao):
        '''param_entao : "então" "=" poscondicoes'''
        elems = param_entao.children

    def param_estado_inicial(self,param_estado_inicial):
        '''param_estado_inicial : "estado_inicial" "=" estado_arg'''
        elems = param_estado_inicial.children

    def param_estados(self,param_estados):
        '''param_estados : "estados" "=" estados'''
        elems = param_estados.children

    def param_escolhas(self,param_escolhas):
        '''param_escolhas : "escolhas" "=" lista_texto'''
        elems = param_escolhas.children

    def param_eventos(self,param_eventos):
        '''param_eventos : "eventos" "=" eventos'''
        elems = param_eventos.children

    def param_falha(self,param_falha):
        '''param_falha : "falha" "=" evento_arg'''
        elems = param_falha.children

    def param_fonte(self,param_fonte):
        '''param_fonte : "fonte" "=" texto'''
        elems = param_fonte.children

    def param_fundo(self,param_fundo):
        '''param_fundo : "fundo" "=" estado'''
        elems = param_fundo.children

    def param_historia(self,param_historia):
        '''param_historia : "história" "=" texto'''
        elems = param_historia.children

    def param_host(self,param_host):
        '''param_host : "host" "=" texto'''
        elems = param_host.children

    def param_imagem(self,param_imagem):
        '''param_imagem : "imagem" "=" texto'''
        elems = param_imagem.children

    def param_imagens(self,param_imagens):
        '''param_imagens : "imagens" "=" lista_texto'''
        elems = param_imagens.children

    def param_lista1(self,param_lista1):
        '''param_lista1 : "lista1" "=" lista_texto'''
        elems = param_lista1.children

    def param_lista2(self,param_lista2):
        '''param_lista2 : "lista2" "=" lista_texto'''
        elems = param_lista2.children

    def param_mensagem(self,param_mensagem):
        '''param_mensagem : "mensagem" "=" texto'''
        elems = param_mensagem.children

    def param_musica(self,param_musica):
        '''param_musica : "música" "=" som'''
        elems = param_musica.children

    def param_objeto(self,param_objeto):
        '''param_objeto : "objeto" "=" objeto_arg'''
        elems = param_objeto.children

    def param_objetos(self,param_objetos):
        '''param_objetos : "objetos" "=" objetos'''
        elems = param_objetos.children

    def param_pergunta(self,param_pergunta):
        '''param_pergunta : "pergunta" "=" texto'''
        elems = param_pergunta.children

    def param_port(self,param_port):
        '''param_port : "port" "=" numero'''
        elems = param_port.children

    def param_posicao(self,param_posicao):
        '''param_posicao : "posição" "=" posição'''
        elems = param_posicao.children

    def param_prox_cena(self,param_prox_cena):
        '''param_prox_cena : "próxima_cena" "=" cenario_arg'''
        elems = param_prox_cena.children

    def param_prox_trans(self,param_prox_trans):
        '''param_prox_trans : "próxima_transição" "=" transicao_arg'''
        elems = param_prox_trans.children

    def param_se(self,param_se):
        '''param_se : "se" "=" precondicoes'''
        elems = param_se.children

    def param_sequencia(self,param_sequencia):
        '''param_sequencia : "sequência" "=" lista_texto'''
        elems = param_sequencia.children

    def param_sons(self,param_sons):
        '''param_sons : "sons" "=" sons'''
        elems = param_sons.children

    def param_repeticoes(self,param_repeticoes):
        '''param_repeticoes : "repetições" "=" numero'''
        elems = param_repeticoes.children

    def param_resposta(self,param_resposta):
        '''param_resposta : "resposta" "=" texto'''
        elems = param_resposta.children

    def param_tamanho(self,param_tamanho):
        '''param_tamanho : "tamanho" "=" tamanho'''
        elems = param_tamanho.children

    def param_time_sprite(self,param_time_sprite):
        '''param_time_sprite : "time_sprite" "=" numero'''
        elems = param_time_sprite.children

    def param_titulo(self,param_titulo):
        '''param_titulo : "título" "=" texto'''
        elems = param_titulo.children

    def param_transicoes(self,param_transicoes):
        '''param_transicoes : "transições" "=" transicoes'''
        elems = param_transicoes.children

    def precondicoes(self,precondicoes):
        '''precondicoes : precondicao|preconds_e|preconds_ou|preconds_nao|preconds_grupo'''
        elems = precondicoes.children

    def preconds_e(self,preconds_e):
        '''preconds_e : precondicoes "e" precondicoes'''
        elems = preconds_e.children

    def preconds_ou(self,preconds_ou):
        '''preconds_ou : precondicoes "ou" precondicoes'''
        elems = preconds_ou.children

    def preconds_nao(self,preconds_nao):
        '''preconds_nao : "não" precondicoes'''
        elems = preconds_nao.children

    def preconds_grupo(self,preconds_grupo):
        '''preconds_grupo : "(" precondicoes ")"'''
        elems = preconds_grupo.children

    def precondicao(self,precondicao):
        '''precondicao : precond_clique_obj | precond_clique_nao_obj | precond_obj_esta_est | precond_clique_obj_depois_ev | precond_obj_uso'''
        elems = precondicao.children

    def precond_clique_obj(self,precond_clique_obj):
        '''precond_clique_obj : "clique" objeto_arg'''
        elems = precond_clique_obj.children

    def precond_clique_nao_obj(self,precond_clique_nao_obj):
        '''precond_clique_nao_obj : "clique não" objeto_arg'''
        elems = precond_clique_nao_obj.children

    def precond_obj_esta_est(self,precond_obj_esta_est):
        '''precond_obj_esta_est : objeto_arg "está" estado_arg'''
        elems = precond_obj_esta_est.children

    def precond_clique_obj_depois_ev(self,precond_clique_obj_depois_ev):
        '''precond_clique_obj_depois_ev : "clique" objeto_arg "depois de" evento_arg "ter acontecido"'''
        elems = precond_clique_obj_depois_ev.children

    def precond_obj_uso(self,precond_obj_uso):
        '''precond_obj_uso : objeto_arg "está em uso"'''
        elems = precond_obj_uso.children

    def poscondicoes(self,poscondicoes):
        '''poscondicoes : poscondicao ("e" poscondicao)*'''
        elems = poscondicoes.children

    def poscondicao(self,poscondicao):
        '''poscondicao : poscond_obj_muda_est|poscond_obj_vai_inv|poscond_fim_de_jogo|poscond_mostra_msg|poscond_obj_muda_tam|poscond_obj_muda_pos|poscond_muda_cena|poscond_remove_obj|poscond_toca_som|poscond_comeca_des|poscond_trans'''
        elems = poscondicao.children

    def poscond_obj_muda_est(self,poscond_obj_muda_est):
        '''poscond_obj_muda_est : objeto_arg "muda para" estado_arg'''
        elems = poscond_obj_muda_est.children

    def poscond_obj_vai_inv(self,poscond_obj_vai_inv):
        '''poscond_obj_vai_inv : objeto_arg "vai para o inventário"'''
        elems = poscond_obj_vai_inv.children

    def poscond_fim_de_jogo(self,poscond_fim_de_jogo):
        '''poscond_fim_de_jogo : "fim de jogo"'''
        elems = poscond_fim_de_jogo.children

    def poscond_mostra_msg(self,poscond_mostra_msg):
        '''poscond_mostra_msg : "mostra mensagem" text'''
        elems = poscond_mostra_msg.children

    def poscond_obj_muda_tam(self,poscond_obj_muda_tam):
        '''poscond_obj_muda_tam : objeto_arg "muda tamanho para" tamanho'''
        elems = poscond_obj_muda_tam.children

    def poscond_obj_muda_pos(self,poscond_obj_muda_pos):
        '''poscond_obj_muda_pos : objeto_arg "muda posição para" posicao'''
        elems = poscond_obj_muda_pos.children

    def poscond_muda_cena(self,poscond_muda_cena):
        '''poscond_muda_cena : "muda para cena" cenario_arg'''
        elems = poscond_muda_cena.children

    def poscond_remove_obj(self,poscond_remove_obj):
        '''poscond_remove_obj : objeto_arg "é removid" ("o"|"a")'''
        elems = poscond_remove_obj.children

    def poscond_toca_som(self,poscond_toca_som):
        '''poscond_toca_som : "toca" som_arg "do" objeto_arg'''
        elems = poscond_toca_som.children

    def poscond_comeca_des(self,poscond_comeca_des):
        '''poscond_comeca_des : "começa desafio" desafio_arg'''
        elems = poscond_comeca_des.children

    def poscond_trans(self,poscond_trans):
        '''poscond_trans : "transição" transicao_arg'''
        elems = poscond_trans.children
