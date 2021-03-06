// Habilitar campos com o Radio de PF e PJ
function muda_valor(elemento) {
    var dicionario = {
        '-2': 'É muito mais importante que',
        '-1': 'É mais importante que',
        '0': 'É Tão importante quanto',
        '1': 'É menos importante que',
        '2': 'É muito menos importante que',
    }
    var paragrafo = document.getElementById('paragrafo_' + elemento.id)
    paragrafo.textContent = dicionario[elemento.value]
}

function esconde_monotonico(e){
    if(e.checked){
        var display = '';
    }
    else {
        var display = 'none';
    }
    var pai = e.parentElement.parentElement;
    var seleciona = pai.getElementsByTagName('select');
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
    var dicionario = {
        '-2': 'É muito melhor que',
        '-1': 'É melhor que',
        '0': 'É equivalente a',
        '1': 'É melhor que',
        '2': 'É muito melhor que',
    }
    var paragrafo = document.getElementById('paragrafo_' + elemento.id)
    paragrafo.textContent = dicionario[elemento.value]
}
