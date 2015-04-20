
/**
* Handles all the functions for the graveyard
*/
(function(React, $){
    var GraveyardList = React.createClass({
        getInitialState: function() {
          return {data: []};
        },
        loadCardsFromServer: function(){
            var that = this;
            $.get('api/zone/FRIENDLY_GRAVEYARD/', function(http){
                that.setState({"data": http.entities});
            });
        },
        render: function() {
            var cardNodes = this.state.data.map(function (card) {
              var src = "card_images/banners/" + card.id + "_banner.png",
                  img = card.id !== "GAME_005" ?  (
                            <span className="banner-container">
                                <img className="banner-image" src={src}></img>
                            </span>
                        ) : (
                            <span className="banner-container">
                                <img className="banner-image"
                                    src="http://placehold.it/200x40/000000/000000/"></img>
                            </span>
                        );
              var cost = card.cost > 0 ? card.cost : "0";
              return (
                <li className="hand-item">{img}
                    <img src="ui_images/mana.png" className="mana-gem"></img>
                    <span className="banner-text">
                        {cost}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{card.name}
                    </span>
                </li>
              );
            });
            return (
              <ul id="" className="hand-list" data={this.state.data}>
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
        <GraveyardList />,
        document.getElementById('graveyard')
    );
})(React, jQuery);
