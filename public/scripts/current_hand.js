/**
* Handles all the functions for the current hand page
*/
(function($){

    var handItemTemplate = " " +
        "<li>"+
        "</li>"+
    " ";

    $.get('api/current_hand', function(http){
        $.each(http.cards, function(idx, card){
            $('.hand').append('<li class="">' + ' ' + card.name + '</li>');
        });
        console.log(http);
    });
})(jQuery);

(function(React){
    var CardList = React.createClass({
        getInitialState: function() {
          return {data: []};
        },
        loadCardsFromServer: function(){
            var that = this;
            $.get('api/current_hand', function(http){
                that.setState({"data": http.cards});
            });
        },
        render: function() {
            var cardNodes = this.state.data.map(function (card) {
              return (
                <li>{card.name}</li>
              );
            });
            return (
              <ul className="card-list" data={this.state.data}>
                {cardNodes}
              </ul>
            );
        },
        componentDidMount: function() {
          this.loadCardsFromServer();
          setInterval(this.loadCardsFromServer, 2000);
        },
    });
    React.render(
        <CardList />,
        document.getElementById('content')
    );
})(React);
