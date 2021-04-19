// Habilitar campos com o Radio de PF e PJ
$(document).ready(function(){
    $(".pj").hide();
});
$("input[type=radio]").on("change", function(){
    if ($(this).val() == "pessoaFisica"){
        $(".pf").show();
        $(".pj").hide(); 
    } else if ($(this).val() == "pessoaJuridica"){
        $(".pj").show(); 
        $(".pf").hide();
    }
});
