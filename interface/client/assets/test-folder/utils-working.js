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
 export var vegaConfig = {
     axis: {labelFontSize:9, titleFontSize:9, labelAngle:-45, labelLimit:50},
     legend: {gradientLength:20, labelFontSize:6, titleFontSize:6, clipHeight:20}
 }

 export function createDataTable(scrollH) {
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
 }
 // function shuffleArray(array) {
 //   for (let i = array.length - 1; i > 0; i--) {
 //     const j = Math.floor(Math.random() * (i + 1));
 //     [array[i], array[j]] = [array[j], array[i]];
 //   }
 // }
 //

export function displayBookmarkCharts(container, created = true) {
    $(container).empty();

     app.sumview.bookmarkedCharts.forEach((ch) => {
        var vegachart = _.extend({}, ch.originalspec,
            {width: 470, height: 225, autosize: 'fit'},
            // { data: {values: app.data.chartdata.values} },
            {config: vegaConfig});
        var $chartContainer = $('<div />', {
            class: 'chartdiv',
            id: 'bookchart' + ch.overallchid
        });
        var $chartLabel = $('<span class="chartlabel"></span>').css('background-color', ch.created ? '#f1a340' : '#998ec3').html('#' + ch.overallchid);

        $(container).append($chartContainer);
        $chartContainer.append('<div class="chartcontainer"></div>', $chartLabel);

        vegaEmbed('#bookchart' + ch.overallchid + ' .chartcontainer', vegachart, {
            actions: false
        });

        $chartContainer.hover((e) => {
            $chartContainer.css('border-color', 'crimson');
            app.sumview.highlight(ch.overallchid, true, true);
        }, (e) => {
            $chartContainer.css('border-color', 'lightgray');
            app.sumview.highlight(ch.overallchid, false, true);
        }).click((e) => {
            app.sumview.bookmarkedselectedChartID = ch.overallchid;
        });
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
        var $chartLabel = $('<span class="chartlabel"></span>').css('background-color', ch.created ? '#f1a340' : '#998ec3').html('#' + ch.chid);

        $(container).append($chartContainer);
        $chartContainer.append('<div class="chartcontainer"></div>', $chartLabel);

        vegaEmbed('#chart' + ch.chid + ' .chartcontainer', vegachart, {
            actions: false
        });

        $chartContainer.hover((e) => {
            $chartContainer.css('border-color', 'crimson');
            app.sumview.highlight(ch.chid, true, false);
        }, (e) => {
            $chartContainer.css('border-color', 'lightgray');
            app.sumview.highlight(ch.chid, false, false);
        }).click((e) => {
            app.sumview.selectedChartID = ch.chid;
        });

        // Create and append bookmark button
        var $bookmarkButton = $('<button>', {
            class: 'bookmark-button',
            text: 'Bookmark'
        }).click(() => {

            console.log('Bookmarking chart ID:', ch.overallchid);
            app.sumview._bookmarkedCharts.push(ch);
            // // Handle bookmarking action here
            // if (app.sumview._bookmarkedCharts.length === 0) {
            //     console.log('Bookmarking chart ID:', ch.overallchid);
            //     app.sumview._bookmarkedCharts.push(ch);
            // }
            //
            // for (let i = 0; i < app.sumview._bookmarkedCharts.length; i++) {
            //     if (app.sumview._bookmarkedCharts[i].overallchid === ch.overallchid) {
            //         console.log('Chart already bookmarked');
            //     }
            //     else {
            //         console.log('Bookmarking chart ID:', ch.overallchid);
            //         app.sumview._bookmarkedCharts.push(ch);
            //     }
            // }
        });
        $chartContainer.append($bookmarkButton);
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
         if(logging) app.logger.push({time:Date.now(), action:'recommendchart'})

     })

     app.chartview.on('similar', (spec) => {
         if(logging) app.logger.push({time:Date.now(), action:'recommendchart', data:spec})

         if(app.sumview.data.chartspecs.length > 0)
            spec._meta = {chid: app.sumview.data.chartspecs[app.sumview.data.chartspecs.length - 1]._meta.chid + 1, uid: 0}
        else
            spec._meta = {chid:0, uid:0}
        app.sumview.data.chartspecs.push(spec) //this holds all the charts that make it to the CenterView



        //displayAllCharts('#allchartsview', false)
        $('#suggestionview').empty()
        //displayAllCharts('#suggestionview', false)


      // Parse JSON string into a JavaScript object
         const visualizationConfig = spec.encoding;

         const shapeField = visualizationConfig.shape?.field !== undefined ? visualizationConfig.shape.field : null;
         const sizeField = visualizationConfig.size?.field !== undefined ? visualizationConfig.size.field : null;
         const xField = visualizationConfig.x?.field !== undefined ? visualizationConfig.x.field : null;
         const yField = visualizationConfig.y?.field !== undefined ? visualizationConfig.y.field : null;
         const colorField = visualizationConfig.color?.field !== undefined ? visualizationConfig.color.field : null;
        // Check if colorField, xField, and yField exist
        // Remove null or undefined values from fieldsArray
        fieldsArray = [colorField, xField, yField, shapeField,sizeField].filter(field => field !== null && field !== undefined);
        attributesHistory.push(fieldsArray);



        // Log extracted fields array
         console.log("Fields array:", fieldsArray);
         app.sumview.update(() => {app.sumview.selectedChartID = spec._meta.chid }, attributesHistory)
         //app.sumview.update(()=> {app.sumview.selectedChartID = spec._meta.chid }, fieldsArray)

         //$('#suggestionview').empty()
         displayAllCharts('#suggestionview', true)

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

    //  app.chartview.on('remove-chart', (spec) => {
    //      app.sumview.data.chartspecs = app.sumview.data.chartspecs.filter((d) => { return d._meta.chid != app.sumview.selectedChartID })
    //      app.sumview.update()
    //      displayAllCharts('#allchartsview', false)
    //      $('#suggestionview').empty()

    //      if(logging) app.logger.push({time:Date.now(), action:'removechart', data:spec})
    //  })

     $('#import').click(() => {
         $('#dialog').css('display', 'block')
     })

     $('.close').click(() => {
         $('#dialog').css('display', 'none')
     })


     // If the user has clicked on the previous charts from the past users then
     // we are getting the state of the clicked chart
     $('#allchartsview').click(() => {
         console.log("A chart has been clicked in Chart View")
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
         $.ajax({
             type: 'POST',
             crossDomain: true,
             url: 'http://localhost:5500/encode2',
             data: JSON.stringify(specs),
             contentType: 'application/json'
         }).done((data) => {
            //  console.log(data)
         })
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

    $('#export').click(() => {
         download(JSON.stringify({
                 charts: app.sumview.data.chartspecs,
                 attributes: app.sumview.data.chartdata.attributes,
                 data: app.sumview.data.chartdata.values
             }, null, '  '), 'datacharts.json', 'text/json')
         if(logging) download(JSON.stringify(app.logger, null, '  '), 'logs.json', 'text/json')

        // Redirect to the post-task-survey.html page with the correct port number
        window.location.href = `${window.location.href}post-task-survey.html`; // Change 8000 to your actual port number
        restartProcess()
     })

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

     // events handling
     handleEvents()
 }

 function download(content, fileName, contentType) {
     var a = document.createElement("a");
     var file = new Blob([content], {type: contentType});
     a.href = URL.createObjectURL(file);
     a.download = fileName;
     a.click();
 }

 export default {vegaConfig, handleEvents, parseurl, createDataTable, displayAllCharts, updateData}

function storeInteractionLogs(interaction, value, time) {
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
        var data = full_data['distribution_response'];


        // Create baseline charts
        createBaselineChart("UserChart", data['distribution_map'], "Probability", "rgba(54, 160, 235, 0.2)", "rgba(42, 160, 235, 1)");
        createBaselineChart("RLChart", data['baselines_distribution_maps']['Greedy'], "Probability", "rgba(54, 160, 235, 0.2)", "rgba(42, 160, 235, 1)");
        createBaselineChart("RandombaselineChart", data['baselines_distribution_maps']['Random'], "Probability", "rgba(255, 99, 132, 0.2)", "rgba(255, 99, 132, 1)");
        createBaselineChart("MomentumbaselineChart", data['baselines_distribution_maps']['Momentum'], "Probability", "rgba(220, 90, 132, 0.2)", "rgba(220, 90, 132, 1)");
        // createAccuracyChart('accuracyChart', full_data, updateTimeSeriesChart);
        createShiftFocusChart(full_data);
        document.getElementById("myNav").style.width = "100%";
    }).fail((xhr, status, error) => {
        alert('Cannot Derive Performance View. Please Try Again Later');
    });
}

// function createAccuracyChart(id,data) {
//     var accuracyData = data;
//
//     var time = accuracyData['RL'].length;
//
//
//
//
// if (time < 1) {
//     alert('Not Enough Data to Derive Hit Rate View. Rendering Other Views');
//     return;
// }
//     var timeLabels = Array.from({ length: time }, (_, i) => i.toString());
//
//     var datasets = Object.keys(accuracyData).map(key => {
//         return {
//             label: key,
//             data: accuracyData[key],
//             fill: false,
//             borderColor: key === "RL" ? "blue" : key === "Random" ? "green" : "red"
//         };
//     });
//
//     var accuracyChart = new Chart(id, {
//         type: "line",
//         data: {
//             labels: timeLabels,
//             datasets: datasets
//         },
//         options: {
//             responsive: true,
//             title: {
//                 display: true,
//                 text: "Hit Rate Over Time"
//             },
//             scales: {
//                 xAxes: [{
//                     scaleLabel: {
//                         display: true,
//                         labelString: "Time"
//                     }
//                 }],
//                 yAxes: [{
//                     scaleLabel: {
//                         display: true,
//                         labelString: "Hit Rate"
//                     }
//                 }]
//             }
//         }
//     });
//      accuracyCharts[id] = accuracyChart;
// }

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



function openBookmark() {
    document.getElementById("myBookmark").style.width = "100%";
    displayBookmarkCharts('#bookmarkview', true)
    }
function closeBookmark() {
  document.getElementById("myBookmark").style.width = "0%";
}

// Function to parse CSV data into an array of arrays
function CSVToArray(text) {
  const rows = text.split('\n');
  return rows.map(row => row.split(','));
}


var hitRateHistory = {'RL': [], 'Random': [], 'Momentum': []  };


// Function to create or update accuracy chart
function createAccuracyChart(id, data, updateTimeSeriesChart, xsc) {

    hitRateHistory = data['accuracy_response'];

    // Determine the number of time points
    var time = hitRateHistory[Object.keys(hitRateHistory)[0]].length;
    var timeLabels = Array.from({ length: time }, (_, i) => i.toString());

    const margin = { top: 20, right: 50, bottom: 50, left: 190 };
    const width = Math.max(window.innerWidth * 0.8 - margin.left - margin.right, 300);
    const height = window.innerHeight * 0.6 - margin.top - margin.bottom;

    // Clear the existing SVG content
    d3.select(`#${id}`).selectAll("*").remove();

    var svg = d3.select(`#${id}`).append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    var xScale = d3.scaleBand()
        .domain(timeLabels)
        .range([0, width])
        .padding(0.1);

    var yScale = d3.scaleLinear()
        .domain([0, 1.1]) // Adjusted yScale domain
        .range([height, 0]);

    var colors = d3.scaleOrdinal()
        .domain(Object.keys(hitRateHistory))
        .range(d3.schemeCategory10);

    // Draw lines for each dataset
    Object.keys(hitRateHistory).forEach((algorithm, i) => {
        var line = d3.line()
            .x((_, i) => xScale(i.toString()) + xScale.bandwidth() / 2)
            .y(d => yScale(d))
            .curve(d3.curveCardinal.tension(0.5));

        svg.append("path")
            .datum(hitRateHistory[algorithm])
            .attr("fill", "none")
            .attr("stroke", colors(algorithm))
            .attr("stroke-width", 2)
            .attr("d", line)
            .on("click", function(_, i) {
                updateTimeSeriesChart(i,data,xsc);
            });

        // Add labels for different algorithms colors
        svg.append("text")
            .attr("x", width - 35)
            .attr("y", margin.top + 20 * i)
            .attr("fill", colors(algorithm))
            .text(algorithm);

    });

    // Add circles to represent data points
    Object.keys(hitRateHistory).forEach(algorithm => {
        hitRateHistory[algorithm].forEach((hitRate, i) => {
            svg.append("circle")
                .attr("cx", xScale(i.toString()) + xScale.bandwidth() / 2)
                .attr("cy", yScale(hitRate))
                .attr("r", 5)
                .attr("fill", colors(algorithm))
                .on("click", () => {
                    updateTimeSeriesChart(i,data,xsc);
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
        .attr("y", height + margin.bottom - 10)
        .attr("text-anchor", "middle")
        .style("font-size", "14px")
        .text("Recommendation Cycle");

    // Add y-axis label
    svg.append("text")
        .attr("transform", `translate(-35, ${height / 2}) rotate(-90)`)
        .attr("text-anchor", "middle")
        .style("font-size", "14px")
        .text("Hit Rate");

    // // Brush functionality
    // svg.append("g").call(d3.brushX()
    //     .extent([[0, 0], [width, height]])
    //     .on("end", brushChart));

    // function brushChart() {
    //     var selection = d3.event.selection;
    //     if (selection) {
    //         var selectedTimes = [];
    //         var startIndex = Math.round(selection[0] / (xScale.bandwidth() + xScale.step()));
    //         var endIndex = Math.round(selection[1] / (xScale.bandwidth() + xScale.step()));
    //         for (var i = startIndex; i <= endIndex; i++) {
    //             selectedTimes.push(i);
    //         }
    //         updateTimeSeriesChart(selectedTimes,data);
    //     }
    // }
}



function updateTimeSeriesChart(clickedTime, data, xScale) {
    const fieldNames = [
        'airport_name', 'aircraft_make_model', 'effect_amount_of_damage', 'flight_date',
        'aircraft_airline_operator', 'origin_state', 'when_phase_of_flight', 'wildlife_size',
        'wildlife_species', 'when_time_of_day', 'cost_other', 'cost_repair', 'cost_total_a',
        'speed_ias_in_knots'
    ];

    var localattributeHistory = attributesHistory;
    var mapping = data['recTimetoInteractionTime'];
    var rlPredictions = data['algorithm_predictions']['RL'][clickedTime + 2];

    // Remove previous highlighting
    d3.selectAll(".highlight").attr("fill", null).classed("highlight", false);

    // Get the corresponding time steps from the mapping
    var allTimeSteps = mapping[clickedTime + 2];

    if (allTimeSteps && allTimeSteps.length > 0) {
        // Iterate over the time steps to highlight the corresponding elements
        allTimeSteps.forEach(timeStep => {
            var userAttributes = localattributeHistory[timeStep];

            // Iterate over each RL prediction
            rlPredictions.forEach(rlPrediction => {
                // Check if the RL algorithm's prediction matches any user attribute
                if (userAttributes.includes(rlPrediction)) {
                    const fieldIndex = fieldNames.indexOf(rlPrediction);
                    if (fieldIndex !== -1) {
                        // Highlight the corresponding element in the time series chart
                        d3.selectAll(`#timeSeriesChart [data-index="${fieldIndex}"]`)
                            .filter(function() {
                                return +d3.select(this).attr("x") === xScale(timeStep);
                            })
                            .attr("fill", "orange")
                            .classed("highlight", true);
                    }
                }
            });
        });
    }
}




function createShiftFocusChart(full_data) {



    d3.select('#timeSeriesChart').selectAll('svg').remove()

    const localattributeHistory = attributesHistory;

    const fieldNames = ['airport_name', 'aircraft_make_model', 'effect_amount_of_damage', 'flight_date', 'aircraft_airline_operator', 'origin_state', 'when_phase_of_flight', 'wildlife_size', 'wildlife_species', 'when_time_of_day', 'cost_other', 'cost_repair', 'cost_total_a', 'speed_ias_in_knots'];

    const timeSeriesData = localattributeHistory.map((attributes, index) => {
        const dataPoint = { time: index};
        fieldNames.forEach((field, fieldIndex) => {
            dataPoint[field] = attributes.includes(field) ? fieldIndex : null;
        });
        return dataPoint;
    });

    // console.log(timeSeriesData)

    const margin = { top: 20, right: 50, bottom: 50, left: 190 };
    const width = Math.max(window.innerWidth * 0.8 - margin.left - margin.right, 300);
    const height = window.innerHeight * 0.6 - margin.top - margin.bottom;
    const svg = d3.select("#timeSeriesChart").append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);


    //create another grouping axis with the prediction time
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
                        // .style("fill", "rgba(54, 160, 235, 0.4)"); // Adjust alpha value for a slightly darker shade

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
        .attr("transform", "rotate(-90)")
        .attr("y", 0 - margin.left)
        .attr("x", 0 - (height / 2))
        .attr("dy", "1em")
        .style("text-anchor", "middle")
        .text("Attribute");

    svg.append("text")
        .attr("transform", `translate(${width / 2},${height + margin.top + 10})`)
        .style("text-anchor", "middle")
        .text("Interactions Observed");
    createAccuracyChart('accuracyChart', full_data, updateTimeSeriesChart, xScale);

}

// /// ################# Shift Focus Chart ####################
// function createShiftFocusChart() {
//     // Remove existing SVG element
//     d3.select('#timeSeriesChart').selectAll('svg').remove();
//
//     const localattributeHistory = attributesHistory;
//
//     const fieldNames = ['airport_name', 'aircraft_make_model', 'effect_amount_of_damage', 'flight_date', 'aircraft_airline_operator', 'origin_state', 'when_phase_of_flight', 'wildlife_size', 'wildlife_species', 'when_time_of_day', 'cost_other', 'cost_repair', 'cost_total_a', 'speed_ias_in_knots'];
//
//     const timeSeriesData = localattributeHistory.map((attributes, index) => {
//             const dataPoint = { time: index };
//             fieldNames.forEach((field, fieldIndex) => {
//                 dataPoint[field] = attributes.includes(field) ? fieldIndex : null;
//             });
//             return dataPoint;
//         });
//
//     const margin = { top: 20, right: 50, bottom: 50, left: 190 }; // Adjusted left margin
//     const width = Math.max(window.innerWidth * 0.8 - margin.left - margin.right, 300); // Minimum width
//     const height = window.innerHeight * 0.6 - margin.top - margin.bottom;
//
//     const svg = d3.select("#timeSeriesChart").append("svg")
//         .attr("width", width + margin.left + margin.right)
//         .attr("height", height + margin.top + margin.bottom)
//         .append("g")
//         .attr("transform", `translate(${margin.left},${margin.top})`);
//
//     const x = d3.scaleBand() // Changed to scaleBand
//         .domain(timeSeriesData.map(d => d.time))
//         .range([0, width])
//         .padding(0.1); // Adjusted padding between bars
//
//     const y = d3.scaleBand()
//         .domain(fieldNames)
//         .range([height, 0])
//         .padding(0.1); // Adjusted padding between bars
//
//     svg.selectAll(".line")
//         .data(timeSeriesData)
//         .enter().append("g")
//         .each(function (d) {
//             const group = d3.select(this);
//             fieldNames.forEach(field => {
//                 if (d[field] !== null) {
//                     group.append("rect")
//                         .attr("x", x(d.time))
//                         .attr("y", y(field))
//                         .attr("width", x.bandwidth()) // Adjusted width of bars
//                         .attr("height", y.bandwidth())
//                         .attr("class", "bar")
//                         .attr("data-index", d[field]); // Set data-index attribute
//                 }
//             });
//         })
//         .on("mouseover", function() {
//             d3.select(this).attr("fill", "grey"); // Change color on hover
//         })
//         .on("mouseout", function() {
//             const fieldIndex = this.getAttribute("data-index"); // Access data-index attribute
//             const field = fieldNames[fieldIndex];
//             d3.select(this).attr("fill", colors(field)); // Restore original color
//         });
//
//     svg.append("g")
//         .attr("transform", `translate(0,${height})`)
//         .call(d3.axisBottom(x).ticks(timeSeriesData.length - 1).tickFormat(d3.format("d"))); // Adjusted tick format
//
//     svg.append("g")
//         .call(d3.axisLeft(y))
//         .selectAll("text")
//         .style("font-size", "14px") // Increase font size
//         .style("font-weight", "bold"); // Make text bold
//
//     svg.append("text")
//         .attr("transform", "rotate(-90)")
//         .attr("y", 0 - margin.left)
//         .attr("x", 0 - (height / 2))
//         .attr("dy", "1em")
//         .style("text-anchor", "middle")
//         .text("Attribute");
//
//     svg.append("text")
//         .attr("transform", `translate(${width / 2},${height + margin.top + 10})`)
//         .style("text-anchor", "middle")
//         .text("Interactions Observed");
// }

// ################# Shift Focus Chart ####################

//###################################################### Performance View ########################################################

    // var all_algorithms_predictions = data['algorithm_predictions'];
    // var users_predictions = data['user_selections'];
    //
    // d3.select(`#${id}`).selectAll('svg').remove()
    //
    // // Initialize hit rates and history object to store accuracies over time
    // var hitRates = {};
    //
    // // Initialize hit rates for each algorithm and create an empty history array
    // Object.keys(all_algorithms_predictions).forEach(algorithm => {
    //     hitRates[algorithm] = { correct: 0, total: 0 };
    // });
    //
    // // Calculate hit rates using current data
    // users_predictions.forEach(user_prediction => {
    //     Object.keys(all_algorithms_predictions).forEach(algorithm => {
    //         var predicted_attribute = all_algorithms_predictions[algorithm];
    //
    //         // Count total predictions for the algorithm
    //         hitRates[algorithm].total++;
    //
    //         // Check if the prediction is correct (exists in user predictions)
    //         if (user_prediction.includes(predicted_attribute)) {
    //             hitRates[algorithm].correct++;
    //         }
    //     });
    // });
    //
    // // Convert counts to hit rates (accuracy) and update history
    // Object.keys(hitRates).forEach(algorithm => {
    //     var correct = hitRates[algorithm].correct;
    //     var total = hitRates[algorithm].total;
    //     var accuracy = total > 0 ? correct / total : 0;
    //
    //     // Store the current accuracy in history
    //     hitRateHistory[algorithm].push(accuracy);
    // });
