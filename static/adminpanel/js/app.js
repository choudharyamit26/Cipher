$(document).ready(function () {
    // block and unblock user
    $('.blockUnblock_btn input').on('change', function (e) {
        console.log('clicked block button')
        e.preventDefault();
        var value = $(this).val();
        console.log("value",value)
        $("#object_id_block_div").html(`<input hidden="true" id="object_id_block_input" value="` + value + `">`)
        if ($(this).is(':checked')) {
            $('#blockModal').modal({ show: 'false' });
        $("#modal_block_button").click(function () {
        var object_id = $("#object_id_block_input").val();
        console.log('Id ',object_id)
        var protocol = window.location.protocol
        var hostname = window.location.hostname
        var port = window.location.port
        var url = protocol + "//" + hostname + ":" + port + "/adminpanel" + "/block-unblock-user" + "/" + object_id + "/"
        window.location.href = url
    });
        } else {
            $('#unblockModal').modal({ show: 'false' });
        }
    })
});


