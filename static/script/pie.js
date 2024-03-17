var pieCanvas = document.getElementById('attendancePercentageStatistics').getContext('2d');
const pieChartConfig = {
    type: 'pie',
    options: {
        plugins: {
            legend: {
                position: 'right',
                labels: {
                    font: {
                        size: 14
                    },
                    textAlign: 'left'
                }
            }
        },
        aspectRatio: 1.3
    }
};
var pieChart = new Chart(pieCanvas, pieChartConfig);
resizeChart();
window.addEventListener('resize', resizeChart);

function updatePieChart(apiData){
    //`percentages` variable represents the percentages calculated for the "attended/not attended" relation (rounded to 2 decimal signs)
    //NOTE: `percentages[0]` is the attended lessons percentage, `percentages[1]` is the not attended ones
    var percentages = [Math.round((apiData[0].attended_lessons / apiData[0].total_lessons) * 100)];
    percentages[1] = 100 - percentages[0];

    pieChart.data = {
        labels: [`Presenze (${percentages[0]}%)`, `Assenze (${percentages[1]}%)`],    

        datasets: [{
            backgroundColor: [
                'rgba(50, 205, 50, 0.5)',
                'rgba(255, 99, 132, 0.5)',
            ],
            borderColor: [
                'rgb(50, 205, 50)',
                'rgb(255, 99, 132)',
            ],
            data: [
                apiData[0].attended_lessons,
                apiData[0].not_attended_lessons,
            ],
        }]
    }
    pieChart.update();
}

//Resiezes the pie chart based on the some set breakponts
function resizeChart(){
    //Matrix containing every breakpoint to check for and the relative scale to apply to the chart
    let breakpoints = [[0, 1.3, 12], [640, 1.4, 16], [768, 1.5, 17], [1024, 1.7, 20], [1280, 1.8, 20], [1536, 2, 20], [1920, 2.4, 20], [3840, 5, 30], [9999]];
    //`breakpoints.every()` stops whenever the executed function returns `false`, in order to not overwhelm the user CPU
    breakpoints.every((breakpoint, index) => {
        //Iterating through each breakpoint and comparing those values with the client's brower size
        if(window.screen.width >= breakpoint[0] && window.screen.width < breakpoints[index + 1][0]){
            //Applying the object defined value and updating the chartm then quitting the loop
            pieChart.options.aspectRatio = breakpoint[1];
            pieChart.options.plugins.legend.labels.font.size = breakpoint[2]
            return false
        }
        else{
            return true
        }
    });
    pieChart.update()
}