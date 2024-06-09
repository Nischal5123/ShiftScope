/*************************************************************************
 * Copyright (c) 2018 Jian Zhao
 *
 *************************************************************************
 *
 * @author
 * Jian Zhao <zhao@fxpal.com>
 *
 *************************************************************************/

 // external libs'
 import vegaEmbed from 'vega-embed'
 import SumView from './sumview.js'
 import ChartView from './chartview.js'

 var logging = true
 var interactionLogs = [];
 var fieldsArray = [];
 var attributesHistory = [];
 var bookmarkedCharts = [];
 var user_session_id = 'user1';
 export var vegaConfig = {
     axis: {labelFontSize:9, titleFontSize:9, labelAngle:-45, labelLimit:50},
     legend: {gradientLength:20, labelFontSize:6, titleFontSize:6, clipHeight:20}
 }



 export function createDataTable() {
    var columns = _.keys(app.data.chartdata.values[0]).map((d) => {return {title: d} })
    var tabledata = app.data.chartdata.values.map((d) => {
        var record = []
        for(var i = 0; i < columns.length; i++)
            record.push(d[columns[i].title])
        return record
    })

    if(app.datatable) {
        app.datatable.destroy()
        $('#dataview table').empty()
    }

    // Calculate dynamic scroll height as a percentage of the viewport height
    var scrollH = `${window.innerHeight * 0.2}px`; // Example: 50% of the viewport height

    app.datatable = $('#dataview table').DataTable({
        columnDefs: [
            {
                targets: '_all',
                render: function(data, type, row, meta) {
                    return '<span style="color:'
                        + app.sumview._varclr(columns[meta.col].title) + '">' + data + '</span>'
                }
            }
        ],
        data: tabledata,
        columns: columns,
        scrollY: scrollH,
        scrollX: true,
        paging: false,
        scrollCollapse: true,
        searching: false,
        info: false
    })

    columns.forEach((c) => {
        $('#legend').append('/<span class="legend-item" style="color:' + app.sumview._varclr(c.title) + '">' + c.title + '</span>')
    })

    // call backend to start session
    $.ajax({
        type: 'GET',
        crossDomain: true,
        url: 'http://localhost:5500/',
        contentType: 'application/json'
    }).done((data) => {
        user_session_id = data['session_id'];
        //log session id
        console.log("Session ID: ", user_session_id);
        storeInteractionLogs('study begins', user_session_id, new Date())
    }).fail((xhr, status, error) => {
        alert('Cannot start session.');
    });
}


export function displayBookmarkCharts(container, created = true) {
    $(container).empty();

      if (app.sumview.bookmarkedCharts.length === 0) {
        // Append a message indicating that there are no charts to display
        $(container).append('<h2> No Bookmarked Charts </h2>');
        return;
    }

     app.sumview.bookmarkedCharts.forEach((ch) => {
        var vegachart = _.extend({}, ch.originalspec,
            {width: 470, height: 225, autosize: 'fit'},
            // { data: {values: app.data.chartdata.values} },
            {config: vegaConfig});
        var $chartContainer = $('<div />', {
            class: 'chartdiv',
            id: 'bookchart' + ch.overallchid
        });

        $(container).append($chartContainer);
        $chartContainer.append('<div class="chartcontainer"></div>');

        vegaEmbed('#bookchart' + ch.overallchid + ' .chartcontainer', vegachart, {
            actions: false
        });

        $chartContainer.hover((e) => {
            $chartContainer.css('border-color', 'crimson');
            app.sumview.highlight(ch.overallchid, true, true);
            if(logging) app.logger.push({time:Date.now(), action:'hoverbookmarkedchart', data:ch})
            storeInteractionLogs('hover over bookmarked chart', {encoding:ch.originalspec.encoding, mark:ch.originalspec.mark}, new Date())
        }, (e) => {
            $chartContainer.css('border-color', 'lightgray');
            app.sumview.highlight(ch.overallchid, false, true);
        }).click((e) => {
            app.sumview.bookmarkedselectedChartID = ch.overallchid;
            if(logging) app.logger.push({time:Date.now(), action:'clickbookmarkedchart', data:ch})
            storeInteractionLogs('clicked bookmarked charts', {encoding:ch.originalspec.encoding, mark:ch.originalspec.mark}, new Date())
        });
           // Create and append bookmark button
        var $removebookmarkButton = $('<button>', {
                class: 'fas fa-trash'
            }).click(() => {

            console.log('Removing bookmarked chart ID:', ch.overallchid);
            if(logging) app.logger.push({time:Date.now(), action:'removebookmarkedchart', data:ch})
            storeInteractionLogs('removed bookmarked charts', {encoding:ch.originalspec.encoding, mark:ch.originalspec.mark}, new Date())
            const index = app.sumview._bookmarkedCharts.indexOf(ch);
            if (index > -1) { // only splice array when item is found
              app.sumview._bookmarkedCharts.splice(index, 1); // 2nd parameter means remove one item only
            }
            displayBookmarkCharts('#bookmarkview', true)
        });
        $chartContainer.append($removebookmarkButton);

    });
}

 export function displayAllCharts(container, created = true) {
    $(container).empty();
    app.sumview.charts.forEach((ch) => {
        var vegachart = _.extend({}, ch.originalspec, {
            width: 470,
            height: 225,
            autosize: 'fit'
        }, {
            config: vegaConfig
        });
        var $chartContainer = $('<div />', {
            class: 'chartdiv',
            id: 'chart' + ch.chid
        });
        // var $chartLabel = $('<span class="chartlabel"></span>').css('background-color', ch.created ? '#f1a340' : '#998ec3').html('#' + ch.chid);

        $(container).append($chartContainer);
        $chartContainer.append('<div class="chartcontainer"></div>');

        vegaEmbed('#chart' + ch.chid + ' .chartcontainer', vegachart, {
            actions: false
        });

        $chartContainer.hover((e) => {
            $chartContainer.css('border-color', 'crimson');
            app.sumview.highlight(ch.chid, true, false);
            storeInteractionLogs('hover on suggested chart', {encoding:ch.originalspec.encoding, mark:ch.originalspec.mark}, new Date())

        }, (e) => {
            $chartContainer.css('border-color', 'lightgray');
            app.sumview.highlight(ch.chid, false, false);
        }).click((e) => {
            app.sumview.selectedChartID = ch.chid;

            storeInteractionLogs('clicked on suggested chart', {encoding:ch.originalspec.encoding, mark:ch.originalspec.mark}, new Date())
        });

         // Create and append bookmark button
            var $bookmarkButton = $('<button>', {
                class: 'fas fa-bookmark'
            }).click(() => {

                console.log('Bookmarking chart ID:', ch.overallchid);
                storeInteractionLogs('bookmarked suggested chart', {encoding:ch.originalspec.encoding, mark:ch.originalspec.mark}, new Date())
                app.sumview._bookmarkedCharts.push(ch);
            });
            $chartContainer.append($bookmarkButton);

    });

}


export function displayBaselineCharts(container, created = true) {
    $(container).empty();


     app.sumview.baselineCharts.forEach((ch) => {
        var vegachart = _.extend({}, ch.originalspec,
            {width: 470, height: 225, autosize: 'fit'},
            // { data: {values: app.data.chartdata.values} },
            {config: vegaConfig});
        var $chartContainer = $('<div />', {
            class: 'chartdiv',
            id: 'baseline' + ch.chid
        });

        $(container).append($chartContainer);
        $chartContainer.append('<div class="chartcontainer"></div>');

        vegaEmbed('#baseline' + ch.chid + ' .chartcontainer', vegachart, {
            actions: false
        });

    });

}


 export function handleEvents() {
     app.sumview.on('clickchart', (ch) => {
        //  console.log(ch.originalspec)
         app.chartview.update(ch.originalspec, 'outside')


         //logger


         // Parse JSON string into a JavaScript object
         var visualizationConfigClick = ch.originalspec.encoding;

        // Array to store extracted fields

         const shapeField = visualizationConfigClick.shape?.field !== undefined ? visualizationConfigClick.shape.field : null;
         const sizeField = visualizationConfigClick.size?.field !== undefined ? visualizationConfigClick.size.field : null;
         const xField = visualizationConfigClick.x?.field !== undefined ? visualizationConfigClick.x.field : null;
         const yField = visualizationConfigClick.y?.field !== undefined ? visualizationConfigClick.y.field : null;
         const colorField = visualizationConfigClick.color?.field !== undefined ? visualizationConfigClick.color.field : null;
        // Check if colorField, xField, and yField exist
        fieldsArray = [colorField, xField, yField, shapeField,sizeField].filter(field => field !== null && field !== undefined);
        attributesHistory.push(fieldsArray);

        // Log extracted fields array


         $('#chartview .chartlabel').css('background-color', ch.created ? '#f1a340' : '#998ec3')
         $('#chartview .chartlabel').html('#' + ch.chid)
         if(ch.created) {
             $('#update, #remove').attr('disabled', true)
         }
         else {
             $('#update, #remove').attr('disabled', false)
         }

         if(logging) app.logger.push({time:Date.now(), action:'clickchart', data:ch.originalspec})
     })
     .on('mouseoverchart', (ch) => {
         if(logging) app.logger.push({time:Date.now(), action:'mouseoverchart', data:ch})
         var vegachart = _.extend({}, ch.originalspec,
             { width: 390, height: 190, autosize: 'fit' },
             { data: {values: app.data.chartdata.values} },
             { config: vegaConfig})
         vegaEmbed('#tooltip .chartcontainer', vegachart, {actions: false})

         $('#tooltip .chartlabel').css('background-color', ch.created ? '#f1a340' : '#998ec3')
         $('#tooltip .chartlabel').html('#' + ch.chid)
     })
     .on('recommendchart', () => {
         displayAllCharts('#suggestionview', true)
         displayBaselineCharts('#suggestionview2', true)
         displayBookmarkCharts('#bookmarkview', true)
         if(logging) app.logger.push({time:Date.now(), action:'recommendchart'})

     })

       app.chartview.on('similar', (spec, fieldsArray = []) => {
        if (logging) app.logger.push({ time: Date.now(), action: 'recommendchart', data: spec });
        storeInteractionLogs('requested chart recommendation', { encoding: spec.encoding, mark: spec.mark }, new Date());

        if (app.sumview.data.chartspecs.length > 0) {
            spec._meta = { chid: app.sumview.data.chartspecs[app.sumview.data.chartspecs.length - 1]._meta.chid + 1, uid: 0 };
        } else {
            spec._meta = { chid: 0, uid: 0 };
        }
        app.sumview.data.chartspecs.push(spec); // This holds all the charts that make it to the CenterView

        $('#suggestionview').empty();

        //###################### This only comes if the call is made from Manual Chart editing ########################################################################
        if (fieldsArray.length > 0) {
            console.log("Fields array:", fieldsArray);
            attributesHistory.push(fieldsArray);
        }
        //#######################################################################################################################

        // Log extracted fields array
        //  console.log("Fields array:", fieldsArray);
         app.sumview.update(() => {app.sumview.selectedChartID = spec._meta.chid }, attributesHistory)
         //app.sumview.update(()=> {app.sumview.selectedChartID = spec._meta.chid }, fieldsArray)

         //$('#suggestionview').empty()
         displayAllCharts('#suggestionview', true)
         displayBookmarkCharts('#bookmarkview', true)

         if(logging) app.logger.push({time:Date.now(), action:'addchart', data:spec})
     })

     app.chartview.on('update-chart', (spec) => {
         spec._meta = app.sumview.data.chartspecs[app.sumview.selectedChartID]._meta
         app.sumview.data.chartspecs[app.sumview.selectedChartID] = spec




         app.sumview.update(() => {app.sumview.selectedChartID = spec._meta.chid })
         displayAllCharts('#allchartsview', false)
         $('#suggestionview').empty()

         if(logging) app.logger.push({time:Date.now(), action:'updatechart', data:spec})
     })


     $('#import').click(() => {
         $('#dialog').css('display', 'block')
     })

     $('.close').click(() => {
         $('#dialog').css('display', 'none')
     })



     $('#allchartsview').click(() => {
         console.log("A chart has been clicked in Chart View")
         if(logging) app.logger.push({time:Date.now(), action:'clickchart', data:app.chartview._cheditor.session.getValue()})
         var specs = app.chartview._cheditor.session.getValue()
         //geting the vegalite encoding of the clicked chart
         //sending it to encode2 in modelserver.py to get the one-hot vector (state)
         $.ajax({
             type: 'POST',
             crossDomain: true,
             url: 'http://localhost:5500/encode2',
             data: JSON.stringify(specs),
             contentType: 'application/json'
         }).done((data) => {
             console.log(data)
         })
     })

     // If the user has clicked on a recommended chart
     $('#suggestionview').click(() => {
         console.log("A chart has been clicked in Suggestion")
         var specs = app.chartview._cheditor.session.getValue()
         if(logging) app.logger.push({time:Date.now(), action:'clickchart-suggestionview', data:specs})
         storeInteractionLogs('clicked on suggested chart', {encoding:JSON.parse(specs).encoding, mark:JSON.parse(specs).mark}, new Date())
         $.ajax({
             type: 'POST',
             crossDomain: true,
             url: 'http://localhost:5500/encode2',
             data: JSON.stringify(specs),
             contentType: 'application/json'
         }).done((data) => {

         });
         // Emit the 'similar' event with the current data
        // app.chartview.emit('similar', JSON.parse(specs)); ################################ Just adding this will start recommendation without user clicking on the 'Recommend' button
     })





     $('#submit').click(() => {
         if($('#inputfile').val()) {
             var reader = new FileReader();
             reader.onload = function(e) {
                 var d = JSON.parse(reader.result);
                 updateData(d, $('#inputfile').val())
             };

             reader.readAsText(document.getElementById('inputfile').files[0]);
         }
         else if($('#inputurl').val()) {
             $.get($('#inputurl').val()).done((d) => {
                 updateData(d, $('#inputurl').val())
             })
         }

         $('.close').click()
         if(logging) app.logger.push({time:Date.now(), action:'submitdata'})
     })

     // ########################################################## SAVE INTERACTION DATA ########################################################
     // this is the End Session button
    $('#export').click(() => {
         let savepath='ShiftScopeLogs/'+user_session_id;
         let datacharts_name = savepath + '/datacharts.json';
            let interactionlogs_name = savepath + '/interactionlogs.json';

         download(JSON.stringify({
                 charts: app.sumview.data.chartspecs,
                 attributes: app.sumview.data.chartdata.attributes,
                 data: app.sumview.data.chartdata.values,
                 bookmarked_charts: app.sumview.bookmarkedCharts
             }, null, '  '), datacharts_name, 'text/json')
         if(logging) download(JSON.stringify(app.logger, null, '  '), interactionlogs_name, 'text/json')

        // Redirect to the post-task-survey.html page
        window.location.href = `${window.location.href}post-task-survey`;
     })

      function download(content, fileName, contentType) {
     //save to sepcific folder ShiftScopeLogs/session_id
     let savepath='ShiftScopeLogs/'+user_session_id;
     var a = document.createElement("a");
     var file = new Blob([content], {type: contentType});
     a.href = URL.createObjectURL(file);
     a.download = fileName;
     a.click();
 }

 // ########################################################## SAVE INTERACTION DATA ########################################################

     $('#performaceViewOpen').click(() => {
            console.log("User requested Performance View")

            openNav()


     })

     $('#performaceViewClose').click(() => {
            console.log("User requested Performance View to be closed")
            closeNav()
     })

     $('#bookmarkViewOpen').click(() => {
            console.log("User requested Bookmark View")
            openBookmark()

     })

     $('#bookmarkViewClose').click(() => {
            console.log("User requested Bookmark View to be closed")
            closeBookmark()
     })

     $('#baselineViewOpen').click(() => {
            console.log("User requested Baseline View")
         storeInteractionLogs('requested baseline charts', "", new Date())
            openBaseline()

     })

     $('#baselineViewClose').click(() => {
            storeInteractionLogs('closed baseline charts', "", new Date())
            closeBaseline()
     })




     $(window).resize(() => {
         app.sumview.svgsize = [$('#sumview').width(), $('#sumview').height()]
     })




 }

 export function parseurl() {
     var parameters = {}
     var urlquery = location.search.substring(1)
     if(urlquery) {
         urlquery.split("&").forEach(function(part) {
             var item = part.split("=")
             parameters[item[0]] = decodeURIComponent(item[1])
             if(parameters[item[0]].indexOf(",") != -1)
                 parameters[item[0]] = parameters[item[0]].split(",")
         })
     }

     return parameters
 }

 export function updateData(data, name) {
     $("#datafile").html(name)

     app.data = {}
     app.data.chartdata = {attributes: data.attributes, values: data.data}
     app.data.chartspecs = data.charts

     app.sumview = new SumView(d3.select('#sumview'), app.data, {
         backend: 'http://127.0.0.1:5500',
         size: [$('#sumview').width(), $('#sumview').height()],
         margin: 10,
         chartclr: ['#f1a340', '#998ec3']
     })
     app.sumview.update()

     app.chartview = new ChartView({}, {
         attributes: app.data.chartdata.attributes,
         datavalues: app.data.chartdata.values,
         vegaconfig: vegaConfig
     })

     createDataTable(280)
     displayAllCharts('#allchartsview', true)
     displayAllCharts('#suggestionview', true)
     displayBaselineCharts('#suggestionview2', true)
     displayBookmarkCharts('#bookmarkview', true)

     // events handling
     handleEvents()
 }



 export default {vegaConfig, handleEvents, parseurl, createDataTable, displayAllCharts, updateData}

export function storeInteractionLogs(interaction, value, time) {
     console.log({ Interaction: interaction, Value: value, Time: time.getTime() });
  interactionLogs.push({
    Interaction: interaction,
    Value: value,
    Time: time.getTime(),
  });
}

//###################################################### Performance View ########################################################



// Declare global variables for charts
var baselineCharts = {};
var accuracyCharts = {};


function openNav() {
    $.ajax({
        type: 'GET',
        crossDomain: true,
        url: 'http://localhost:5500' + '/get-performance-data',
        contentType: 'application/json'
    }).done((full_data) => {
        storeInteractionLogs('Open Performance View', full_data, new Date())
        var data = full_data['distribution_response'];

        // // console.log(data)
        // // Create baseline charts
        // createBaselineChart("UserChart", data['distribution_map'], "Probability", "rgba(54, 160, 235, 0.2)", "rgba(42, 160, 235, 1)");
        // createBaselineChart("RLChart", data['baselines_distribution_maps']['RL'], "Probability", "rgba(54, 160, 235, 0.2)", "rgba(42, 160, 235, 1)");
        // createBaselineChart("HotspotbaselineChart", data['baselines_distribution_maps']['Hotspot'], "Probability", "rgba(255, 99, 132, 0.2)", "rgba(255, 99, 132, 1)");
        // createBaselineChart("MomentumbaselineChart", data['baselines_distribution_maps']['Momentum'], "Probability", "rgba(220, 90, 132, 0.2)", "rgba(220, 90, 132, 1)");
        // createAccuracyChart('accuracyChart', full_data, updateTimeSeriesChart);
        try {
            createShiftFocusChart(full_data);
        } catch (error) {
            console.warn('Failed to create accuracy chart:', error);
            alert('Not enough interactions to derive Performance View. Please try again later.');
        }
        document.getElementById("myNav").style.width = "100%";
    }).fail((xhr, status, error) => {
        alert('Cannot Derive Performance View. Please Try Again Later');
    });
}



function createBaselineChart(id, data, label, backgroundColor, borderColor) {
    var fieldNames = Object.keys(data);
    var probabilities = Object.values(data);


    var baselineChart = new Chart(id, {
        type: "bar",
        data: {
            labels: fieldNames,
            datasets: [{
                label: label,
                data: probabilities,
                backgroundColor: backgroundColor,
                borderColor: borderColor,
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                yAxes: [{
                    ticks: {
                        beginAtZero: true
                    }
                }]
            }
        }
    });

    baselineCharts[id] = baselineChart;
}



/* Close when someone clicks on the "x" symbol inside the overlay */
function closeNav() {
      // Loop through baselineCharts and destroy each chart
    Object.keys(baselineCharts).forEach(function(key) {
        baselineCharts[key].destroy();
    });
    // Loop through accuracyCharts and destroy each chart
    Object.keys(accuracyCharts).forEach(function(key) {
        accuracyCharts[key].destroy();
    });
    // Clear the chart objects
    baselineCharts = {};
    accuracyCharts = {};

  document.getElementById("myNav").style.width = "0%";
}

function openBaseline() {
      document.getElementById("mySidebar").style.width = "550px";
      displayBaselineCharts('#suggestionview2',true);
}

function closeBaseline() {
        document.getElementById("mySidebar").style.width = "0";
        storeInteractionLogs('Close Baseline View', "", new Date())

    }


function openBookmark() {
    document.getElementById("myBookmark").style.width = "550px";
    storeInteractionLogs('Open Bookmark View', "", new Date())

    displayBookmarkCharts('#bookmarkview', true)

    }
function closeBookmark() {
  document.getElementById("myBookmark").style.width = "0%";
   storeInteractionLogs('Close Task/Bookmark View', "", new Date())
}




// Function to parse CSV data into an array of arrays
function CSVToArray(text) {
  const rows = text.split('\n');
  return rows.map(row => row.split(','));
}

function createAccuracyChart(id, data, updateTimeSeriesChart, xsc, algorithm) {
    const fieldNames = [
        'airport_name', 'aircraft_make_model', 'effect_amount_of_damage', 'flight_date',
        'aircraft_airline_operator', 'origin_state', 'when_phase_of_flight', 'wildlife_size',
        'wildlife_species', 'when_time_of_day', 'cost_other', 'cost_repair', 'cost_total_a',
        'speed_ias_in_knots'
    ];

    // ########################################################## Variables ########################################################
    var algorithmPredictions = data['algorithm_predictions'];
    //only select Random, RL, and Momentum from the algorithm predictions
    const selectedAlgorithms = ['Hotspot','Modified-Hotspot', 'ShiftScope'];
    const selectedAlgorithmPredictions = {};
    selectedAlgorithms.forEach(algorithm => {
        selectedAlgorithmPredictions[algorithm] = algorithmPredictions[algorithm];
    });
    algorithmPredictions = selectedAlgorithmPredictions;
    const fullHistory = data['full_history'];
    const recTimetoInteractionTime = data['recTimetoInteractionTime'];
    // ########################################################## Variables ########################################################

    // Clear the existing SVG content
    d3.select(`#${id}`).selectAll("*").remove();

    const margin = { top: 0, right: 200, bottom: 60, left: 190 }; // increased right margin for legend
    const width = Math.max(window.innerWidth * 0.8 - margin.left - margin.right, 300);
    const height = window.innerHeight * 0.3 - margin.top - margin.bottom;

    const svg = d3.select(`#${id}`).append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    const xScale = d3.scaleBand()
        .domain(Object.keys(recTimetoInteractionTime)) // Use the length of predictions as the domain not the full history because # interactions can be larger than # predictions
        .range([0, width])
        .padding(0.1);

    const yScale = d3.scaleLinear()
        .domain([0, 1.1])
        .range([height, 0]);

    const colors = d3.scaleOrdinal()
        .domain(Object.keys(algorithmPredictions))
        .range(d3.schemeCategory10);

    // ########################################################## Calculating Accuracy ########################################################

    // Compute hit rates for each algorithm
    const hitRateHistory = {};
    Object.keys(algorithmPredictions).forEach(algorithm => {
        const predictions = algorithmPredictions[algorithm];
        const hitRates = [];
        Object.keys(recTimetoInteractionTime).forEach(time => {
            const timeSteps = recTimetoInteractionTime[time];

            let concatenatedHistory = [];
            // Same as concatenatedPredictions, full history step is also a list of interactions; flatten that too
            timeSteps.forEach(step => {
                if (!fullHistory[step]) {
                    console.log('No interactions for time:', time, 'step:', step);
                    return;
                }
                concatenatedHistory.push(...fullHistory[step].flat());
            });

            let concatenatedPredictions = [];
            // For each item in predictions[time], make one array of all predictions
            if (predictions[time] && predictions[time].length > 0) {
                predictions[time].forEach(predictionArray => {
                    concatenatedPredictions.push(...predictionArray);
                });
            }

            if (concatenatedHistory.length > 0) {
                let accuracy = computeAccuracy(concatenatedPredictions, concatenatedHistory);
                hitRates.push(accuracy);
            } else {
                console.log('No interactions for time:', time);
                hitRates.push(0);
            }
        });
        // // ########################################################## make hitRateHistory cumulative and between 0-1 ########################################################
        //  hitRates.forEach((hitRate, hr) => {
        //     if (hr > 0) {
        //         hitRates[hr] += hitRates[hr - 1];
        //     }
        //  });
        // hitRates.forEach((hitRate, hr) => {
        //     hitRates[hr] = hitRate / (hr + 1);
        // }   );
        hitRateHistory[algorithm] = hitRates;


    });



    // ########################################################## Plotting Accuracy Calculations ########################################################
    storeInteractionLogs('updated accuracy chart', hitRateHistory, new Date())
    // Draw lines for each dataset
    Object.keys(hitRateHistory).forEach((algorithm, i) => {
        const line = d3.line()
            .x((_, j) => xScale(j.toString()) + xScale.bandwidth() / 2)
            .y(d => yScale(d))
            .curve(d3.curveCardinal.tension(0.5));

        svg.append("path")
            .datum(hitRateHistory[algorithm])
            .attr("fill", "none")
            .attr("stroke", colors(algorithm))
            .attr("stroke-width", 2)
            .attr("d", line)
            .on("click", (_, j) => {
                updateTimeSeriesChart(j, data, xsc, algorithm, colors(algorithm));
            });
    });

    // Add circles to represent data points
    Object.keys(hitRateHistory).forEach((algorithm, j) => {
        hitRateHistory[algorithm].forEach((hitRate, i) => {
            svg.append("circle")
                .attr("cx", xScale(i.toString()) + xScale.bandwidth() / 2)
                .attr("cy", yScale(hitRate))
                .attr("r", 10)
                .attr("fill", colors(algorithm))
                .on("click", () => {
                    updateTimeSeriesChart(i, data, xsc, algorithm, colors(algorithm));
                });
        });
    });

    // Add x-axis
    svg.append("g")
        .attr("transform", `translate(0,${height})`)
        .call(d3.axisBottom(xScale));

    // Add y-axis
    svg.append("g")
        .call(d3.axisLeft(yScale).ticks(5));

    // Add x-axis label
    svg.append("text")
        .attr("x", width / 2)
        .attr("y", height + margin.bottom - 20)  // Adjusted position for more space
        .attr("text-anchor", "middle")
        .style("font-size", "20px")
        .text("Interactions");

    // Add y-axis label
    svg.append("text")
        .attr("transform", `translate(-35, ${height / 2}) rotate(-90)`)
        .attr("text-anchor", "middle")
        .style("font-size", "20px")
        .text(" Coverage");

    // Add a label box for different algorithms on the right
    const legend = svg.append("g")
        .attr("transform", `translate(${width + 30}, 0)`);  // add extra padding

    Object.keys(hitRateHistory).forEach((algorithm, i) => {
        const legendRow = legend.append("g")
            .attr("transform", `translate(0, ${i * 30})`);  // 30 pixels spacing between labels

        legendRow.append("rect")
            .attr("width", 20)
            .attr("height", 20)
            .attr("fill", colors(algorithm));

        const legendText = legendRow.append("text")
            .attr("x", 30)
            .attr("y", 15)
            .attr("text-anchor", "start")
            .style("font-size", "15px")
            .style("font-weight", "bold")
            .text(algorithm);

    });

}




 function updateTimeSeriesChart(clickedTime, data, xScale, algorithm, fillColor) {
    // console.log("Circle clicked:", clickedTime, algorithm);

    const fieldNames = ['airport_name', 'speed_ias_in_knots','aircraft_make_model', 'flight_date', 'aircraft_airline_operator', 'origin_state', 'effect_amount_of_damage', 'when_phase_of_flight', 'wildlife_size', 'wildlife_species', 'when_time_of_day', 'cost_other', 'cost_repair', 'cost_total_a'];


    var localattributeHistory = data['full_history'];
    var mapping = data['recTimetoInteractionTime'];
    var Predictions = data['algorithm_predictions'][algorithm][clickedTime];

    // Remove previous highlighting
    d3.selectAll(".highlight").attr("fill", "rgba(128, 128, 128, 0.6)").classed("highlight", false);

    // Get the corresponding time steps from the mapping
    var allTimeSteps = mapping[clickedTime];

    if (allTimeSteps && allTimeSteps.length > 0) {
        // Iterate over the time steps to highlight the corresponding elements
        allTimeSteps.forEach(timeStep => {
            var userAttributes = localattributeHistory[timeStep];

            Predictions.forEach(predictionArray => {
                predictionArray.forEach(prediction => {
                    if (userAttributes.includes(prediction)) {
                        const fieldIndex = fieldNames.indexOf(prediction);
                        if (fieldIndex !== -1) {
                            // Highlight the corresponding element in the time series chart
                            d3.selectAll(`#timeSeriesChart [data-index="${fieldIndex}"]`)
                                .filter(function () {
                                    return +d3.select(this).attr("x") === xScale(timeStep);
                                })
                                .attr("fill", fillColor)
                                .classed("highlight", true);
                        }
                    }
                });
            });
        });
    }
}



function createShiftFocusChart(full_data) {
    d3.select('#timeSeriesChart').selectAll('svg').remove();

    const localattributeHistory = full_data['full_history'];

    const fieldNames = ['airport_name', 'speed_ias_in_knots','aircraft_make_model', 'flight_date', 'aircraft_airline_operator', 'origin_state', 'effect_amount_of_damage', 'when_phase_of_flight', 'wildlife_size', 'wildlife_species', 'when_time_of_day', 'cost_other', 'cost_repair', 'cost_total_a'];

    const timeSeriesData = localattributeHistory.map((attributes, index) => {
        const dataPoint = { time: index };
        fieldNames.forEach((field, fieldIndex) => {
            dataPoint[field] = attributes.includes(field) ? fieldIndex : null;
        });
        return dataPoint;
    });

    const margin = { top: 0, right: 200, bottom: 50, left: 190 }; // Adjusted right margin for legend
    const width = Math.max(window.innerWidth * 0.8 - margin.left - margin.right, 300);
    const height = window.innerHeight * 0.6 - margin.top - margin.bottom;
    const svg = d3.select("#timeSeriesChart").append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    const xScale = d3.scaleBand()
        .domain(timeSeriesData.map(d => d.time))
        .range([0, width])
        .padding(0.1);

    const yScale = d3.scaleBand()
        .domain(fieldNames)
        .range([height, 0])
        .padding(0.1);

    svg.selectAll(".line")
        .data(timeSeriesData)
        .enter().append("g")
        .each(function (d) {
            const group = d3.select(this);
            fieldNames.forEach(field => {
                if (d[field] !== null) {
                    group.append("rect")
                        .attr("x", xScale(d.time))
                        .attr("y", yScale(field))
                        .attr("width", xScale.bandwidth())
                        .attr("height", yScale.bandwidth())
                        .attr("class", "bar")
                        .attr("data-index", d[field])
                        .attr("fill", "rgba(128, 128, 128, 0.6)"); // Grey color with adjusted alpha value
                }
            });
        });

    svg.append("g")
        .attr("transform", `translate(0,${height})`)
        .call(d3.axisBottom(xScale).ticks(timeSeriesData.length - 1).tickFormat(d3.format("d")));

    svg.append("g")
        .call(d3.axisLeft(yScale))
        .selectAll("text")
        .style("font-size", "14px")
        .style("font-weight", "bold");

    svg.append("text")
        .attr("transform", `translate(${width / 2},${height + margin.top + 22})`)
        .style("text-anchor", "middle")
        .text("Interactions")
        .style("font-weight", "bold");

    // Add a label for the grey color on the right side
    const legend = svg.append("g")
        .attr("transform", `translate(${width + 30}, 0)`);  // add extra padding

    const legendRow = legend.append("g")
        .attr("transform", `translate(0, 0)`);  // 30 pixels spacing between labels

    legendRow.append("rect")
        .attr("width", 20)
        .attr("height", 20)
        .attr("fill", "rgba(128, 128, 128, 0.6)"); // Grey color

    legendRow.append("text")
        .attr("x", 30)
        .attr("y", 15)
        .attr("text-anchor", "start")
        .style("font-size", "15px")
        .style("font-weight", "bold")
        .text("User Interactions");

    createAccuracyChart('accuracyChart', full_data, updateTimeSeriesChart, xScale);
}


// ###################################################### Helper Functions ########################################################

function computeAccuracy(predictions, groundTruth) {
    // Filter out placeholders like 'none' from ground truth and predictions
    const ground = [...new Set(groundTruth.filter(attribute => attribute !== 'none'))];
    const predict = [...new Set(predictions.filter(attribute => attribute !== 'none'))];

    // Initialize total matches
    let matches = 0;

    // Iterate through unique ground truth attributes
    ground.forEach(attr => {
        if (predict.includes(attr)) {
            matches++;
        }
    });

    // Calculate accuracy as the proportion of unique matches to the number of unique attributes in the ground truth
    const accuracy = matches / ground.length;

    return accuracy;
}


function computeCTR(predictions, groundTruth) {
    // Helper function to compare two arrays
    //fileter out 'none' from both predictions and groundTruth
    predictions = predictions.filter(attribute => attribute !== 'none');
    groundTruth = groundTruth.filter(attribute => attribute !== 'none');
    function arraysEqual(a, b) {
        const sortedA = [...a].sort();
        const sortedB = [...b].sort();
        for (let i = 0; i < sortedA.length; i++) {
            if (sortedA[i] !== sortedB[i]) return false;
        }
        return true;
    }

    // Check if groundTruth exists in predictions
    for (let i = 0; i < predictions.length; i++) {
        if (arraysEqual(predictions[i], groundTruth)) {
            return 1;
        }
    }
    return 0;
}



// ######################################### Task Description #########################################################################################

// Function to clear localStorage
function clearLocalStorage() {
  localStorage.clear();
}
// Attach event listener to window's beforeunload event
window.addEventListener('beforeunload', clearLocalStorage);


// Function to create task form
export function createTaskForm() {
  const taskview = document.getElementById('taskview');
  taskview.innerHTML = ''; // Clear any existing content

  const formTitle = document.createElement('h2');
  formTitle.classList.add('task-form-title');
  formTitle.innerText = 'Exploration Task';

  const questions = [
    "\n What birdstrikes should the FAA be most concerned about? \n \n"
  ];

  const form = document.createElement('form');
  form.id = 'taskForm';

  questions.forEach((question, index) => {
    const formGroup = document.createElement('div');
    formGroup.classList.add('form-group');

    const label = document.createElement('label');
    label.innerText = `${question}`;
    label.style.display = 'block';
    label.style.width = '100%';
    formGroup.appendChild(label);

    const input = document.createElement('textarea');
    input.name = `answer${index}`;
    input.classList.add('form-control');
    input.style.width = '90%';
    input.style.height = '250px'; // Increase the height of the input box
    input.style.overflowY = 'scroll'; // Make it scrollable if content exceeds height
    formGroup.appendChild(input);

    // Load saved value from local storage
    const savedValue = localStorage.getItem(`answer${index}`);
    if (savedValue) {
      input.value = savedValue;
    }

    input.addEventListener('input', function() {
      // Save value to local storage on input change
      storeInteractionLogs('Taking notes', input.value, new Date());
      console.log('task form input', input.value);
      localStorage.setItem(`answer${index}`, input.value);
    });

    form.appendChild(formGroup);
  });

  const submitButton = document.createElement('button');
  submitButton.type = 'button';
  submitButton.innerText = 'Submit';
  submitButton.classList.add('btn');
  submitButton.onclick = sendLogs;
  form.appendChild(submitButton);



  taskview.appendChild(formTitle);
  taskview.appendChild(form);

  // submit button click event
  submitButton.addEventListener('click', function() {
    storeInteractionLogs('Task Complete for User', {
      sessionid: user_session_id,
      algorithm: app.sumview._algorithm,
      baseline: app.sumview._baseline
    }, new Date());
    sendLogs();
  });
}


// ######################################### Send Logs to Backend #########################################################################################
function sendLogs() {
  const form = document.getElementById('taskForm');
  const formData = new FormData(form);
  const answers = {};

  formData.forEach((value, key) => {
    answers[key] = value;
  });

  const chartdata= {
                 allrecommendedcharts: app.sumview.allrecommendedCharts,
                 attributes_history: attributesHistory,
                 bookmarked_charts: app.sumview.bookmarkedCharts
             };
    const interactionlogs = interactionLogs;
    const finalData = {'chartdata': chartdata, 'interactionlogs': interactionlogs, 'taskanswers': answers};


  // call backend to store the answers
    $.ajax({
        type: 'POST',
        crossDomain: true,
        url: 'http://localhost:5500' + '/submit-form',
        data: JSON.stringify(finalData),
        contentType: 'application/json'
    }).done(() => {
        if(!alert('Note Stored! Safe to close')){window.location.reload();}
        // Restart the application using pm2
    // setTimeout(() => {
    //     process.exit(0); // Exit the application to allow pm2 to restart it
    // }, 1000); // Adding a delay to ensure the response is sent before restarting
    }).fail(() => {
        alert('Failed to store notes. Please try again later.');
    });
  console.log(answers);

}



