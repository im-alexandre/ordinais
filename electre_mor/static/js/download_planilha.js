$('#baixa_planilha').on('click', function () {
    $.ajax({
        url: 'http://electremor.com/download/' + $(this).data('id'),
        method: 'GET',
        xhrFields: {
            responseType: 'blob'
        },
        success: function (data) {
            var a = document.createElement('a');
            var url = window.URL.createObjectURL(data);
            a.href = url;
            a.download = 'resultado.zip';
            document.body.append(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);
        }
    });
});
