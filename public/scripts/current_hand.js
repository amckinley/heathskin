/**
* Handles all the functions for the current hand page
*/
(function(React, $){
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
              <div><h2>Hand ({this.state.data.length})</h2>
              <ul id="" className="hand-list" data={this.state.data}>
                {cardNodes}
              </ul>
              </div>

            );
        },
        componentDidMount: function() {
          this.loadCardsFromServer();
          setInterval(this.loadCardsFromServer, 2000);
        },
    });
    React.render(
        <CardList />,
        document.getElementById('current-hand')
    );
})(React, jQuery);
