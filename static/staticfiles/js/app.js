function submitFormWithConfirmation(form,
                                    url,
                                    title,
                                    text,
                                    {table_id = null,
                                    select_class = null,
                                    data= null,
                                    data_value= null,
                                    link_attr = null,
                                    modal_id = null,
                                    loadUrl = null,
                                    loadContent = null,
                                    reload = null,
                                    btnClicker = null,
                                    isForm = null} = {}) {

    var formData = new FormData(form);

    if (data) {
        for (var i = 0; i < data.length; i++) {
            formData.append(data_value, data[i]);
        }
    }

    Swal.fire({
        title: title,
        text: text,
        icon: "info",
        showCancelButton: true,
        confirmButtonColor: "#00BFA5",
        confirmButtonText: "Yes",
        allowOutsideClick: false,
        showLoaderOnConfirm: true,
        preConfirm: function () {
            return $.ajax({
                data: formData,
                url: url,
                type: 'POST',
                cache: false,
                contentType: false,
                processData: false,
            });
        },
    }).then(function (response) {
        if (response.value.data == "success") {
            Swal.fire({
                title: "Good job!",
                text: response.value.msg,
                icon: "success",
                confirmButtonColor: "#3498DB",
            }).then((result) => {
                if (result.isConfirmed) {
                    $(form).trigger('reset');

                    if(modal_id) {
                        $(modal_id).modal('hide');
                    }

                    if(select_class) {
                        $(select_class).val('').trigger('change');
                    }

                    if(table_id) {
                        $(table_id).DataTable().ajax.reload();
                    }

                    if(link_attr) {
                        window.location.href = link_attr;
                    }

                    if(loadContent) {
                        $(loadContent).empty();
                        $(loadContent).load(loadUrl);
                    }

                    if(btnClicker) {
                        $(btnClicker).click();
                    }

                    if(reload) {
                        window.location.reload();
                    }
                }
            });
        } else {
            Swal.fire({
                title: "Unauthorized transaction",
                text: response.value.msg,
                icon: "warning",
                confirmButtonColor: "#3498DB",
            });
        }
    });
}

function submitDataWithoutFormConfirmation(list,
                                    url,
                                    title,
                                    text,
                                    {modal_id = null,
                                    table_id = null,
                                    select_class = null,
                                    link_attr = null,
                                    loadUrl = null,
                                    loadContent = null} = {}) {
    Swal.fire({
        title: title,
        text: text,
        icon: "info",
        showCancelButton: true,
        confirmButtonColor: "#00BFA5",
        confirmButtonText: "Yes",
        allowOutsideClick: false,
        showLoaderOnConfirm: true,
        preConfirm: function () {
            return $.ajax({
                data: list,
                url: url,
                type: 'POST',
            });
        },
    }).then(function (response) {
        if (response.value.data == "success") {
            Swal.fire({
                title: "Good job!",
                text: response.value.msg,
                icon: "success",
                confirmButtonColor: "#3498DB",
            }).then((result) => {
                if (result.isConfirmed) {
                    if(modal_id) {
                        $(modal_id).modal('hide');
                    }

                    if(select_class) {
                        $(select_class).val('').trigger('change');
                    }

                    if(table_id) {
                        $(table_id).DataTable().ajax.reload();
                    }

                    if(link_attr) {
                        window.location.href = link_attr;
                    }

                    if(loadContent) {
                        $(loadContent).load(loadUrl);
                    }
                }
            });
        } else {
            Swal.fire({
                title: "Unauthorized transaction",
                text: response.value.msg,
                icon: "warning",
                confirmButtonColor: "#3498DB",
            });
        }
    });
}