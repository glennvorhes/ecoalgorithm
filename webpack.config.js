/**
 * Created by glenn on 10/2/16.
 */

const path = require('path');

module.exports = {
    watch: true,
    entry: path.join(__dirname, 'js', 'results.js'),
    output: {
        filename: 'results.js',
        path: path.join(__dirname, 'ecoalgorithm', 'static')
    },
    externals: {
        // "c3": "c3"
    }
};