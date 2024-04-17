const translate_to_hmm_pos = (sequence, position) => {
    let hmm_pos = 0;

    for (let i = 0; i < sequence.length; i++) {
        if (sequence[i] === 'x') {
            hmm_pos = hmm_pos + 1;
            if (i >= position) break;
        }
    }

    return hmm_pos;
};

const loadFamilyData = () => {
    document.getElementById('show-members-btn').addEventListener('click', function() {
        let div = document.getElementById('family-members-div');
        div.style.display = div.style.display === 'none' ? 'block' : 'none';
        this.textContent = div.style.display === 'none' ? 'Show' : 'Hide';
    });
};

const loadBiomeData = () => {
    let biomesDataURL = document.getElementById('biomes-data').dataset.url;
    d3.csv(biomesDataURL, function(err, rows){
        function unpack(rows, key) {
            return rows.map(function(row) { return row[key]; });
        }

        let data = [
            {
                type: "sunburst",
                ids: unpack(rows, 'ids'),
                labels: unpack(rows, 'labels'),
                parents:unpack(rows, 'parents'),
                values:unpack(rows, 'counts')
            }
        ];

        let layout = {
            margin: {l: 0, r: 0, b: 0, t:0},
            extendsunburstcolorway: true
        };

        Plotly.newPlot('sunburst-div', data, layout, {showSendToCloud: true});
    })
};

const loadMSAData = () => {
    let rootDiv = document.getElementById("msa-div")
    let msaDataURL = document.getElementById('msa-data').dataset.url;
    let opts = {
        el: rootDiv,
            importURL: msaDataURL,
            menu: {
            menuFontsize: "14px",
            menuItemFontsize: "14px",
            menuItemLineHeight: "14px",
            menuMarginLeft: "3px",
            menuPadding: "3px 4px 3px 4px",
        },
        bootstrapMenu: true,
        vis: {
            seqlogo: false,
            conserv: false,
            overviewbox: false,
            gapHeader: false,
            labelId: true,
            labelName: true,
            labelPartition: false,
            labelCheckbox: false
        },
        colorscheme: {
            scheme: "clustal2", // name of your color scheme
            colorBackground: true, // otherwise only the text will be colored
            showLowerCase: true, // used to hide and show lowercase chars in the overviewbox
            opacity: 0.6 //opacity for the residues
        }
    };
    let m = new msa.msa(opts);
    m.render();
};

$(document).ready(function () {

    loadFamilyData();
    loadBiomeData();
    loadMSAData();
    
})
