canvas = document.getElementById('attendanceStatistics').getContext('2d');
const config = {
    type: 'bar',
    options: {
        borderRadius: 5,
        borderWidth: 1,
        scales: {
            y: {
                beginAtZero: true,
                ticks: {
                    precision: 0,
                },
            }
        }
        //TODO: Add graph title
    }
}
var chart = new Chart(canvas, config);

function updateChart(apiData){
    let newChartDataset = [];
    let newChartLabels = [];

    apiData.forEach(course => {
        //Array used to store the ordered lessons based on chart labels dates (gets cleaned up on every loop execution)
        var orderedLessonAttendancesCount = [];
        course['dataLezione'].forEach((courseDate, index) => {
            //Checking if the label with the defined date is already in the array, otherwise adding it
            if(newChartLabels.indexOf(courseDate) == -1){
                newChartLabels.push(courseDate);
            }
            //Appending at the defined label's index the relative attendances count
            orderedLessonAttendancesCount[newChartLabels.indexOf(courseDate)] = course['conteggioPresenze'][index];
        });
        newChartDataset.push(
            {
                //Dataset label
                label: course['nomeCorso'],
                data: orderedLessonAttendancesCount
            }
        );
    });
    chart.data.datasets = newChartDataset;
    //Lessons dates (X axis value)
    chart.data.labels = newChartLabels;
    chart.update()
}