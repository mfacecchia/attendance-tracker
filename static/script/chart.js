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
    }
}
var chart = new Chart(canvas, config);

function updateChart(apiData){
    let newChartDataset = [];
    let newChartLabels = [];

    apiData.forEach(course => {
        newChartLabels.push(...course['dataLezione'])
        var orderedLessonAttendancesCount = []

        //Updating lessons to place attendances count in the right chart's label
        newChartLabels.forEach((element, index) => {
            //Checking if course's array position exists, it it doesn't the last element is selected for each iteration
            if(course['dataLezione'][index] == undefined){
                if(element != course['dataLezione'][course['dataLezione'].length - 1]){
                    //Adding a null placeholder value if the lesson date does not match with the course's current array value
                    orderedLessonAttendancesCount.push(null);
                }
                else{
                    orderedLessonAttendancesCount.push(course['conteggioPresenze'][course['conteggioPresenze'].length - 1])
                }
            }
            else{
                if(element != course['dataLezione'][index]){
                    orderedLessonAttendancesCount.push(null);
                }
                else{
                    orderedLessonAttendancesCount.push(course['conteggioPresenze'][index])
                }
            }
        })
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