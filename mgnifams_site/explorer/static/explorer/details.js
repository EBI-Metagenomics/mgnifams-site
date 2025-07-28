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

const loadStructureScoreColor = () => {
    const plddt = parseFloat(document.querySelector('.plddtColor').textContent.trim());

    const getPlddtColors = (plddt) => {
        if (plddt >= 90) {
            return { backgroundColor: 'rgb(0, 83, 214)', color: 'white' }; // Very high confidence (blue)
        } else if (plddt >= 70) {
            return { backgroundColor: 'rgb(101, 203, 243)', color: 'black' }; // High confidence (cyan)
        } else if (plddt >= 50) {
            return { backgroundColor: 'rgb(255, 219, 19)', color: 'black' }; // Low confidence (yellow)
        } else {
            return { backgroundColor: 'rgb(255, 125, 69)', color: 'black' }; // Very low confidence (orange)
        }
    };

    const plddtElement = document.querySelector('.plddtColor');
    const colors = getPlddtColors(plddt);
    plddtElement.style.backgroundColor = colors.backgroundColor;
    plddtElement.style.color = colors.color;
};

const renderFeatures = (jsonData) => {
    if (!jsonData || !jsonData.sequence || !Array.isArray(jsonData.features)) {
        console.error('Invalid data structure for Feature Viewer:', jsonData);
        return;
    }

    const ft = new FeatureViewer.createFeature(jsonData.sequence,
        '#featuresContainer',
        {
            showAxis: true,
            showSequence: true,
            toolbar: true
        });

    jsonData.features.forEach(feature => {
        if (feature && feature.type && Array.isArray(feature.data)) {
            try {
                ft.addFeature(feature);
            } catch (error) {
                console.error('Error adding feature:', feature, error);
            }
        } else {
            console.warn('Invalid feature object:', feature);
        }
    });
};

const loadSecondaryStructureData = () => {
    let featureDataURL = document.getElementById('feature-data').dataset.url;
    fetch(featureDataURL)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            renderFeatures(data);
        })
        .catch(error => {
            console.error('Error fetching features JSON:', error);
        });
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
    jsonData.architecture_containers.slice(0, 15).forEach(container => {
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

            if (domain.name.includes("MGnifam")) {
                domainLink.style.fontWeight    = 'bold';
                domainSpan.style.paddingLeft   = '15px';
                domainSpan.style.paddingRight  = '15px';
                domainSpan.style.paddingTop    = '6px';
                domainSpan.style.paddingBottom = '6px';
            }

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
        $('#pfams-table').DataTable({ordering: false});
    }
    if ($('#structural-annotations-table:contains("No structural annotations found")').length === 0) {
        $('#structural-annotations-table').DataTable({ordering: false});
    }
};

const downloadProteins = (mgyf, family_members) => {
    // Create file content
    const fileContent = family_members.join("\n");
    const blob = new Blob([fileContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);

    // Create a temporary link element
    const a = document.createElement('a');
    a.href = url;
    a.download = mgyf + '_mgyps.txt';
    document.body.appendChild(a);
    a.click();

    // Cleanup
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
};

$(document).ready(function () {
    loadBiomeData();
    loadStructureScoreColor();
    loadSecondaryStructureData();
    loadMSAData();
    // loadHMMData(); // TODO update
    loadDomainData();
    loadDatatables();

})
