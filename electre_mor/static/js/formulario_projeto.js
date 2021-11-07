var classes = document.getElementById('id_qtde_classes');
var alternativas = document.getElementById('id_qtde_alternativas');
function valida_classes() {
    var min_classes = alternativas.value;

    classes.setAttribute('max', min_classes);
    if (classes.value > min_classes) {
        classes.value = min_classes;
    }
    classes.setAttribute('style', 'width: 226px')
}

classes.setAttribute('min', 2)
document.getElementById('id_qtde_criterios').setAttribute('min', 2)
document.getElementById('id_lamb').setAttribute('step', 0.01)
document.getElementById('id_lamb').setAttribute('min', 0.5)
document.getElementById('id_lamb').setAttribute('max', 1)
document.getElementById('id_qtde_decisores').setAttribute('min', 1)
document.getElementById('id_qtde_alternativas').setAttribute('min', 2)
alternativas.setAttribute('onchange', 'valida_classes()')
