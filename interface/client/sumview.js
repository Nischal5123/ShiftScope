/*************************************************************************
 * Copyright (c) 2024 Sanad Saha
 *
 *************************************************************************
 *
 * @author
 * Sanad <sahasa@oregonstate.edu>
 *
 *************************************************************************/

import EventEmitter from "events"
var logging = true
export default class SumView extends EventEmitter {
    constructor(container, data, conf) {
        super()

        this.container = container
        this.data = data
        this.conf = conf

        this._params = {
            recradius: 0.1,
            recnum: 6,
            dotr: 11,
            distw: 0.5,
            clthreshold: 0.4,
            ngbrN: 6
        }
        this._charts = []
        this._allRecommendedcharts = []
        this._baselinecharts = []
        this._prevcharts = []
        this._selectedChartID = -1
        this._selectedbookmarkedChartID = -1
        this._performanceData = {}
        
        this._varclr = d3.scaleOrdinal(['#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231', '#911eb4', '#46f0f0', '#f032e6', '#bcf60c', '#fabebe', '#008080', '#e6beff', '#9a6324', '#fffac8', '#800000', '#aaffc3', '#808000', '#ffd8b1', '#000075'])
        this._varclr = d3.scaleOrdinal(['#F3C300', '#875692', '#F38400', '#A1CAF1', '#BE0032', '#C2B280', '#848482', '#008856', '#E68FAC', '#0067A5', '#F99379', '#604E97', '#F6A600', '#B3446C', '#DCD300', '#882D17', '#8DB600', '#654522', '#E25822', '#2B3D26'])
        this._usrclr = d3.scaleOrdinal(d3.schemeGreys[5]).domain([0, 1, 2, 3, 4])
        this._bookmarkedCharts = []

        this._algorithm= 'ActorCritic'
        this._baseline= 'Momentum'

        this._init()
    }

    get charts() {
      return this._charts
    }

    get baselineCharts() {
        return this._baselinecharts
    }

    get bookmarkedCharts() {
        return this._bookmarkedCharts
    }

     get allrecommendedCharts() {
        return this._allRecommendedcharts
    }

    get selectedChartID() {
        return this._selectedChartID
    }


     set bookmarkedselectedChartID(ch) {
        this._svgDrawing.selectAll('.chartdot.selected')
            .classed('selected', false)
        if (ch < 0) {
            this._selectedChartID = -1
        } else {
            this._selectedChartID = ch
            this._svgDrawing.selectAll('.chartdot')
                .filter((c) => {
                    return c.overallchid == ch
                })
                .classed('selected', true)
            var selectedChart = _.find(this._bookmarkedCharts, (d) => {
                return this._selectedChartID == d.overallchid
            })
            this.emit('clickchart', selectedChart)
        }
    }

    set selectedChartID(ch) {
        this._svgDrawing.selectAll('.chartdot.selected')
            .classed('selected', false)
        if (ch < 0) {
            this._selectedChartID = -1
        } else {
            this._selectedChartID = ch
            this._svgDrawing.selectAll('.chartdot')
                .filter((c) => {
                    return c.chid == ch
                })
                .classed('selected', true)
            var selectedChart = _.find(this._charts, (d) => {
                return this._selectedChartID == d.chid
            })
            this.emit('clickchart', selectedChart)
        }
    }
  

    _init() {
        this.container.select('svg').remove()
        this.svg = this.container.append('svg')
            .attr('width', this.conf.size[0])
            .attr('height', this.conf.size[1])
        this._svgDrawing = this.svg.append('g')
            .attr('translate', 'transform(' + this.conf.margin + ',' + this.conf.margin + ')')
        this._svgDrawing.append('g')
            .attr('class', 'bubblelayer')
        this._svgDrawing.append('g')
            .attr('class', 'textlayer')
        this._svgDrawing.append('circle')
            .attr('class', 'cursorc')
            .attr('r', this.conf.size[0] * this._params.recradius)
            .style('visibility', 'hidden')
        this._svgDrawing.append('rect')
            .attr('class', 'background')
            .attr('x', 0)
            .attr('y', 0)
            .attr('width', this.conf.size[0])
            .attr('height', this.conf.size[1])
            .on('click', () => {
                if (!this.conf.norecommend && this._charts.length >= 3) {
                    var p = d3.mouse(this._svgDrawing.node())
                    this._charts = _.filter(this._charts, (c) => {
                        return !c.created
                    })
                    // this.render()
                    this._recommendCharts()
                } else {
                    // alert('You need to create at least 3 charts.')
                }
            })
            .on('mouseover', () => {
                this._svgDrawing.select('.cursorc').style('visibility', 'visible')
            })
            .on('mouseout', () => {
                this._svgDrawing.select('.cursorc').style('visibility', 'hidden')
            })
            .on('mousemove', () => {
                var p = d3.mouse(this._svgDrawing.node())
                this._svgDrawing.select('.cursorc').attr('cx', p[0]).attr('cy', p[1])
            })
        this._svgDrawing.append('g')
            .attr('class', 'chartlayer')
    }

    update(callback, attributesHistory = null) {
        this._prevcharts = this._charts

        this._recommendCharts(attributesHistory)
        this._collectAllRecommendedCharts()
        // this.render()
        // if (callback) callback()

    }

    highlight(chid, hoverin, bookmarked = false) {
        this._svgDrawing.selectAll('.chartdot.hovered').classed('hovered', false)
        if (hoverin) {
            if (bookmarked) {
                this._svgDrawing.selectAll('.chartdot')
                    .filter((c) => {
                        return c.overallchid == chid
                    })
                    .classed('hovered', true)
            } else {
                this._svgDrawing.selectAll('.chartdot')
                    .filter((c) => {
                        return c.chid == chid
                    })
                    .classed('hovered', true)
            }
        }
    }

// collect all recommended charts
_collectAllRecommendedCharts() {
    for (var i = 0; i < this._charts.length; i++) {
        if (this._charts[i]) {
            //change the chart id to the next available id without changing original id
            this._charts[i].overallchid = this._allRecommendedcharts.length;
            this._allRecommendedcharts.push(this._charts[i]);
        }
    }

}

_recommendCharts(attributesHistory, callback) {
    // Question: When phase of flight has the highest number of birdstrike records in
    // June (Flight_Date)? :['when_phase_of_flight', 'flight_date']
    // Question: What speed (IAS) in knots could cause the substantial (Effect Amount
    // of damage) damage of AVRO RJ 85 (Aircraft Make Model)? :['speed_ias', 'aircraft_make_model']
    if (attributesHistory == null) {
        attributesHistory = [];
    }

    // Get the selected algorithm directly here
    var algorithmDropdown = document.getElementById("algorithm");
     this._algorithm = algorithmDropdown.value;

      // Get the selected baseline directly here
    var baselinealgorithmDropdown = document.getElementById("baseline");
     this._baseline = baselinealgorithmDropdown.value;

    // also send bookmarked charts
    var JsonRequest = {
        history: JSON.stringify(attributesHistory),
        bookmarked: this._bookmarkedCharts,
        algorithm: this._algorithm,
        baseline:  this._baseline
    };

    $.ajax({
        context: this,
        type: 'POST',
        crossDomain: true,
        url: this.conf.backend + '/top_k',
        data: JSON.stringify(JsonRequest),
        contentType: 'application/json'
    }).done((data) => {
        this._charts = [];
        this._baselinecharts = [];
        this._performanceData = data['distribution_map'];
        for (var i = 0; i < data['chart_recommendations'].length; i++) {
            // returns the recommendations and the distribution of fields
            if (data['chart_recommendations'][i]) {
                var chart = {
                    originalspec: JSON.parse(data['chart_recommendations'][i]),
                    created: true,
                    chid: i+1,
                };
                this._charts.push(chart);

            }
        }
        for (var j = 0; j < data['baseline_chart_recommendations'].length; j++) {
            // returns the recommendations and the distribution of fields
            if (data['chart_recommendations'][j]) {
                var bchart = {
                    originalspec: JSON.parse(data['baseline_chart_recommendations'][j]),
                    created: true,
                    chid: j,
                };
                this._baselinecharts.push(bchart);

            }
        }
        if (logging) {
            app.logger.push({ time: Date.now(), action: 'system-recommendations', data: this._charts });
        }
        if (logging) {
            app.logger.push({ time: Date.now(), action: 'current_distribution', data: data['distribution_map'] });
        }
        // Trigger the render method only on success
        // this.render();
        this.emit('recommendchart', this._charts);
    }).fail((xhr, status, error) => {
        alert('Cannot Generate Recommendations.');
    }).always(() => {
        // Trigger the callback function regardless of success or failure
        if (callback) {
            callback();
        }
    });
}

    }
