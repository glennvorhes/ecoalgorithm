/**
 * Created by glenn on 10/2/16.
 */

const path = require('path');

module.exports = {
    watch: true,
    entry: path.join(__dirname, 'ts_js', 'summary.js'),
    output: {
        filename: 'summary.js',
        path: path.join(__dirname, 'ecoalgorithm', 'static')
    },
    externals: {
        // "c3": "c3"
    }
};