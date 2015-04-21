(function(React, $){
    var GameList = React.createClass({
        getInitialState: function() {
          return {data: []};
        },
        loadCardsFromServer: function(){
            var that = this;
            $.get('api/history', function(http){
                that.setState({"data": http.data});
            });
        },
        render: function() {
            var rows = this.state.data.map(function (data) {
                var heroSlug = data.hero.split(' ').join('-'),
                    oppSlug = data.opponent.split(' ').join('-'),
                    outcome = data.p1_won ? "W" : "L",
                    p2Outcome = data.p1_won ? "L" : "W";
              return (
                <tr>
                  <td>{data.player1}</td>
                  <td>{outcome}</td>
                  <td>{data.player2}</td>
                  <td>{p2Outcome}</td>
                  <td>{data.turns}</td>
                  <td><span className={heroSlug}>{data.hero}</span> 
                      <span>&nbsp; {data.player1}</span>
                      <span>&nbsp; {outcome}</span>
                      <span>&nbsp;vs&nbsp;</span> 
                      <span className={oppSlug}>{data.opponent}</span>
                      <span>&nbsp; {data.player2}</span>
                  </td>
                  <td></td>
                </tr>
              );
            });
            return (
              <div><h2>History ({this.state.data.length})</h2>
              <table className="history-table">
                <tr>
                  <td>Player1</td>
                  <td></td>
                  <td>Player2</td>
                  <td></td>
                  <td>Turns</td>
                  <td>Description</td>
                  <td></td>
                </tr>
                {rows}
              </table>
              </div>
            );
        },
        componentDidMount: function() {
          this.loadCardsFromServer();
          setInterval(this.loadCardsFromServer, 2000);
        },
    });
    React.render(
        <GameList />,
        document.getElementById('history')
    );
})(React, jQuery);
