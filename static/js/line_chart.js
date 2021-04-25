var total_line_data = total_line_data
var chart_id = chart_id
var ctx = document.getElementById(chart_id).getContext('2d')
var lineChart = new Chart(ctx, {
    type: 'line',
    data: total_line_data,
    options:{
        responsive: false,
        title: {
        display: true,
        text: 'Covid Data'
        }
    }
})