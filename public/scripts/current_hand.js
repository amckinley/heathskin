/**
* Handles all the functions for the current hand page
*/
(function($){
    $.get('/current_hand', function(http){
        console.log(http);
    });
})(jQuery);
