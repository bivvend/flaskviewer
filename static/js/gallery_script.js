$(document).ready(function(){
    function setupGallery() { 
        Galleria.loadTheme('/static/galleria/themes/classic/galleria.classic.js');
        Galleria.run('.galleria');
        Galleria.run('.galleriaBest');
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
    
    $("#refreshBestButton").click(function(){        
        $.ajax({url:'best_gallery_refresh',
                success: function(resp){
                    console.log(resp);
                    $("#galleryBestWrapper").html(resp);
                    Galleria.loadTheme('/static/galleria/themes/classic/galleria.classic.js');
                    Galleria.run('.galleriaBest');                    
                } 
            
        });
    });
    
    
    setupGallery();
    
});
