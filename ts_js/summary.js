/// <reference path="../_types/c3/c3.d.ts"/>
"use strict";
var c3 = require('c3');
var $ = require('jquery');
$.get(window.location.origin + '/summ', {}, function (d) {
    console.log(d);
    if (d['json']) {
        /**
         * returned d has a specific format for entry into c3 generate
         * 'x' the x axis as identified in the response, is identified as 'x'
         * 'json' an object with keys and values as arrays, the 'x' values as well as the values from other data series
         * 'hide' an array of keys in json to be hidden in the chart by default
         */
        var chart = c3.generate({
            data: d,
            axis: {
                x: {
                    label: {
                        text: 'Generation',
                        position: 'outer-center',
                    }
                },
                y: {
                    label: {
                        text: 'Success',
                        position: 'outer-middle',
                    }
                }
            }
        });
    }
    else {
        $('.no-generations').css('display', 'block');
    }
}, 'json');
//
// // var chart = c3.generate({
// //     data: {
// //         json: {
// //             x: [30, 50, 100, 230, 300, 310],
// //             data2: [30, 200, 100, 400, 150, 250],
// //             data3: [130, 300, 200, 300, 250, 450]
// //         }
// //     }
// // });
//
//
// function makeChart() {
//
//     var chart = c3.generate({
//         bindto: '#chart',
//         data: {
//             x: 'x',
//             json: {
//                 x: [30, 50, 100, 230, 300, 310],
//                 data2: [30, 200, 100, 400, 150, 250],
//                 data3: [130, 300, 200, 300, 250, 100]
//             }
//         }
//     });
//
//     //
//     // setTimeout(function () {
//     //     chart.load({
//     //         columns: [
//     //             ['data1', 100, 250, 150, 200, 100, 350]
//     //         ]
//     //     });
//     // }, 1000);
//     //
//     // setTimeout(function () {
//     //     chart.load({
//     //         columns: [
//     //             ['data3', 80, 150, 100, 180, 80, 150]
//     //         ]
//     //     });
//     // }, 1500);
//     //
//     // setTimeout(function () {
//     //     chart.unload({
//     //         ids: 'data2'
//     //     });
//     // }, 2000);
//
// }
//
// window['makeChart'] = makeChart;
//
