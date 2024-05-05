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
 
 export function displayAllCharts(container, created=true) {
     $(container).empty()
     // shuffleArray(app.sumview.charts;
     app.sumview.charts.forEach((ch) => {
         // if(ch.created == created) {
         //    //  console.log(ch.originalspec)
            var vegachart = _.extend({}, ch.originalspec,
                { width: 470, height: 225, autosize: 'fit' },
            //  { data: {values: app.data.chartdata.values} },
                { config: vegaConfig})
            // console.log(vegachart)
            $(container).append($('<div />', {class: 'chartdiv', id: 'chart' + ch.chid}))
            $('#chart' + ch.chid).append('<div class="chartcontainer"></div><span class="chartlabel"></span>')
        
            vegaEmbed('#chart' + ch.chid + ' .chartcontainer', vegachart, {actions: false})
            $('#chart' + ch.chid + ' .chartlabel').css('background-color', ch.created ? '#f1a340' : '#998ec3')
            $('#chart' + ch.chid + ' .chartlabel').html('#' + ch.chid)
            
            $('#chart' + ch.chid).hover((e) => {
                $('#chart' + ch.chid).css('border-color', 'crimson')
                app.sumview.highlight(ch.chid, true)
            }, (e) => {
                $('#chart' + ch.chid).css('border-color', 'lightgray')
                app.sumview.highlight(ch.chid, false)
            }).click((e) => {
                app.sumview.selectedChartID = ch.chid
                })
         // }
     })
 }
 
 export function handleEvents() {
     app.sumview.on('clickchart', (ch) => {
        //  console.log(ch.originalspec)
         app.chartview.update(ch.originalspec, 'outside')
 
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

        // Array to store extracted fields


        //  const colorField = visualizationConfig.color.field !== undefined ? visualizationConfig.color.field : null;
        //  const xField = visualizationConfig.x.field !== undefined ? visualizationConfig.x.field : null;
        //  const yField = visualizationConfig.y.field !== undefined ? visualizationConfig.y.field : null;
        //
        // // Remove null or undefined values from fieldsArray
        //  fieldsArray = [colorField, xField, yField].filter(field => field !== null && field !== undefined);

         const shapeField = visualizationConfig.shape?.field !== undefined ? visualizationConfig.shape.field : null;
         const sizeField = visualizationConfig.size?.field !== undefined ? visualizationConfig.size.field : null;
         const xField = visualizationConfig.x?.field !== undefined ? visualizationConfig.x.field : null;
         const yField = visualizationConfig.y?.field !== undefined ? visualizationConfig.y.field : null;
         const colorField = visualizationConfig.color?.field !== undefined ? visualizationConfig.color.field : null;
        // Check if colorField, xField, and yField exist
         if (shapeField!=null && colorField !== null && xField !== null && yField !== null && sizeField !== null) {
            // Remove null or undefined values from fieldsArray
            fieldsArray=[colorField, xField, yField, shapeField,sizeField].filter(field => field !== null && field !== undefined);
         } else {
            // Handle case where colorField, xField, or yField is null
            console.error('Error: colorField, xField, or yField is null or undefined.');
         }
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
            openNav()

     })

     $('#performaceViewClose').click(() => {
            console.log("User requested Performance View to be closed")
            closeNav()
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

/* Open when someone clicks on the span element */
let myChart;
let baselineChart;// Declare a variable to store the chart instance

function openNav() {
    document.getElementById("myNav").style.width = "100%";

    $.ajax({
        type: 'GET',
        crossDomain: true,
        url: 'http://localhost:5500' + '/get-performance-data',
        contentType: 'application/json'
    }).done((data) => {


        // 1. Rl Data
        // Extract field names and probabilities from the data object
        const RLFieldNames = Object.keys(data['baselines_distribution_maps']['Greedy']);
        let RLProbabilities = Object.values(data['baselines_distribution_maps']['Greedy']);
        // Create a new Chart.js chart
        baselineChart = new Chart("RLChart", {
            type: "bar",
            data: {
                labels: RLFieldNames,
                datasets: [{
                    label: "Probability",
                    data: RLProbabilities,
                    backgroundColor: "rgba(54, 160, 235, 0.2)",
                    borderColor: "rgba(42, 160, 235, 1)",
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


        // data[0] contains the user data and data[1] contains the baseline data, we want 2 plots with titles
        // 1. User Data
        // Extract field names and probabilities from the data object

        const fieldNames = Object.keys(data['distribution_map']);
        let probabilities = Object.values(data['distribution_map']);
            // Create a new Chart.js chart
        myChart = new Chart("myChart", {
            type: "bar",
            data: {
                labels: fieldNames,
                datasets: [{
                    label: "Probability",
                    data: probabilities,
                    backgroundColor: "rgba(54, 162, 235, 0.2)",
                    borderColor: "rgba(54, 162, 235, 1)",
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

        // 2. Baseline Data
        // Extract field names and probabilities from the data object
        const baselineFieldNames = Object.keys(data['baselines_distribution_maps']['Random']);
        let baselineProbabilities = Object.values(data['baselines_distribution_maps']['Random']);
        // Create a new Chart.js chart
        baselineChart = new Chart("RandombaselineChart", {
            type: "bar",
            data: {
                labels: baselineFieldNames,
                datasets: [{
                    label: "Probability",
                    data: baselineProbabilities,
                    backgroundColor: "rgba(255, 99, 132, 0.2)",
                    borderColor: "rgba(255, 99, 132, 1)",
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



         // 3. Momentum Baseline Data
        // Extract field names and probabilities from the data object
        const MomentumbaselineFieldNames = Object.keys(data['baselines_distribution_maps']['Momentum']);
        let MomentumbaselineProbabilities = Object.values(data['baselines_distribution_maps']['Momentum']);
        // Create a new Chart.js chart
        baselineChart = new Chart("MomentumbaselineChart", {
            type: "bar",
            data: {
                labels: MomentumbaselineFieldNames,
                datasets: [{
                    label: "Probability",
                    data: MomentumbaselineProbabilities,
                    backgroundColor: "rgba(220, 90, 132, 0.2)",
                    borderColor: "rgba(220, 90, 132, 1)",
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

    }).fail((xhr, status, error) => {
        alert('Not Enough Data to Derive Performace View.');
    });
}

// Function to parse CSV data into an array of arrays
function CSVToArray(text) {
  const rows = text.split('\n');
  return rows.map(row => row.split(','));
}


/* Close when someone clicks on the "x" symbol inside the overlay */
function closeNav() {
  document.getElementById("myNav").style.width = "0%";
}



