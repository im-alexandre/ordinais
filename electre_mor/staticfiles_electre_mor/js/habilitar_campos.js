// Habilitar campos com o Radio de PF e PJ
var dicionario = {
    '-2': 'É muito menos importante que',
    '-1': 'É Menos importante que',
    '0': 'É Tão importante quanto',
    '1': 'É Mais importante que',
    '2': 'É Muito mais importante que',
}
function muda_valor(elemento) {
    var paragrafo = document.getElementById('paragrafo_' + elemento.id)
    paragrafo.textContent = dicionario[elemento.value]
}
