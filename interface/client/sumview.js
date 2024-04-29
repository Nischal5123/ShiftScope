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
        this._prevcharts = []
        this._clusterNum = 1
        this._bubbleSets = []
        this._variableSets = []
        this._showBubbles = true
        this._selectedChartID = -1
        this._rscale = d3.scaleLinear().domain([0, 4]).range([0, this._params.dotr])
        this._xscale = d3.scaleLinear().domain([0, 1])
            .range([this.conf.margin, this.conf.size[0] - this.conf.margin])
        this._yscale = d3.scaleLinear().domain([0, 1])
            .range([this.conf.margin, this.conf.size[1] - this.conf.margin])
        this._pie = d3.pie().sort(null).value(d => d.value)
        this._arc = d3.arc().innerRadius(this._params.dotr - 5).outerRadius(this._params.dotr)
        this._varclr = d3.scaleOrdinal(['#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231', '#911eb4', '#46f0f0', '#f032e6', '#bcf60c', '#fabebe', '#008080', '#e6beff', '#9a6324', '#fffac8', '#800000', '#aaffc3', '#808000', '#ffd8b1', '#000075'])
        this._varclr = d3.scaleOrdinal(['#F3C300', '#875692', '#F38400', '#A1CAF1', '#BE0032', '#C2B280', '#848482', '#008856', '#E68FAC', '#0067A5', '#F99379', '#604E97', '#F6A600', '#B3446C', '#DCD300', '#882D17', '#8DB600', '#654522', '#E25822', '#2B3D26'])
        this._usrclr = d3.scaleOrdinal(d3.schemeGreys[5]).domain([0, 1, 2, 3, 4])

        this._init()
    }

    get charts() {
        return this._charts
    }
    
    get selectedChartID() {
        return this._selectedChartID
    }

    set selectedChartID(ch) {
        this._svgDrawing.selectAll('.chartdot.selected')
            .classed('selected', false) 
        if(ch < 0) {
            this._selectedChartID = -1
        }
        else {
            this._selectedChartID = ch
            this._svgDrawing.selectAll('.chartdot')
                .filter((c) => {return c.chid == ch})
                .classed('selected', true)
            var selectedChart = _.find(this._charts, (d) => {return this._selectedChartID == d.chid}) 
            this.emit('clickchart', selectedChart) 
        }
    }
    set weight(w) {
        this._params.distw = w
        this.update()
    }

    set svgsize(size) {
        this.conf.size = size
        this._xscale.range([this.conf.margin, this.conf.size[0] - this.conf.margin])
        this._yscale.range([this.conf.margin, this.conf.size[1] - this.conf.margin])
        this.svg.attr('width', this.conf.size[0])
            .attr('height', this.conf.size[1])
        this.svg.select('.background')
            .attr('width', this.conf.size[0])
            .attr('height', this.conf.size[1])
        // this._createBubbles()
        this.render()
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
                if(!this.conf.norecommend && this._charts.length >= 3) {
                    var p = d3.mouse(this._svgDrawing.node())
                    this._charts = _.filter(this._charts, (c) => {return !c.created})
                    this.render()
                    this._recommendCharts()
                }
                else {
                    alert('You need to create at least 3 charts.')
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

    update(callback, attributesHistory=null) {
        this._prevcharts = this._charts


        //this.selectedChartID = -1
        // this._charts = this.data.chartspecs.map((d, i) => {
        //     var osp = _.extend({}, d)
        //     delete osp._meta

        //     var sp = JSON.stringify(osp)
        //     var vars = []
        //     this.data.chartdata.attributes.forEach((attr) => {
        //         sp = sp.replace(new RegExp(attr[0], 'g'), (m) => {
        //             vars.push(m)
        //             return attr[1]
        //         })
        //     })
        //     //var varnum = (sp.match(/num|str/g) || []).length
        //     return {originalspec: osp, normspec: sp, 
        //         vars: _.union(vars), created: false, chid: d._meta.chid, uid: d._meta.uid}
        // })
        
        this._recommendCharts(attributesHistory)
        this.render()
        if(callback) callback()
    
    }

    render() {
        // draw charts
        var charts = this._svgDrawing.select('.chartlayer')
            .selectAll('.chartdot')
            .data(this._charts, (d) => { return d.chid })

        // enter
        var chartsenter = charts.enter()
            .append('g')
            .attr('class', 'chartdot')
            .attr('transform', (d) => {
                return 'translate(' + this._xscale(d.coords[0]) + ',' + this._yscale(d.coords[1]) + ')'
            })
            .on('click', (d) => {
                this.selectedChartID = d.chid
                console.log(this.selectedChartID)
                console.log("This has been selected")
                if(logging) app.logger.push({time:Date.now(), action:'clickchart', data:d})
            })
            .on('mouseover', (d) => {
                this.highlight(d.chid, true)
                this.emit('mouseoverchart', d)
                d3.select('#tooltip')
                    .style('display', 'inline-block')
                    .style('left', (d3.event.pageX + 8) + 'px')
                    .style('top', (d3.event.pageY + 8) + 'px')
                if(logging) app.logger.push({time:Date.now(), action:'mousover', data:d})
            })
            .on('mouseout', (d) => {
                this._svgDrawing.selectAll('.chartdot.hovered').classed('hovered', false) 
                d3.select('#tooltip').style('display', 'none')
                if(logging) app.logger.push({time:Date.now(), action:'mouseout', data:d})
            })

        chartsenter.append('circle')
            .attr('r', this._params.dotr)
            .attr('cx', 0)
            .attr('cy', 0)        

        chartsenter.append('text')
            .attr('class', 'marktext')
            .attr('x', 0)
            .attr('y', 0)
            .text((d) => {return d.originalspec.mark.substring(0,1).toUpperCase()})

        chartsenter.append('rect')
            .attr('x', this._params.dotr - 5)
            .attr('y', this._params.dotr - 5)
            .attr('width', 10)
            .attr('height', 10)
            
        chartsenter.append('text')
            .attr('class', 'uidtext')
            .attr('x', this._params.dotr)
            .attr('y', this._params.dotr)
            .text((d) => { return d.created ? 'x' : d.uid })
        
        var arcs = chartsenter.selectAll('path')
            .data((d) => { return this._pie(d.vars.map((v) => {return {name: v, value: 1.0}})) })
        arcs.enter()
            .append('path')
            .attr('d', this._arc)
            .style('fill', (d) => { return this._varclr(d.data.name) })
        
        chartsenter.style('opacity', 0)
            .transition()
            // .duration(500)
            .style('opacity', 1)

        // update
        charts.transition()
            // .duration(1000)
            .attr('transform', (d) => {
                return 'translate(' + this._xscale(d.coords[0]) + ',' + this._yscale(d.coords[1]) + ')'
            })

        chartsenter.select('.marktext')
            .text((d) => {return d.originalspec.mark.substring(0,1).toUpperCase()})

        chartsenter.select('.uidtext')
            .text((d) => { return d.created ? 'x' : d.uid })
        
        arcs = charts.selectAll('path')
            .data((d) => { return this._pie(d.vars.map((v) => {return {name: v, value: 1.0}})) })
        arcs.enter()
            .append('path')
            .attr('d', this._arc)
            .style('fill', (d) => { return this._varclr(d.data.name) })
        arcs.attr('d', this._arc)
            .style('fill', (d) => { return this._varclr(d.data.name) })
        arcs.exit().remove()
        
        // exit
        charts.exit()
            .remove()
    }

    highlight(chid, hoverin) {
        this._svgDrawing.selectAll('.chartdot.hovered').classed('hovered', false) 
        if(hoverin) {
            this._svgDrawing.selectAll('.chartdot')
                .filter((c) => {return c.chid == chid})
                .classed('hovered', true)
        }
    }
  
    _recommendCharts(attributesHistory) {
        if (attributesHistory == null) {
            var attributesHistory = [['airport_name', 'flight_date', 'origin_state']]
        }
        else {
            var attributesHistory = attributesHistory
        }


        $.ajax({
            context: this,
            type: 'POST',
            crossDomain: true,
            url: this.conf.backend + '/top_k',    
            data: JSON.stringify(attributesHistory),
            contentType: 'application/json'
        }).done((data) => {
            // this._charts = data
            this._charts = []
            for(var i = 0; i < data.length; i++) {
                if(data[i]) {

                    var chart = {
                        originalspec: JSON.parse(data[i]),
                        // normspec: normspecs[vlcharts[i].index],
                        // embedding: embeddings[vlcharts[i].index],
                        // vars: vlcharts[i].vars,
                        created: true,
                        chid: i,
                        // uid: 0
                    }
                    this._charts.push(chart)
                }
            }
           if(logging) app.logger.push({time:Date.now(), action:'system-recommendations', data:this._charts})
        }).fail((xhr, status, error) => {
            alert('Cannot Generate Recommendations.')
        })
        
    }
}