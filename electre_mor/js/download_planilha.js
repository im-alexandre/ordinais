$('#baixa_planilha').on('click', function () {
    $.ajax({
        url: 'http://127.0.0.1:8000/download/' + $(this).data('id'),
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
