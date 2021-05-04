var total_line_data = total_line_data
var chart_id = chart_id
var ctx = document.getElementById(chart_id).getContext('2d')
var lineChart = new Chart(ctx, {
    type: 'line',
    data: total_line_data,
    options:{
        responsive: false,
        scales: {
            x: {ticks:{color:'#FFFAFA'}, grid:{color:'#454444'}},
            y: {ticks:{color:'#FFFAFA'}, grid:{color:'#454444'}}
        },
        plugins:{
            title: {
            display: true,
            text: title_text,
            color: "white",
            },
            legend: {
                display: true,
                labels: {
                    color: 'white'
                }
            }
        }
    }
})