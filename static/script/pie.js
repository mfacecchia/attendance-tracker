var pieCanvas = document.getElementById('attendancePercentageStatistics').getContext('2d');
const pieChartConfig = {
    type: 'pie',
};
var pieChart = new Chart(pieCanvas, pieChartConfig);

function updatePieChart(apiData){

}