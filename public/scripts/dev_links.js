$(document).ready(function(){
    $(".links li").each(function(){
        $(this).mouseenter(function(){
            $(this).fadeTo("fast", 0.9);
            $(this).animate({width: 240}, 150);
        });
        $(this).mouseleave(function(){
            $(this).fadeTo("fast", 1);
            $(this).animate({width: 230}, 150);
        });
        var i = 0;
        var li_links = ["/universe_dump", "/current_hand", "/history", "/get_named_cards", "/api/help", "/deck_maker", "/deck_list", "/uploadform"];
        click_handler = function(url) {
            $("#links-li" + i).click(function(){
                window.location.href=url;
            });
        };
        for(var url in li_links) {
            click_handler(li_links[url]);
            i++;
        }
    });
});
