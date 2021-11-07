document.querySelectorAll("select").forEach(function(valor){
    valor.setAttribute("readonly", "readonly");
    valor.setAttribute("adia-disabled", "true");
    valor.setAttribute("tabindex", "-1");
});
