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

    // Match AlphaFold's published pLDDT confidence bands so the page uses familiar structure colors.
    const getPlddtColors = (plddt) => {
        if (plddt >= 90) {
            return { backgroundColor: 'rgb(0, 83, 214)', color: 'white' };
        } else if (plddt >= 70) {
            return { backgroundColor: 'rgb(101, 203, 243)', color: 'black' };
        } else if (plddt >= 50) {
            return { backgroundColor: 'rgb(255, 219, 19)', color: 'black' };
        } else {
            return { backgroundColor: 'rgb(255, 125, 69)', color: 'black' };
        }
    };

    const plddtElement = document.querySelector('.plddtColor');
    const colors = getPlddtColors(plddt);
    plddtElement.style.backgroundColor = colors.backgroundColor;
    plddtElement.style.color = colors.color;
};

const renderFeatures = (jsonData, container_id) => {
    if (!jsonData || !jsonData.sequence || !Array.isArray(jsonData.features)) {
        console.error('Invalid data structure for Feature Viewer:', jsonData);
        return;
    }

    const ft = new FeatureViewer.createFeature(jsonData.sequence,
        container_id,
        {
            showAxis: true,
            showSequence: true,
            brushActive: true,
            toolbar: true,
            zoomMax:50
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

const loadFeaturesData = (data_container_id, feature_container_id) => {
    let featureDataURL = document.getElementById(data_container_id).dataset.url;
    fetch(featureDataURL)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            renderFeatures(data, feature_container_id);
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
            scheme: "clustal2",
            colorBackground: true,
            showLowerCase: true,
            opacity: 0.6
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
    // RF dots at the ends are padding; internal dots still occupy MSA columns and must be counted.
    let trimmed_sequence = sequence.replace(/^\.+|\.+$/g, '');
    let x_counter = 0;
    let msa_pos;
    for ( msa_pos = 0; msa_pos < trimmed_sequence.length; msa_pos++) {
        if (trimmed_sequence[msa_pos] === 'x') {
            x_counter = x_counter + 1;
            if (x_counter == hmm_position) break;
        }
    }
    return x_counter == hmm_position ? msa_pos : -1;
};

const link_hmm_to_msa = () => {
    // The HMM logo plugin reports clicked columns by mutating #col_info, so observe that bridge element.
    const hiddenParagraph = document.createElement('p');
    hiddenParagraph.textContent = 'Hidden paragraph content';
    hiddenParagraph.style.display = 'none';
    const divElement = document.getElementById('col_info');
    divElement.appendChild(hiddenParagraph);
    const observer = new MutationObserver(function(mutationsList, observer) {
        for(const mutation of mutationsList) {
            if (mutation.type === 'childList') {
                mutation.addedNodes.forEach(node => {
                    if (node.tagName === 'P') {
                        const divElement = document.getElementById('col_info');
                        const pElement = divElement.querySelector('p:first-of-type');
                        let clicked_col = extract_hmm_column(pElement.textContent);
                        let msa_pos = translate_to_msa_pos(document.getElementById('logo').dataset.rf, clicked_col);
                        let elements = document.getElementsByClassName('msa-col-header');
                        if (msa_pos >= 0 && elements[msa_pos]) {
                            elements[msa_pos].click();
                        }
                    }
                });
            }
        }
    });
    const config = { childList: true, subtree: true };
    observer.observe(divElement, config);
};

const loadHMMData = () => {
    let hmmLogoJson = JSON.parse(document.getElementById('logo').dataset.hmmLogoJson);
    if (hmmLogoJson) {
        let logoDiv = document.getElementById('logo');
        logoDiv.setAttribute('data-logo', JSON.stringify(hmmLogoJson));
        $('#logo').hmm_logo({height_toggle: true, column_info: "#col_info"});
        // The observed scale shows the most informative logo height for sparse HMM columns.
        let radioInput = document.querySelector('input[name="scale"][value="obs"]');
        radioInput.click();
        // Coordinate controls expose plugin internals that do not map cleanly to the MSA viewer.
        let logoSettingsDiv = document.querySelector('.logo_settings');
        let fieldsets = logoSettingsDiv.querySelectorAll('fieldset');
        fieldsets[2].style.display = 'none';
        link_hmm_to_msa();
    } else {
        console.warn("No HMM logo JSON available (timed out or error)");
    }
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
    
    jsonData.architecture_containers.slice(0, 15).forEach(container => {
        const containerDiv = document.createElement('div');
        containerDiv.classList.add('architecture-div');
        const architectureTextPara = document.createElement('span');
        architectureTextPara.textContent = `${container.architecture_text}`;
        architectureTextPara.classList.add('descr-span');
        containerDiv.appendChild(architectureTextPara);
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

            // Highlight the query MGnifam inside each architecture so it is visible among Pfam domains.
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
    if ($('#funfams-table:contains("No FunFam hits found")').length === 0) {
        $('#funfams-table').DataTable({ order: [[2, 'desc']] });
    }
    if ($('#pfams-table:contains("No Pfam hits found")').length === 0) {
        $('#pfams-table').DataTable({ order: [[3, 'desc']] });
    }
    if ($('#pfams_model-table:contains("No MGnifam model Pfam hits found")').length === 0) {
        $('#pfams_model-table').DataTable({ order: [[3, 'desc']] });
    }
    if ($('#structural-annotations-table:contains("No structural matches found")').length === 0) {
        $('#structural-annotations-table').DataTable({ order: [[0, 'asc']] });
    }
};

const downloadProteins = (mgyf, family_members) => {
    const fileContent = family_members.join("\n");
    const blob = new Blob([fileContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = mgyf + '_mgyps.txt';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
};

const loadProteinSequenceContainer = () => {

    const proteinSequenceContainer = document.getElementById(
        'proteinSequenceContainer'
    );
    const positionMessage = document.getElementById('positionMessage');
    const proteinSequence = proteinSequenceContainer.textContent.trim();
    proteinSequenceContainer.innerHTML = '';

    /**
     * Render one span per residue so hover and region highlighting can target individual positions.
     */
    const displaySequence = (proteinSequence, proteinSequenceContainer) => {
        for (let i = 0; i < proteinSequence.length; i++) {
        const span = document.createElement('span');
        span.textContent = proteinSequence[i];
        proteinSequenceContainer.appendChild(span);
        }
    };

    /**
     * Read optional one-based residue coordinates from MGnify Proteins deep links.
     */
    const getStartAndEnd = () => {
        const urlParams = new URLSearchParams(window.location.search);
        const start = urlParams.get('start');
        const end = urlParams.get('end');
        return { start: start, end: end };
    };

    /**
     * Highlight inclusive, one-based residue coordinates in the zero-indexed span list.
     */
    const highlightRegion = (proteinSequenceContainer, start, end) => {
        for (let i = start; i <= end; i++) {
        const span = proteinSequenceContainer.children[i - 1];
        span.classList.add('highlight');
        }
    };

    const updatePositionMessage = (position) => {
        positionMessage.textContent = `Amino acid position: ${position}`;
    };
    const updateCursorStyle = (cursorStyle) => {
        proteinSequenceContainer.style.cursor = cursorStyle;
    };

    const handleMouseOver = (event) => {
        if (event.target.tagName === 'SPAN') {
        const position = Array.from(
            proteinSequenceContainer.querySelectorAll('span')
        ).indexOf(event.target);
        updatePositionMessage(position + 1);
        const targetElement = event.target;
        targetElement.style.backgroundColor = '#ffc4c4';
        }
    };

    proteinSequenceContainer.addEventListener('mouseover', (event) => {
        updateCursorStyle('pointer');
        handleMouseOver(event);
    });

    proteinSequenceContainer.addEventListener('mousemove', handleMouseOver);

    proteinSequenceContainer.addEventListener('mouseout', (event) => {
        updatePositionMessage(' -');
        updateCursorStyle('auto');
        if (event.target.tagName === 'SPAN') {
        event.target.style.backgroundColor = '';
        }
    });

    displaySequence(proteinSequence, proteinSequenceContainer);

    const { start, end } = getStartAndEnd();

    if (start !== null && end !== null) {
        highlightRegion(proteinSequenceContainer, start, end);
    }
}

$(document).ready(function () {
    loadBiomeData();
    loadStructureScoreColor();
    loadFeaturesData('feature-data', '#featuresContainer')
    if (document.getElementById('tm-data')) {
        loadFeaturesData('tm-data', '#tm_featuresContainer')
    }
    loadMSAData();
    loadHMMData();
    loadDomainData();
    loadDatatables();
    loadProteinSequenceContainer();
})
