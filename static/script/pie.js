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
                }
            }
        },
        aspectRatio: 1
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
    //FIXME: Update chart aspect ratio values
    let breakpoints = [[0, 1], [640, 1.2], [768, 1.4], [1024, 1.6], [1280, 1.8], [1536, 3], [9999]];
    //`breakpoints.every()` stops whenever the executed function returns `false`, in order to not overwhelm the user CPU
    breakpoints.every((breakpoint, index) => {
        //Iterating through each breakpoint and comparing those values with the client's brower size
        if(window.screen.width >= breakpoint[0] && window.screen.width < breakpoints[index + 1][0]){
            //Applying the object defined value and updating the chartm then quitting the loop
            pieChart.options.aspectRatio = breakpoint[1];
            return false
        }
        else{
            return true
        }
    });
    pieChart.update()
}