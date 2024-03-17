function getTeacherID(){
    //Returns the selected teacher value from `select option` DOM element
    let select = document.getElementsByName('assignedTeacher')[0]
    let selectionIndex = select.options.selectedIndex;
    return select.options[selectionIndex].value;
}

function getTeacherCourses(){
    //Makes an async request to Python API route which returns a list of all selected teacher's enrolled courses
    let teacherID = getTeacherID()
    $.ajax({
        url: '/user/courses',
        method: 'get',
        data: {'uid': teacherID},
        success: function(response){
            //Calling the function to update the courses `select option` DOM element with the API response as parameter
            updateCoursesSelection(response);
        }
    });
}

function updateCoursesSelection(response){
    let coursesSelect = document.getElementsByName('course')[0];

    //Clearing `select` options and adding all API obtained courses as possible options
    $(coursesSelect).empty();
    let option = document.createElement('option');
    option.text =  '-- Seleziona un corso --';
    option.value = '';
    coursesSelect.options.add(option);
    response.forEach(course => {
        let option = document.createElement('option');
        option.text = option.value = course;
        coursesSelect.options.add(option);
    });
}