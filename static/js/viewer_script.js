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
    $("#clock").text("Time: " +h+" : "+m+" : "+s);
    setTimeout(function(){
        getDate()}, 500);
    }

    $("#getFrameButton").click(function(){        
        $.ajax({url:'save_frame',
                success: function(resp){
                    console.log(resp);
                    $("#storedImage").attr('src', resp.result + "?t=" + new Date().getTime());
                } 
            
        });
    });
    
    $("#runCycleButton").click(function(){
      $.ajax({url:'run_cycle',
                success: function(resp){
                    console.log(resp);                    
                }             
        });         
    });


       
    getDate();
});
