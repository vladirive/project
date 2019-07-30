$(function() {

    $("#mensaje").click(function(){
        alert('Saludos Javier');
    });

    $('#btnSignUp').click(function() {       
        $.ajax({
            url: '/signUpUser',
            data: $('form').serialize(),
            type: 'POST',
            success: function(response) {
                var json_obj = $.parseJSON(response); // lo convierte a Array
                $("#msg").html(json_obj['username']);
                console.log(json_obj['username']);
                /*if(json_obj['username'] == '¡ENHORABUENA!, los campos ha sido validados') 
                { window.location.href = "/inicio";}*/              
            },
            error: function(error) {
                console.log(error);
            }
        });
        
    });
});
