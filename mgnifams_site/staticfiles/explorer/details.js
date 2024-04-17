$(document).ready(function () {

    // Family members
    document.getElementById('show-members-btn').addEventListener('click', function() {
        var div = document.getElementById('family-members-div');
        div.style.display = div.style.display === 'none' ? 'block' : 'none';
        this.textContent = div.style.display === 'none' ? 'Show' : 'Hide';
    });

    // Biomes distribution
    var biomesDataURL = document.getElementById('biomes-data').dataset.url;
    d3.csv(biomesDataURL, function(err, rows){
        function unpack(rows, key) {
            return rows.map(function(row) { return row[key]; });
        }

        var data = [
            {
                type: "sunburst",
                ids: unpack(rows, 'ids'),
                labels: unpack(rows, 'labels'),
                parents:unpack(rows, 'parents'),
                values:unpack(rows, 'counts')
            }
        ];

        var layout = {
            margin: {l: 0, r: 0, b: 0, t:0},
            extendsunburstcolorway: true
        };

        Plotly.newPlot('sunburst-div', data, layout, {showSendToCloud: true});
    })

})
