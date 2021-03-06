/// <reference path="../_types/c3/c3.d.ts"/>
"use strict";
var c3 = require('c3');
// var chart = c3.generate({
//     data: {
//         json: {
//             x: [30, 50, 100, 230, 300, 310],
//             data2: [30, 200, 100, 400, 150, 250],
//             data3: [130, 300, 200, 300, 250, 450]
//         }
//     }
// });
function makeChart() {
    var chart = c3.generate({
        bindto: '#chart',
        data: {
            x: 'x',
            json: {
                x: [30, 50, 100, 230, 300, 310],
                data2: [30, 200, 100, 400, 150, 250],
                data3: [130, 300, 200, 300, 250, 100]
            }
        }
    });
    //
    // setTimeout(function () {
    //     chart.load({
    //         columns: [
    //             ['data1', 100, 250, 150, 200, 100, 350]
    //         ]
    //     });
    // }, 1000);
    //
    // setTimeout(function () {
    //     chart.load({
    //         columns: [
    //             ['data3', 80, 150, 100, 180, 80, 150]
    //         ]
    //     });
    // }, 1500);
    //
    // setTimeout(function () {
    //     chart.unload({
    //         ids: 'data2'
    //     });
    // }, 2000);
}
window['makeChart'] = makeChart;
