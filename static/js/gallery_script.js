$(document).ready(function(){
    function setupGallery() { 
        Galleria.loadTheme('/static/galleria/themes/classic/galleria.classic.js');
        Galleria.run('.galleria');
    }
    
    $("#refreshButton").click(function(){        
        $.ajax({url:'gallery_refresh',
                success: function(resp){
                    console.log(resp);
                    $("#galleryWrapper").html(resp);
                    Galleria.loadTheme('/static/galleria/themes/classic/galleria.classic.js');
                    Galleria.run('.galleria');                    
                } 
            
        });
    });
    
    
    setupGallery();
    
});
