var inventory = {};
var lastShow = null;

// Altera a src image de um objeto
function changeSrcImage(id, srcImage) {
    const element = document.getElementById(id);
    element.src = '../../images/'+srcImage;
}

function removeObjectOnClick(id){
    element = document.getElementById(id);

    element.onclick = "none";
    element.style.cursor = "default";
}

//Altera a visibilidade para "hidden" de um elemento
function hidden(id) {
    const element = document.getElementById(id);
    element.style.visibility = "hidden";
}
//Altera a visibilidade para "visible" de um elemento
function visible(id) {
    console.log(id);
    const element = document.getElementById(id);
    console.log(element);
    element.style.visibility = "visible";
}

// Altera o style top/left de um elemento
function move(id, top, left) {
    const element = document.getElementById(id);
    element.style.top = top + "px";
    element.style.left = left + "px";
}

function transform(id, transform) {
    const element = document.getElementById(id);
    element.style.transform = transform;
}


function removeOnClick(id){

    element = document.getElementById(id);

    element.onclick = "none";
    element.style.cursor = "default";
}

function changeOnClick(id, func){
    element = document.getElementById(id);

    element.onclick = func;
}

function activeItem(id){

    for (key in inventory){
        if (inventory[key]["active"]){
            desactiveItem(key);
        }
    }

    inventory[id]["active"] = true;
    changeOnClick(id,function(){desactiveItem(id);})
    changeSrcImage(id,'active_'+id+'.png');
}

function desactiveItem(id){
    inventory[id]["active"] = false;
    changeOnClick(id,function(){activeItem(id);})
    changeSrcImage(id,id+'.png');
}

//Encontra o slot vazio mais pequeno do inventário
function emptyNextSlot() {
    // Crie um array para armazenar todos os IDs existentes
    var existingSlots = [];
    
    // Preencha o array com os IDs existentes
    for (var key in inventory) {
        if (inventory.hasOwnProperty(key)) {
            existingSlots.push(inventory[key].slot);
        }
    }
    
    // Ordene o array de IDs em ordem crescente
    existingSlots.sort(function(a, b) {
        return a - b;
    });
    
    // Encontre o menor ID disponível
    var lowestAvailableSlot = 1;
    for (var i = 0; i < existingSlots.length; i++) {
        if (existingSlots[i] === lowestAvailableSlot) {
            lowestAvailableSlot++;
        } else {
            // Se encontrarmos um espaço vago, retornamos o menor ID disponível
            return lowestAvailableSlot;
        }
    }
    
    // Se não encontrarmos nenhum espaço vago, retornamos o próximo ID
    return lowestAvailableSlot;
}

function getIDbySlot(slot){
    for (id in inventory){
        if (inventory[id]['slot'] == slot){
            return id;
        }
    }
    return null;
}

function addToInventory(id, onclick, slot){

    //adicionar ao inventario (dicionario)
    inventory[id] = {"slot" : slot, "active" : false};
}

function pickupItem(id, onclick){

    var slot = emptyNextSlot();

    //adicionar ao inventário
    addToInventory(id, onclick, slot);

    //mensagem na tela
    alert("Pegaste num item e meteste no bolso.");

    var newLeft =  40 + ((slot-1) * 146);

    //remover objeto da cena
    move(id, 925, newLeft);
    transform(id, "scale(1)");

    visible('eye'+slot);

    //Adicionar/remover evento onlick;
    if(onclick){
        changeOnClick(id,function(){activeItem(id)});
    }
    else{
        removeOnClick(id);
    }
}


function openCofre(id, msg, code, objects){
    var promptCode = prompt(msg)
    if(promptCode == code){
        console.log("acertouu");
        element = document.getElementById(id);
        changeSrcImage(id,"open_"+id+'.png');
        removeObjectOnClick(id);

        console.log(objects);
        objects.forEach(visible);

    }
    else {
        alert("Código errado!");
    }
    
}

function tryDoor(){
    
    if('key' in inventory){
        if(inventory['key']['active']){
            element = document.getElementById('door')
            element.style.filter = "brightness(0%)";
            alert('Porta aberta!')
            end_game()
        }
        else{
            alert("Porta trancada! Tenta usar a chave que tens no inventário!")
        }
    }
    else{
        alert("Porta trancada! Precisa de uma chave para abrir.")
    }
}

function show(slot){
    if (lastShow != null){
        closeView();
    }
    visible('board');
    visible('x');

    var id = getIDbySlot(slot);
    visible(id+'V');
    lastShow = id+'V';
}

function closeView(){
    hidden('board');
    hidden('x');
    hidden(lastShow);
    lastShow = null;
}


function end_game(){
    window.location = "escaped.html";
}