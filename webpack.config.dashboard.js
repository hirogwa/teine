var ExtractTextPlugin = require('extract-text-webpack-plugin');
var webpack = require('webpack');

module.exports = {
    entry: {
        dashboard: "./teine/static/dashboard-assets.js",
        account: "./teine/static/account-assets.js"
    },
    output: {
        path: __dirname + '/teine/static',
        filename: "[name]-bundle.js"
    },
    resolve: {
        alias: {
            bootbox: 'bootbox',
            bootstrapNotify: 'bootstrap-notify'
        }
    },
    externals: {
        jquery: 'jQuery'
    },
    module: {
        loaders: [{
            test: /\.html$/,
            loader: 'underscore-template-loader'
        }, {
            test: /\.css$/,
            loader: ExtractTextPlugin.extract('style-loader', 'css-loader')
        }]
    },
    plugins: [
        new ExtractTextPlugin('[name]-bundle.css')
    ]
};
