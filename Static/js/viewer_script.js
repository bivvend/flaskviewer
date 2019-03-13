$(document).ready(function(){
    function getDate(){
           var today = new Date();
       var h = today.getHours();
       var m = today.getMinutes();
       var s = today.getSeconds();
        if(s<10){
            s = "0"+s;
        }
        if (m < 10) {
           m = "0" + m;
       }
       $("#clock").text(h+" : "+m+" : "+s);
       setTimeout(function(){getDate()}, 500);
       }
       
    getDate();
});