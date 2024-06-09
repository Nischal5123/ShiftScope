const path = require('path');
const { CleanWebpackPlugin } = require('clean-webpack-plugin');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const CopyWebpackPlugin = require('copy-webpack-plugin');

module.exports = {
  mode: 'development', // or 'production'
  context: path.resolve(__dirname, 'client'),

  entry: {
    app1: './app1.js'
  },

  output: {
    path: path.resolve(__dirname, 'public'),
    filename: './assets/js/[name].bundle.js'
  },

  module: {
    rules: [
      {
        test: /\.js$/,
        include: /client/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-env']
          }
        }
      },
      {
        test: /\.html$/,
        use: ['html-loader']
      },      
      {
        test: /\.css$/,
        use: [
          MiniCssExtractPlugin.loader,
          {
            loader: 'css-loader',
            options: {
              sourceMap: true
            }
          }
        ],
      },
      {
        test: /\.scss$/,
        include: [path.resolve(__dirname, 'client', 'assets', 'scss')],
        use: [
          MiniCssExtractPlugin.loader,
          {
            loader: 'css-loader',
            options: {
              sourceMap: true
            }
          },
          {
            loader: 'sass-loader',
            options: {
              sourceMap: true
            }
          }
        ]
      },
      {
        test: /\.(jpg|png|gif|svg)$/,
        type: 'asset/resource', // Use 'asset/resource' for images
        generator: {
          filename: 'assets/media/[name][ext]'
        }
      },
      {
        test: /\.(woff|woff2|eot|ttf|otf)$/,
        type: 'asset/resource', // Use 'asset/resource' for fonts
        generator: {
          filename: 'assets/fonts/[name][ext]'
        }
      }
    ]
  },

  plugins: [
    new CleanWebpackPlugin(),
    new HtmlWebpackPlugin({
      template: './index.html', // Path relative to the context directory
      chunks: ['app1'],
      filename: './index.html'
    }),
    new MiniCssExtractPlugin({
      filename: './assets/css/app.css' // Output for CSS file
    }),
    new CopyWebpackPlugin({
      patterns: [
        { from: path.resolve(__dirname, 'server/web/static/css/main.css'), to: 'assets/css' }
      ]
    })
  ],

  // devServer: {
  //   contentBase: path.join(__dirname, 'public'),
  //   compress: true,
  //   port: 9000,
  //   historyApiFallback: true // Ensure this is enabled to serve the index.html file for all routes
  // },

  devtool: 'eval-source-map', 
  cache: true,
  
  stats: {
    children: true
  }
};
