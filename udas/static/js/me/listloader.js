function listLoader(url, output_container) {
    $.ajax({
        url: url,
        type: 'get',
        cache: true,
        dataType: 'json',
        beforeSend: function() {
            $(output_container).html('<div class="m-2">Loading...</div>')
        },
        success: function(data) {
            if (data.status != 'error') {
                $(output_container).html(data.html_list)
                addCallbackToJsBtnUpdate();
                addCallbackToJsBtnDelete();
            } else {
                $(output_container).html(data.html_error)
            }
        },
        error: function() {
            $(output_container).html('<div class="m-2 text-danger">Maaf Telah terjadi kesalahan.</div>')
        }
    })
}