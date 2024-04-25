/*************************************************************************
 * Copyright (c) 2018 Jian Zhao
 *
 *************************************************************************
 *
 * @author
 * Jian Zhao <zhao@fxpal.com>
 *
 *************************************************************************/

// style
import './assets/scss/app.scss'

// global libs
var d3 = require('d3')
window.d3 = d3
var _ = require('lodash');
window._ = _

import { parseurl, updateData} from './utils.js'

// app instance
var app = {}
app.logger = []
window.app = app

var datafile = '/data/birdstrikes.json'
// var datafile = 'data/movies_cleaned.json'

$(document).ready(function() {
    var parameters = parseurl()
    if(parameters['data']) 
        datafile = parameters.data
    
    // get and visualize data
    $.get(datafile).done((d) => {
        updateData(d, datafile)
    })
})
