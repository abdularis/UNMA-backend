function addCallback(element) {
    $(element).click(function(event) {
        $.ajax({
            url: $(this).data('href'),
            type: 'get',
            cache: true,
            dataType: 'json',
            beforeSend: function() {
                $('#formModal').modal('show')
                $('#formModal .modal-content').html('<div class="modal-body">Loading...</div>')
            },
            success: function(data) {
                if (data.status != 'error') {
                    $('#formModal .modal-content').html(data.html_form)
                } else {
                    $('#formModal .modal-content').html(data.html_error)
                }
            },
            error: function() {
                $('#formModal .modal-content').html('<div class="modal-body text-danger">Telah terjadi kesalahan.</div>')
            }
        })
    });
}

function addCallbackToJsBtnUpdate() {
    $('.js-btn-update').off()
    addCallback('.js-btn-update');
}

function addCallbackToJsBtnCreate() {
    $('.js-btn-create').off()
    addCallback('.js-btn-create');
}

function addCallbackToJsBtnDelete() {
    $('.js-btn-delete').off()
    addCallback('.js-btn-delete');
}

function addOnSubmitEventHandler(form_selector, on_success) {
    $('#formModal').on('submit', form_selector, function(event) {
        event.preventDefault();
        var form = $(this)
        var formData = new FormData($(this)[0]);
        $.ajax({
            url: form.attr('action'),
            data: formData,
            type: form.attr('method'),
            cache: false,
            contentType: false,
            processData: false,
            beforeSend: function() {
                $('#formModal .modal-content input').prop('disabled', true)
                $('#formModal .modal-content button').prop('disabled', true)
                $('.img-progress').show(500)
            },
            success: function(data) {
                if (data.status == 'success') {
                    $('#formModal').modal('hide')
                    $(".js-dynamic-table").html(data.html_list);
                    addCallbackToJsBtnUpdate();
                    addCallbackToJsBtnDelete();
                } else if (data.status == 'invalid') {
                    $('#formModal .modal-content').html(data.html_form)
                } else {
                    $('#formModal .modal-content').html(data.html_error)
                }
            },
            error: function(data) {
                $('#formModal .modal-content').html('<div class="modal-body text-danger">Telah terjadi kesalahan.</div>')
            }
        });
    });
}


addCallbackToJsBtnCreate();
addOnSubmitEventHandler("#newForm");
addOnSubmitEventHandler("#editForm");
addOnSubmitEventHandler('#deleteForm');