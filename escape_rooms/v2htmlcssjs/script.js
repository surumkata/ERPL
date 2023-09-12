//-----------------------------------IMAGES-------------------------------------------

// Altera a src image de um objeto
function changeObjectSrcImage(id, srcImage) {
    const element = document.getElementById(id);
    element.style.backgroundImage = 'url('+srcImage+')';
}

// Altera a src image de um item
function changeItemSrcImage(id, srcImage) {
    var slot = inventory[id]["slot"];
    const container = document.getElementById("slot" + slot);
    const imgElement = container.querySelector("img");
    
    if (imgElement) {
        imgElement.src = srcImage;
        console.log(srcImage);
    } else {
        console.log("Elemento <img> não encontrado no contêiner.");
    }
}

// Altera o style top/left de um elemento
function move(id, top, left) {
    const element = document.getElementById(id);
    element.style.top = top + "px";
    element.style.left = left + "px";
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

//--------------------------------INVENTORY----------------------------------------------

var inventory = {};

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

function addToInventory(id, onclick){
    //busca um slot disponivel no inventario
    var slot = emptyNextSlot();

    //adicionar ao inventario (dicionario)
    inventory[id] = {"slot" : slot, "active" : onclick};

    //adicionar visualmente
    element = document.getElementById("slot" + slot);
    element.className = "inventory-item";

    element.innerHTML = `
        <div class="slot-number">${slot}</div>
        <img src="${id}">
        <div class="zoom-icon" onclick="abrirPopup('lupa_${id}')">&#128269;</div>
    `;
}


function removeItem(id){
    var slot = inventory[id]["slot"];

    delete inventory[id];

    element = document.getElementById("slot" + slot);
    element.className = "empty-slot";
    element.innerHTML = `
        <div class="slot-number">${slot}</div>
        Slot Vazio
    `;
}

//--------------------------------AUXILIARES-------------------------------

function removeObjectOnClick(id){
    element = document.getElementById(id);

    element.onclick = "none";
    element.style.cursor = "default";
}

function removeOnClick(id){

    var slot = inventory[id]["slot"];
    element = document.getElementById("slot" + slot);

    element.onclick = "none";
    element.style.cursor = "default";
}

function changeOnClick(id, func){
    var slot = inventory[id]["slot"];
    element = document.getElementById("slot" + slot);

    element.onclick = func;
}


//-------------------------------POPUP VER IMAGEM--------------------

// Função para abrir o popup de ampliação
function abrirPopup(src) {
    const itemPopup = document.getElementById('item-popup');
    const popupImage = document.getElementById('popup-image');
    
    popupImage.src = src;
    itemPopup.style.display = 'flex';
}

// Função para fechar o popup de ampliação
function fecharPopup() {
    const itemPopup = document.getElementById('item-popup');
    itemPopup.style.display = 'none';
}

// Adicione um evento de clique para fechar o popup quando clicar no botão X
const closePopupButton = document.getElementById('close-popup');
closePopupButton.addEventListener('click', fecharPopup);


//--------------------------------EVENTS----------------------------------------------

function pickObject(id, onclick){
    //adicionar ao inventário
    addToInventory(id, onclick);

    //mensagem na tela
    alert("Pegaste num item e meteste no bolso.");

    //remover objeto da cena
    hidden(id);

    //Adicionar/remover evento onlick;
    if(onclick){
        changeOnClick(id,function(){activeItem(id)});
    }
    else{
        removeOnClick(id);
    }
}


function openObjectByCode(id, msg, code, objects){
    var promptCode = prompt(msg)
    if(promptCode == code){
        element = document.getElementById(id);
        changeObjectSrcImage(id,"open_"+id);
        removeObjectOnClick(id);

        console.log(objects);
        objects.forEach(visible);

    }
    else {
        alert("Código errado!");
    }
    
}


function activeItem(id){

    for (key in inventory){
        if (inventory[key]["active"]){
            desactiveItem(key);
        }
    }

    inventory[id]["active"] = true;
    changeOnClick(id,function(){desactiveItem(id);})
    changeItemSrcImage(id,'active_'+id);
}

function desactiveItem(id){
    inventory[id]["active"] = false;
    changeOnClick(id,function(){activeItem(id);})
    changeItemSrcImage(id,id);
}



/*
function tryDoor() {
    console.log("tryDoor");
    if ("key" in inventory) {
        if(inventory["key"]["active"]){
            removeItem("key");

            door = document.getElementById("door");
            door.style.filter = "brightness(0%)";
            door.onclick = exit;
            alert("Porta aberta");
        }
        else {
            alert("Porta trancada! Talvez com a chave que encontraste abra.");
        }
    }
    else {
        alert("Porta trancada! Precisa de uma chave");
    }
}
*/



