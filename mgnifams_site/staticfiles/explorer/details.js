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

const extract_hmm_column = (p_text) => {
    let parts = p_text.split(':');
    let numberPart = parts[parts.length - 1];
    let col = parseInt(numberPart);
    return col;
};

const translate_to_msa_pos = (sequence, hmm_position) => {
    let x_counter = 0;
    let msa_pos;
    for ( msa_pos = 0; msa_pos < sequence.length; msa_pos++) {
        if (sequence[msa_pos] === 'x') {
            x_counter = x_counter + 1;
            if (x_counter == hmm_position) break;
        }
    }
    return msa_pos;
};

const link_hmm_to_msa = () => {
    // need a dummy init p in the col_info div to tie the event
    const hiddenParagraph = document.createElement('p');
    hiddenParagraph.textContent = 'Hidden paragraph content';
    hiddenParagraph.style.display = 'none';
    const divElement = document.getElementById('col_info');
    divElement.appendChild(hiddenParagraph);
    // create the observer
    const observer = new MutationObserver(function(mutationsList, observer) {
        for(const mutation of mutationsList) {
            if (mutation.type === 'childList') {
                mutation.addedNodes.forEach(node => {
                    if (node.tagName === 'P') {
                        const divElement = document.getElementById('col_info');
                        const pElement = divElement.querySelector('p:first-of-type');
                        let clicked_col = extract_hmm_column(pElement.textContent);
                        let msa_pos = translate_to_msa_pos(rf, clicked_col);
                        let elements = document.getElementsByClassName('msa-col-header');
                        elements[msa_pos].click();
                    }
                });
            }
        }
    });
    // Configure and start observing for changes in child nodes
    const config = { childList: true, subtree: true };
    observer.observe(divElement, config);
};

const loadHMMData = () => {
    let hmmLogoJson = JSON.parse(hmm_logo_json);
    let logoDiv = document.getElementById('logo');
    logoDiv.setAttribute('data-logo', JSON.stringify(hmmLogoJson));
    $('#logo').hmm_logo({height_toggle: true, column_info: "#col_info"});
    // switch to maximum observed scale
    let radioInput = document.querySelector('input[name="scale"][value="obs"]');
    radioInput.click();
    // hide Coordinates fieldset options
    let logoSettingsDiv = document.querySelector('.logo_settings');
    let fieldsets = logoSettingsDiv.querySelectorAll('fieldset');
    fieldsets[2].style.display = 'none';

    // link event to msa
    link_hmm_to_msa();
};

const showTooltip = (event, text, max_shown_length) => {
    if (text.length > max_shown_length) {
        const domain_tooltip = document.getElementById('domain_tooltip');
        domain_tooltip.textContent = text;
        domain_tooltip.style.display = 'block';
        domain_tooltip.style.left = event.pageX - window.innerWidth/5 + 'px';
        domain_tooltip.style.top = event.pageY  + 'px';
    }
};

const hideTooltip = () => {
    const domain_tooltip = document.getElementById('domain_tooltip');
    domain_tooltip.style.display = 'none';
};

const renderArchitecture = (jsonData) => {
    const max_shown_length = 30;
    const architecturesContainer = document.getElementById('architecturesContainer');
    
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
    loadHMMData();
    loadDomainData();
    loadDatatables();

})
