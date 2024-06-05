/*************************************************************************
 * Copyright (c) 2018 Jian Zhao
 *
 *************************************************************************
 *
 * @author
 * Jian Zhao <zhao@fxpal.com>
 *
 *************************************************************************/

 import { EventEmitter } from "events"

 import ace from 'ace-builds/src-noconflict/ace'
 import 'ace-builds/webpack-resolver'
 import vegaEmbed from 'vega-embed'
 import { storeInteractionLogs, createTaskForm } from "./utils.js"
 
 export default class ChartView extends EventEmitter {
     constructor(data, conf) {
         super()
 
         // global variable: window.app
         this.data = data
         this.conf = conf
 
         this._attributeTypeMap = {}
         this.conf.attributes.forEach((att) => {
                 this._attributeTypeMap[att[0]] = att[2]
         })
 
         this._init()
     }
 
     _init() {
        // text editor
         this._cheditor = ace.edit('editorcontainer', {
             mode: 'ace/mode/json',
             minLines: 20,
                maxLines: 35,
                wrap: true,
                autoScrollEditorIntoView: true,
                highlightActiveLine: true,
                showPrintMargin: true,
                showGutter: false,
         })

         createTaskForm();
         // ui controls
         var html = ''
 
         var comps = ['ch-x', 'ch-y', 'ch-color', 'ch-size', 'ch-shape']
         comps.forEach((comp) => {
             html = '<option value="-">-</option>'
             this.conf.attributes.forEach((d) => {
                  d[0] = d[0].toString().toLowerCase();
                 html += '<option value="' + d[0] + '">' + d[0] + '</option>'
             })
             $('#' + comp).append(html)
         })
     
         var marks = ['bar', 'point', 'circle', 'line', 'tick']
         html = ''
         marks.forEach((d) => {
             html += '<option value="' + d + '">' + d + '</option>'
         })
         $('#ch-mark').append(html)
         
         var comps = ['ch-xtrans', 'ch-ytrans', 'ch-colortrans', 'ch-sizetrans']
         var aggs = ['-', 'count', 'mean', 'sum', 'bin']
         comps.forEach((comp) => {
             html = ''
             aggs.forEach((d) => {
                 html += '<option value="' + d + '">' + d + '</option>'
             })
     
             $('#' + comp).append(html)
         })
 
         // buttons
         $('#add').click((e) => {
             this.update(this._cheditor.session.getValue(), 'texteditor')
             this.emit('similar', this.data)
         })
  
         $('#preview1').click((e) => {
             var data = _.cloneDeep(this.data)
             data['mark'] = $('#ch-mark').val()
 
             if(!data['encoding'])
                 data['encoding'] = {}
 
             var channels = ['x', 'y', 'color', 'size', 'shape']
             channels.forEach((channel) => {
                 if(!data['encoding'][channel])
                     data['encoding'][channel] = {}
 
                 if(channel != 'shape') {
                     var val = $('#ch-' + channel + 'trans').val()
                     if(val == 'bin')
                         data['encoding'][channel]['bin'] = true
                     else if(val != '-')
                         data['encoding'][channel]['aggregate'] = val
                     else {
                         delete data['encoding'][channel]['aggregate']
                         delete data['encoding'][channel]['bin']
                     }
                 }
 
                 var val = $('#ch-' + channel).val()
                 if(val != '-') {
                     data['encoding'][channel]['field'] = val
                     data['encoding'][channel]['type'] = this._attributeTypeMap[val]
                 }
                 else
                     delete data['encoding'][channel]
             })
            //  console.log(data)
              storeInteractionLogs('manually Edited Chart', {encoding:data['encoding'], mark:data['mark']}, new Date())
              this._validateChart(data, (recommended_chart_specs) => {
        this.update(recommended_chart_specs, 'uicontrols');


        /// ############################### Manually Edited Chart should also make to the history ##############################
         const visualizationConfig = this.data.encoding;

         const shapeField = visualizationConfig.shape?.field !== undefined ? visualizationConfig.shape.field : null;
         const sizeField = visualizationConfig.size?.field !== undefined ? visualizationConfig.size.field : null;
         const xField = visualizationConfig.x?.field !== undefined ? visualizationConfig.x.field : null;
         const yField = visualizationConfig.y?.field !== undefined ? visualizationConfig.y.field : null;
         const colorField = visualizationConfig.color?.field !== undefined ? visualizationConfig.color.field : null;
         const fieldsArray = [colorField, xField, yField, shapeField,sizeField].filter(field => field !== null && field !== undefined);


        //#######################################################################################################################

        // Automatically generate similar charts
        this.emit('similar', this.data, fieldsArray); // Automatically generate similar charts
    });


         })


 
         $('#preview2').click((e) => {
             var data = this._cheditor.session.getValue()

             this._validateChart(data, () => {this.update(data, 'texteditor')})            
         })
     
         $('#cancel1, #cancel2').click((e) => {
             if(app.sumview.selectedChartID >= 0) {
                 var ch = app.sumview.charts[app.sumview.selectedChartID]
                 this.update(ch.originalspec, 'outside')
             }
         })
     }
     
update(data_all, eventsource) {
    // Handle data parsing, string or object
    if (['outside'].includes(eventsource)) {
        this.data = data_all;
    } else {
        if (typeof data_all === 'object') {
            // Extract the first key from the object and update data_all
            data_all = [data_all[Object.keys(data_all)[0]]];
        } else if (typeof data_all === 'string') {
            // Convert string to an array containing the string itself
            data_all = [data_all];
        }

        var data = data_all[0];
        if (typeof data == 'string') {
            try {
                this.data = JSON.parse(data);
            } catch (err) {
                console.log(err, data);
                return;
            }
        } else if (typeof data == 'object') {
            this.data = data;
        }
    }
// Calculate the dimensions of chartview
    var chartViewElement = document.getElementById('chartview');
    var chartViewWidth = chartViewElement.clientWidth;
    var chartViewHeight = chartViewElement.clientHeight;

    var vegachart = _.extend({}, this.data, {
        width: chartViewWidth*0.95 ,
        height: chartViewHeight*0.95 ,
        autosize: { type: 'fit', resize: true },
        config: this.conf.vegaconfig
    });

    vegaEmbed('#chartview .chartcontainer', vegachart, { actions: false })
        .then((result) => {
            // Access the Vega view instance
            var view = result.view;
            var spec = result.spec; // Capture the spec here

            // Add hover event listeners to the view
            view.addEventListener('mousemove', (event, item) => {
                if (item && item.datum) {
                    storeInteractionLogs('hover on main chart', {
                        encoding: spec.encoding,
                        mark: spec.mark,
                        fields: item.datum
                    }, new Date());
                }
            });

        })
        .catch(console.error);

    if (eventsource != 'texteditor')
        this._cheditor.session.setValue(JSON.stringify(this.data, null, '  '));

    if (eventsource != 'uicontrols')
        this._updateChartComposer(this.data);
}

     _updateChartComposer(chart_data){
         if(this.data['mark'])
             $('#ch-mark').val(this.data['mark']['type'])
         var channels = ['x', 'y', 'color', 'size', 'shape']
         channels.forEach((ch) => {
             if(chart_data['encoding'][ch]) {
                 // if (chart_data['encoding'][ch]['field'].toString()=='cost_total_a'){
                 //     $('#ch-' + ch).val('Cost_Total_a')
                 // }
                 // else {
                 $('#ch-' + ch).val(chart_data['encoding'][ch]['field'])
     
                 if(ch != 'shape') {
                     if(chart_data['encoding'][ch]['bin'])
                         $('#ch-' + ch + 'trans').val('bin')
                     else if(chart_data['encoding'][ch]['aggregate'])
                         $('#ch-' + ch + 'trans').val(chart_data['encoding'][ch]['aggregate'])
                     else
                         $('#ch-' + ch + 'trans').val('-')
                 }
             }
             else {
                 $('#ch-' + ch).val('-')
                 if(ch != 'shape') $('#ch-' + ch + 'trans').val('-')
             }
         })
     }
 
     _validateChart(chart, callback) {
         var sp = chart
         if(typeof chart == 'object') 
             sp = JSON.stringify(chart)

         $.ajax({
             type: 'POST',
             crossDomain: true,
             url: app.sumview.conf.backend + '/encode',
             data: JSON.stringify([sp]),
             contentType: 'application/json'
         }).done((data) => {
            //  console.log(data)
             callback(data)
         }).fail((xhr, status, error) => {
             alert('This chart is currently not supported.')
         })
     }
 }