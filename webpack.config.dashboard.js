module.exports = {
    entry: "./static/js/dashboard.js",
    output: {
        path: __dirname + '/static/js',
        filename: "dashboard-bundle.js"
    },
    module: {
        loaders: [{
            test: /\.html$/,
            loader: 'underscore-template-loader'
        }]
    }
};
