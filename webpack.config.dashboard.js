var ExtractTextPlugin = require('extract-text-webpack-plugin');
module.exports = {
    entry: {
        dashboard: "./static/dashboard-assets.js"
    },
    output: {
        path: __dirname + '/static',
        filename: "[name]-bundle.js"
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
