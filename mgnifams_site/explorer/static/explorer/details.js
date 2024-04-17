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

const renderArchitecture = (jsonData) => {
    const max_shown_length = 30;
    const architecturesContainer = document.getElementById('architecturesContainer');

    const showTooltip = (event, text, max_shown_length) => {
        if (text.length > max_shown_length) {
            const tooltip = document.getElementById('tooltip');
            tooltip.textContent = text;
            tooltip.style.display = 'block';
            tooltip.style.left = event.pageX - window.innerWidth/5 + 'px';
            tooltip.style.top = event.pageY  + 'px';
        }
    };

    const hideTooltip = () => {
        const tooltip = document.getElementById('tooltip');
        tooltip.style.display = 'none';
    };
    
    // Loop through each architecture container
    jsonData.architecture_containers.slice(0, 10).forEach(container => {
        const containerDiv = document.createElement('div');
        containerDiv.classList.add('architecture-div');
        const architectureTextPara = document.createElement('span');
        architectureTextPara.textContent = `${container.architecture_text}`;
        architectureTextPara.classList.add('descr-span');
        containerDiv.appendChild(architectureTextPara);

        // Loop through each domain in the container
        container.domains.forEach(domain => {
            const domainSpan = document.createElement('span');
            const domainLink = document.createElement('a');
            domainLink.textContent = domain.name.length > max_shown_length ? domain.name.substring(0, (max_shown_length - 3)) + "..." : domain.name;
            domainLink.href = domain.link;
            domainLink.setAttribute('target', '_blank');
            domainLink.classList.add('domain-link');
            domainSpan.classList.add('domain-span');
            domainSpan.style.backgroundColor = domain.color;
            domainSpan.style.color = domain.font_color;
            domainSpan.appendChild(domainLink);
            domainSpan.addEventListener('mouseover', function(event) {
                showTooltip(event, domain.name, max_shown_length);
            });
            domainSpan.addEventListener('mouseout', hideTooltip);
            containerDiv.appendChild(domainSpan);
        });

        architecturesContainer.appendChild(containerDiv);
    });
};

const loadDomainData = () => {
    let domainDataURL = document.getElementById('domain-data').dataset.url;
    fetch(domainDataURL)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            renderArchitecture(data);
        })
        .catch(error => {
            console.error('Error fetching domain architecture JSON:', error);
        });
};

const loadDatatables = () => {
    if ($('#pfams-table:contains("No Pfam hits found")').length === 0) {
        $('#pfams-table').DataTable();
    }
    if ($('#structural-annotations-table:contains("No structural annotations found")').length === 0) {
        $('#structural-annotations-table').DataTable();
    }
};

$(document).ready(function () {

    loadFamilyData();
    loadBiomeData();
    loadMSAData();
    loadDomainData();
    loadDatatables();

})
