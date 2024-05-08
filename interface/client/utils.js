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
        var vegachart = _.extend({}, ch.originalspec, {
            width: 470,
            height: 225,
            autosize: 'fit'
        }, {
            config: vegaConfig
        });
        var $chartContainer = $('<div />', {
            class: 'chartdiv',
            id: 'bookchart' + ch.chid
        });
        var $chartLabel = $('<span class="chartlabel"></span>').css('background-color', ch.created ? '#f1a340' : '#998ec3').html('#' + ch.chid);

        $(container).append($chartContainer);
        $chartContainer.append('<div class="chartcontainer"></div>', $chartLabel);

        vegaEmbed('#bookchart' + ch.chid + ' .chartcontainer', vegachart, {
            actions: false
        });

        $chartContainer.hover((e) => {
            $chartContainer.css('border-color', 'crimson');
            app.sumview.highlight(ch.chid, true);
        }, (e) => {
            $chartContainer.css('border-color', 'lightgray');
            app.sumview.highlight(ch.chid, false);
        }).click((e) => {
            app.sumview.bookmarkedselectedChartID = ch.chid;
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
            app.sumview.highlight(ch.chid, true);
        }, (e) => {
            $chartContainer.css('border-color', 'lightgray');
            app.sumview.highlight(ch.chid, false);
        }).click((e) => {
            app.sumview.selectedChartID = ch.chid;
        });

        // Create and append bookmark button
        var $bookmarkButton = $('<button>', {
            class: 'bookmark-button',
            text: 'Bookmark'
        }).click(() => {
            // Handle bookmarking action here
            // For example:
            app.sumview._bookmarkedCharts.push(ch);
            console.log('Bookmarking chart ID:', ch.chid);
        });
        $chartContainer.append($bookmarkButton);
    });
    // openNav()
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





         //

 
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

         // search through history and get spec?



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
         //remove last element from the attributesHistory array
         attributesHistory.pop()
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
 
     // #Sanad
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
     //Sanad
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
            document.getElementById("myNav").style.width = "100%";
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

let accuracyChart;
let baselineCharts = {};

function openNav() {
    $.ajax({
        type: 'GET',
        crossDomain: true,
        url: 'http://localhost:5500' + '/get-performance-data',
        contentType: 'application/json'
    }).done((data) => {
        // Create accuracy chart
        createAccuracyChart(data);

        // Create baseline charts
        createBaselineChart("UserChart", data['distribution_map'], "Probability", "rgba(54, 160, 235, 0.2)", "rgba(42, 160, 235, 1)");
        createBaselineChart("RLChart", data['baselines_distribution_maps']['Greedy'], "Probability", "rgba(54, 160, 235, 0.2)", "rgba(42, 160, 235, 1)");
        createBaselineChart("RandombaselineChart", data['baselines_distribution_maps']['Random'], "Probability", "rgba(255, 99, 132, 0.2)", "rgba(255, 99, 132, 1)");
        createBaselineChart("MomentumbaselineChart", data['baselines_distribution_maps']['Momentum'], "Probability", "rgba(220, 90, 132, 0.2)", "rgba(220, 90, 132, 1)");
    }).fail((xhr, status, error) => {
        alert('Not Enough Data to Derive Performace View.');
    });
}

function createAccuracyChart(data) {
    const accuracyData = {
        "RL": [0.1, 0, 0.4],
        "Random": [0.1, 0, 0.3],
        "Momentum": [0.2, 0.5, 0.7]
    };

    const time = accuracyData['RL'].length;
    const timeLabels = Array.from({ length: time }, (_, i) => i.toString());

    const datasets = Object.keys(accuracyData).map(key => {
        return {
            label: key,
            data: accuracyData[key],
            fill: false,
            borderColor: key === "RL" ? "blue" : key === "Random" ? "green" : "red"
        };
    });

    accuracyChart = new Chart("AccuracyChart", {
        type: "line",
        data: {
            labels: timeLabels,
            datasets: datasets
        },
        options: {
            responsive: true,
            title: {
                display: true,
                text: "Accuracy Over Time"
            },
            scales: {
                xAxes: [{
                    scaleLabel: {
                        display: true,
                        labelString: "Time"
                    }
                }],
                yAxes: [{
                    scaleLabel: {
                        display: true,
                        labelString: "Accuracy"
                    }
                }]
            }
        }
    });
}

function createBaselineChart(id, data, label, backgroundColor, borderColor) {
    const fieldNames = Object.keys(data);
    const probabilities = Object.values(data);

    const baselineChart = new Chart(id, {
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

// Function to parse CSV data into an array of arrays
function CSVToArray(text) {
  const rows = text.split('\n');
  return rows.map(row => row.split(','));
}


/* Close when someone clicks on the "x" symbol inside the overlay */
function closeNav() {
    $('#chart-container-perf').empty()
  document.getElementById("myNav").style.width = "0%";
}



function openBookmark() {
    document.getElementById("myBookmark").style.width = "100%";
    displayBookmarkCharts('#bookmarkview', true)
    }
function closeBookmark() {
  document.getElementById("myBookmark").style.width = "0%";
}

