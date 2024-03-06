var pieCanvas = document.getElementById('attendancePercentageStatistics').getContext('2d');
const pieChartConfig = {
    type: 'pie',
};
var pieChart = new Chart(pieCanvas, pieChartConfig);

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