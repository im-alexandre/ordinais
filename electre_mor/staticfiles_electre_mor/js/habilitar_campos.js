// Habilitar campos com o Radio de PF e PJ
function muda_valor(elemento) {
    var dicionario = {
        '-2': 'is much more important than',
        '-1': 'is more important than',
        '0': 'is as important as',
        '1': 'is less important than',
        '2': 'is much less important than',
    }
    var paragrafo = document.getElementById('paragrafo_' + elemento.id)
    paragrafo.textContent = dicionario[elemento.value]
}

function esconde_monotonico(e){
    if(e.value == "True"){
        var display = '';
    }
    else {
        var display = 'none';
    }
    var pai = e.parentElement.parentElement;
    var seleciona = pai.getElementsByClassName('monotonico');
    seleciona[0].parentElement.setAttribute('style', 'display:' + display);
    var monotonico = pai.getElementsByTagName('td');
    for (let item of monotonico) {
        if (item.innerHTML == 'Monotonico'){
            item.setAttribute('style', 'display:'+display);
        }
    }
}

var chequebox = document.getElementsByClassName('check');
for (let item of chequebox){
    esconde_monotonico(item);
}
function muda_valor_alternativa(elemento) {
    var dicionario_alternativas = {
        '-2': 'is much better than',
        '-1': 'is better than',
        '0': 'is equivalent to',
        '1': 'is worse than',
        '2': 'is much worse than',
    }
    var paragrafo = document.getElementById('paragrafo_' + elemento.id)
    paragrafo.textContent = dicionario_alternativas[elemento.value]
}
