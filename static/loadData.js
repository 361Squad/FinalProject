var length = 0;

function loadJSON(data){
    $(document).ready(function()
    {
        console.log(data.games);
        length = data.games.length;
        for(i = 0; i<length; i++){
            writeToDom(data.games[i].title, data.games[i].fromTitle, i);
        }
    });
}

function writeToDom(recTitle, fromTitle, index){
    $("#results").append("<div><h4>Game# " + (i+1) + "</h4>" + "<div> Recommended: " + recTitle + "</div><div> From: " + fromTitle + "</div></div>");
    $("#results").append("<br>")
}