document.addEventListener('DOMContentLoaded', function (event) {
    
    const POST = "POST";
    const URL = "https://localhost/restore_password/";
    const PASSWORD_ID = "password";
    const SECOND_PASSWORD_ID = "second_password";
    
    let HTTP_STATUS = {OK: 200, BAD_REQUEST: 400, UNAUTHORIZED: 401};
    let restorePasswordForm = document.getElementById("restore-form");
    let alertDiv = document.getElementById("restore-alert");

    restorePasswordForm.addEventListener("submit", function(e) {
        e.preventDefault();
        alertDiv.innerHTML = "";
        let c1 = checkPassword();
        let c2 = checkBothPasswords();
        if (c1 == true && c2 ==true) {
            restorePassword();
        }
    });

    function restorePassword() {
        let restoreURL = URL + document.location.href.split('/')[4];

        let restoreParams = {
            method: POST,
            body: new FormData(restorePasswordForm),
            redirect: "follow"
        };

        fetch(restoreURL, restoreParams)
            .then(response => getResponseInformation(response))
    }

    function getResponseInformation(response) {
        let status = response.status;

        if (status === HTTP_STATUS.OK) {
            restorePasswordForm.reset();
            let successAlert = document.createElement("div");
            let successText = document.createTextNode("Hasło zostało zmienione pomyślnie.");
            successAlert.setAttribute("class", "alert alert-success");
            successAlert.setAttribute("role", "alert");
            successAlert.appendChild(successText);
            alertDiv.appendChild(successAlert);
        } else if (status === HTTP_STATUS.BAD_REQUEST) {
            let warningAlert = document.createElement("div");
            let warningText = document.createTextNode("Hasło nie zostało poprawnie zmienione.");
            warningAlert.setAttribute("class", "alert alert-danger");
            warningAlert.setAttribute("role", "alert");
            warningAlert.appendChild(warningText);
            alertDiv.appendChild(warningAlert);
        } else if(status === HTTP_STATUS.UNAUTHORIZED) {
            let warningAlert = document.createElement("div");
            let warningText = document.createTextNode("Strona wygasła. Przeprowadź procedurę od początku.");
            warningAlert.setAttribute("class", "alert alert-danger");
            warningAlert.setAttribute("role", "alert");
            warningAlert.appendChild(warningText);
            alertDiv.appendChild(warningAlert);
        } else {
            console.error("Response status code: " + response.status);
            throw "Unexcepted response status: " + response.status;
        }
    }

    function checkPassword() {
        let password = document.getElementById(PASSWORD_ID);
        
        if (password.value.length < 8) {
            let passwordAlert = document.createElement("div");
            let warningText = document.createTextNode("Hasło musi składać się przynajmniej z 8 znaków.");
            passwordAlert.setAttribute("class", "alert alert-danger");
            passwordAlert.setAttribute("role", "alert");
            passwordAlert.appendChild(warningText);
            alertDiv.appendChild(passwordAlert);
            return false;
        }

        if (password.value.match(/[a-z]+/) && password.value.match(/[A-Z]+/) 
            && password.value.match(/[0-9]+/) && password.value.match(/[!@#$%^&*]+/)) {
            return true;
        } else {
            let passwordAlert = document.createElement("div");
            let warningText = document.createTextNode("Hasło musi zawierać dużą i małą literę, cyfrę oraz znak specjalny.");
            passwordAlert.setAttribute("class", "alert alert-danger");
            passwordAlert.setAttribute("role", "alert");
            passwordAlert.appendChild(warningText);
            alertDiv.appendChild(passwordAlert);
            return false;
        }

    }

    function checkBothPasswords() {
        let password = document.getElementById(PASSWORD_ID);
        let secondPassword = document.getElementById(SECOND_PASSWORD_ID);

        if (password.value == secondPassword.value) {
            return true;
        } else {
            let passwordAlert = document.createElement("div");
            let warningText = document.createTextNode("Hasła są różne.");
            passwordAlert.setAttribute("class", "alert alert-danger");
            passwordAlert.setAttribute("role", "alert");
            passwordAlert.appendChild(warningText);
            alertDiv.appendChild(passwordAlert);
            return false;
        }
    }


});