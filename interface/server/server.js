const express = require('express')
const path = require('path'); // Import the 'path' module

const bodyParser = require('body-parser'),
	compress = require('compression'),
	methodOverride = require('method-override')

const webpackMiddleware = require('webpack-dev-middleware'),
	webpack = require('webpack'),
	webpackConfig = require('../webpack.config.js')

const app = express()
// configure
if(process.env.NODE_ENV != 'prod')
	app.use(webpackMiddleware(webpack(webpackConfig)))
app.use(bodyParser.json({limit: '50mb'}));
app.use(bodyParser.urlencoded({extended: true, limit: '50mb', parameterLimit: 50000}))
app.use(compress())
app.use(methodOverride())

//this is for the dataset
app.use('/data', express.static('staticdata'))

// this is for welcome page post-task page and so on
app.use('/static', express.static(path.join(__dirname, 'web/static')));

// Route for the post-task survey
app.get('/post-task-survey', (req, res) => {
    res.sendFile(path.join(__dirname, 'web/templates', 'post-task-survey.html'));
});

// Route for the pilot introduction page
app.get('/welcome', (req, res) => {
    res.sendFile(path.join(__dirname, 'web/templates', 'welcome.html'));
});


app.listen(8000, function() {
	console.log('Server: listening 8000')
});;
