var total_bar_data = total_bar_data
var chart_id = chart_id
var ctx = document.getElementById(chart_id).getContext('2d')
var lineChart = new Chart(ctx, {
    type: 'bar',
    data: total_bar_data,
    options:{
        scales: {
            x: {ticks:{color:'#FFFAFA'}},
            y: {ticks:{color:'#FFFAFA'}}
        },
        indexAxis: 'y',
        elements: {
          bar: {
            borderWidth: 2,
            borderColor: 'grey'
          }
        },
        responsive: false,
        plugins:{
            title: {
            display: true,
            text: title_text,
            color: "white",
            },
            legend: {
                display: false,

            }
        }
    }
})