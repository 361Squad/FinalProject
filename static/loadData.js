var length = 0;

function loadJSON(){
    $(document).ready(function()
    {
        $.getJSON("/static/data.json", function(data) {
            console.log("success");
        })
        .done(function(data){
            console.log(data.games[0]);
            length = data.games.length;
            for(i = 0; i<length; i++){
                writeToDom(data.games[i].title);
            }
        });
    });
}

function writeToDom(content){
     $("#results").append("<li>" + content + "</li>");
}