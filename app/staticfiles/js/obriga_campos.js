document.querySelectorAll("select").forEach(function(valor){
    valor.setAttribute("readonly", "readonly");
    valor.setAttribute("adia-disabled", "true");
    valor.setAttribute("tabindex", "-1");
});

document.querySelectorAll("input").forEach(function(valor){
    valor.setAttribute("required", " ");
});
console.log('foi');
