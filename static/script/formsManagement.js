function getCheckboxes(){
    //Getting all checkboxes from the table
    let checkboxes = document.querySelectorAll('input[type="checkbox"]');
            
    //Updating the parents' values (label wrapping all checkboxes) and setting an event listener for each checkbox
    checkboxes.forEach(checkbox => {
        updateButtonStyle(checkbox.value, checkbox.checked);
        checkbox.addEventListener('change', updateAttendancesStatus);
    });
}

function updateAttendancesStatus(event){
    //Passing as functions parameters the value (repesenting the same value of label's ID) and a boolean value representing the checkbox state
    updateButtonStyle(event.target.value, event.target.checked);
}

//Updates the button background color and text by manipulating classes
function updateButtonStyle(element, present = false){
    var label = document.getElementById(element)
    //If the checked value is `True` the button becomes blue and updates the label text (childNode 2)
    if(present){
        label.classList.add('dark-blue');
        label.classList.remove('orange');
        label.childNodes[2].textContent = 'Presente';
    }
    else{
        label.classList.add('orange');
        label.classList.remove('dark-blue');
        label.childNodes[2].textContent = 'Assente';
    }
}

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


//Shows a confirmation checkbox if the the user selects "Admin" as the new user role
function adminRoleChosen(){
    let chosenRole = document.querySelector('#role').value;
    let pwVerificationLabel = document.querySelector('#adminVerification');
    let pwVerificationCheckbox = pwVerificationLabel.childNodes[1];
    if(chosenRole == 'Admin'){
        pwVerificationLabel.style.display = 'block';
        pwVerificationCheckbox.checked = false;
    }
    else{
        pwVerificationLabel.style.display = 'none';
        pwVerificationCheckbox.checked = true;
    }
}