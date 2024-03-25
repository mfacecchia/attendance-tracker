var barCanvas = document.getElementById('attendanceStatistics').getContext('2d');
const barChartConfig = {
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
        },
        plugins: {
            legend: {
                labels: {
                    font: {
                        size: 14
                    }
                }
            }
        }
    }
}
var barChart = new Chart(barCanvas, barChartConfig);
resizeChart()
window.addEventListener('resize', resizeChart)

function updateBarChart(apiData){
    //All courses names obtained from the API Response
    var coursesNames = [];
    //All courses dates obtained from the API Response
    var coursesDates = [];
    //NOTE: Matrix subdivided per course name
    var attendancesCount = [];
    var chartDatasets = [];

    apiData.forEach(course => {
        //Checking if the courses names and lessons dates are already in the `coursesNames` and `coursesDates` arrays, otherwise the values will be added at the end of them
        if(coursesDates.indexOf(course.dataLezione) == -1){
            coursesDates.push(course.dataLezione)
        }
        if(coursesNames.indexOf(course.nomeCorso) == -1){
            coursesNames.push(course.nomeCorso)
        }
        //Looping through each obtained lesson date to add the relative attendances count based on course name
        coursesDates.forEach((date, dateIndex) => {
            if(date == course.dataLezione){
                //Getting the course position in the array
                courseIndex = coursesNames.indexOf(course.nomeCorso);
                if(!Array.isArray(attendancesCount[courseIndex])){
                    attendancesCount[courseIndex] = []
                }
                //Adding the lesson attendances count at the relative course `coursesNames` index and `dateIndex` value in order to place it in the correct date position
                attendancesCount[courseIndex][dateIndex] = course.conteggioPresenze;
            }
        })
    });
    //Adding all datasets in an array and then to the chart itself
    coursesNames.forEach((courseName, index) => {
        chartDatasets.push({
            //NOTE: `label` represents the dataset "title"
            label: courseName,
            data: attendancesCount[index]
        })
    })
    //NOTE: `chart.data.labels` represent all the X axis labels
    barChart.data.labels = [...coursesDates];
    barChart.data.datasets = chartDatasets;
    barChart.update();
}

//Resiezes the bar chart legend font size based on the some set breakponts
function resizeChart(){
    //Matrix containing every breakpoint to check for and the relative scale to apply to the chart
    let breakpoints = [[1024, 13], [1280, 14], [1536, 15], [1920, 15], [3840, 20], [9999]];
    //`breakpoints.every()` stops whenever the executed function returns `false`, in order to not overwhelm the user CPU
    breakpoints.every((breakpoint, index) => {
        //Iterating through each breakpoint and comparing those values with the client's brower size
        if(window.innerWidth >= breakpoint[0] && window.innerWidth < breakpoints[index + 1][0]){
            //Applying the object defined value and updating the chartm then quitting the loop
            barChart.options.plugins.legend.labels.font.size = breakpoint[1]
            return false
        }
        else{
            return true
        }
    });
    barChart.update()
}