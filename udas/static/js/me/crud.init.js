function registerOpsButton() {
    registerJsUpdateButton();
    registerJsDeleteButton();
}

registerJsCreateButton();
registerOpsButton();

registerAsyncFormSubmission("#newForm", function(data) {
    $(".js-dynamic-table").html(data.html_list);
    registerOpsButton();
});

registerAsyncFormSubmission("#editForm", function(data) {
    $(".js-dynamic-table").html(data.html_list);
    registerOpsButton();
});

registerAsyncFormSubmission('#deleteForm', function(data) {
    $(".js-dynamic-table").html(data.html_list);
    registerOpsButton();
});