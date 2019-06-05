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
    
    $("#stepPlusButton").click(function(){        
        $.ajax({url:'step_plus',
                success: function(resp){
                    console.log(resp);
                    $("#countLabel").text("Stepper counts = " + resp.result)
                    
                } 
            
        });
    });
    
    $("#stepMinusButton").click(function(){        
        $.ajax({url:'step_minus',
                success: function(resp){
                    console.log(resp);
                    $("#countLabel").text("Stepper counts = " + resp.result)
                } 
            
        });
    });
    
    $("#stepHomeButton").click(function(){        
        $.ajax({url:'step_home',
                success: function(resp){
                    console.log(resp);
                    $("#countLabel").text("Stepper counts = " + resp.result)
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
    
    $("#runProcessingButton").click(function(){
        $ .ajax({url:'run_processing',
                success: function(resp){
                    console.log(resp);                    
                }             
        });         
    
    
    });

    getDate();
});
