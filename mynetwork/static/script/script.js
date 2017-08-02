

function authenticate(){

  var credentials = {
  username: $('#username').val(),
  password: $('#password').val()
};

var csrftoken = jQuery("[name=csrfmiddlewaretoken]").val();

$.post("http://localhost:8000/api-token-auth/", credentials, function(auth) {
  $.ajax({
    type: "POST",
    url: "http://localhost:8000/login/",
    beforeSend: function(xhr) {
      xhr.setRequestHeader("Authorization", "Bearer " + auth.token);
      xhr.setRequestHeader("X-CSRFToken", csrftoken); 
    },
    success: function(data){
      console.log(data);
      alert(data)
    }
  });
}); 

}

