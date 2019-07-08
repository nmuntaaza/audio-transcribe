
$(document).ready(function () {

    "use strict";

    /*
     ----------------------------------------------------------------------
     Preloader
     ----------------------------------------------------------------------
     */
    
    $(".loader").delay(400).fadeOut();
    $(".animationload").delay(400).fadeOut("fast");


    /*
     ----------------------------------------------------------------------
     Animation
     ----------------------------------------------------------------------
     */
    $('.animated').appear(function () {
        var elem = $(this);
        var animation = elem.data('animation');
        if (!elem.hasClass('visible')) {
            var animationDelay = elem.data('animation-delay');
            if (animationDelay) {
                setTimeout(function () {
                    elem.addClass(animation + " visible");
                }, animationDelay);
            } else {
                elem.addClass(animation + " visible");
            }
        }
    });

    /*
     ----------------------------------------------------------------------
     FilePond
     ----------------------------------------------------------------------
     */



}); // End $(document).ready(function(){