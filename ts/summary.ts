/// <reference path="../_types/c3/c3.d.ts"/>

import c3 = require('c3');
import $ =  require('jquery');

let chart = null;

function refreshChart() {
    $.get(window.location.origin + '/summ', {}, function (d) {

        if (d['json']) {

            /**
             * returned d has a specific format for entry into c3 generate
             * 'x' the x axis as identified in the response, is identified as 'x'
             * 'json' an object with keys and values as arrays, the 'x' values as well as the values from other data series
             * 'hide' an array of keys in json to be hidden in the chart by default
             */
            if (!chart) {
                chart = c3.generate({
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
                    },
                    zoom: {
                        enabled: true
                    }
                });

            } else {
                chart.load(d);
            }
            $('#summary-none').addClass('summary-none');
        } else {
            if (chart) {
                chart.destroy();
                chart = null;
            }
            $('#summary-none').removeClass('summary-none');
        }

    }, 'json');
}

$('#refresh').click(refreshChart);

refreshChart();
