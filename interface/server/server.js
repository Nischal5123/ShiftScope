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
// static directories
app.use(express.static('public'))
app.use('/data', express.static('staticdata'))


app.get('/post-task-survey.html', (req, res) => {
    // Send the static post-task-survey.html file
    res.sendFile('post-task-survey.html');
});

app.get('/index-demo.html', (req, res) => {
    // Send the static post-task-survey.html file
    res.sendFile('/Users/aryal/Desktop/Personal/RLVisRec/interface/client/index-demo.html');
});
app.listen(8000, function() {
	console.log('Server: listening 8000')
});;
