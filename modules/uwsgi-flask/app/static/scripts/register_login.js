document.addEventListener('DOMContentLoaded', function (event) {
    
    const GET = "GET";
    const POST = "POST";
    const URL = "https://localhost/";

    const NAME_ID = "name";
    const SURNAME_ID = "surname";
    const EMAIL_ID = "email";
    const LOGIN_ID = "login";
    const PASSWORD_ID = "password";
    const SECOND_PASSWORD_ID = "second-password";
    
    let HTTP_STATUS = {OK: 200, CREATED: 201, BAD_REQUEST:400, NOT_FOUND: 404};
    let PASSWORD_STATUS = {0: "bardzo słabe.", 1: "słabe.", 2: "średnie.", 3: "silne.", 4: "bardzo silne."};
    let registrationForm = document.getElementById("signup-form");
    let passwordField = document.getElementById("password");
    let meter = document.getElementById("password-strength-meter");
    let passwordText = document.getElementById("password-strength-text");
    let alertDiv = document.getElementById("signup-alert");

    registrationForm.addEventListener("submit", function (event) {
        event.preventDefault();
        alertDiv.innerHTML = "";
        let c1 = checkName();
        let c2 = checkSurname();
        let c3 = checkEmail();
        let c4 = checkLogin();
        let c5 = checkPassword();
        let c6 = checkBothPasswords();
        if (c1 == true && c2 == true && c3 == true && c4 == true && c5 == true && c6 == true) {
            submitRegisterForm();
        }
    });

    function submitRegisterForm() {
        let registerUrl = URL + "signup";

        let registerParams = {
            method: POST,
            body: new FormData(registrationForm),
            redirect: "follow"
        };

        fetch(registerUrl, registerParams)
                .then(response => getRegisterResponseData(response))
                .then(response => displayRegisterAlert(response))
                .catch(err => {
                    console.log("Caught error: " + err);
                });
    }

    function getRegisterResponseData(response) {
        let status = response.status;

        if (status === HTTP_STATUS.CREATED || status === HTTP_STATUS.BAD_REQUEST) {
            return response.json();
        } else {
            console.error("Response status code: " + response.status);
            throw "Unexpected response status: " + response.status;
        }
    }

    function displayRegisterAlert(response) {
        if (response.registration == "Accept") {
            registrationForm.reset();
            meter.value = 0;
            passwordText.innerHTML = "";
            let successAlert = document.createElement("div");
            let successText = document.createTextNode("Zarejestrowano pomyślnie.");
            successAlert.setAttribute("class", "alert alert-success");
            successAlert.setAttribute("role", "alert");
            successAlert.appendChild(successText);
            alertDiv.appendChild(successAlert);
        } else if (response["login_exists"] == "Login already exists.") {
            let loginExistsAlert = document.createElement("div");
            let warningText = document.createTextNode("Login jest już zajęty.");
            loginExistsAlert.setAttribute("class", "alert alert-warning");
            loginExistsAlert.setAttribute("role", "alert");
            loginExistsAlert.appendChild(warningText);
            alertDiv.appendChild(loginExistsAlert);
        }
    }

    
    passwordField.addEventListener("input", function() {
        let password = passwordField.value;
        console.log(password);
        console.log(meter);
        let entropy = countEntropy(password);
        let state = 0;
        if (entropy < 1) {
            state = 0;
        } else if (entropy < 2) {
            state = 1;
        } else if (entropy < 4) {
            state = 2;
        } else if (entropy < 6) {
            state = 3;
        } else {
            state = 4;
        }
        meter.value = state;
        
        if (password !== "") {
            passwordText.innerHTML = "Hasło jest " + PASSWORD_STATUS[state];
        } else {
            passwordText.innerHTML = "";
        }
    });


    function checkName() {
        let name = document.getElementById(NAME_ID);
        let letters = /^[A-Za-z]+$/;

        if (!name.value.match(letters)) {
            let nameAlert = document.createElement("div");
            let warningText = document.createTextNode("Imię musi składać się z samych liter.");
            nameAlert.setAttribute("class", "alert alert-danger");
            nameAlert.setAttribute("role", "alert");
            nameAlert.appendChild(warningText);
            alertDiv.appendChild(nameAlert);
            return false;
        }
        return true;
    }

    function checkSurname() {
        let surname = document.getElementById(SURNAME_ID);
        let letters = /^[A-Za-z]+$/;

        if (!surname.value.match(letters)) {
            let surnameAlert = document.createElement("div");
            let warningText = document.createTextNode("Nazwisko musi składać się z samych liter.");
            surnameAlert.setAttribute("class", "alert alert-danger");
            surnameAlert.setAttribute("role", "alert");
            surnameAlert.appendChild(warningText);
            alertDiv.appendChild(surnameAlert);
            return false;
        }
        return true;
    }

    function checkEmail() {
        let email = document.getElementById(EMAIL_ID);
        let emailCharacters = /[^@]+@[^@]+\.[^@]+/;

        if (!email.value.match(emailCharacters)) {
            let emailAlert = document.createElement("div");
            let warningText = document.createTextNode("Niepoprawny format adresu e-mail.");
            emailAlert.setAttribute("class", "alert alert-danger");
            emailAlert.setAttribute("role", "alert");
            emailAlert.appendChild(warningText);
            alertDiv.appendChild(emailAlert);
            return false;
        }
        return true;
    }

    function checkLogin() {
        let login = document.getElementById(LOGIN_ID);
        let alphaNumCharacters = /^[a-z0-9]+$/i;

        if (!login.value.match(alphaNumCharacters)) {
            let loginAlert = document.createElement("div");
            let warningText = document.createTextNode("Login musi składać się ze znaków alfanumerycznych.");
            loginAlert.setAttribute("class", "alert alert-danger");
            loginAlert.setAttribute("role", "alert");
            loginAlert.appendChild(warningText);
            alertDiv.appendChild(loginAlert);
            return false;
        }

        if (login.value.length < 5) {
            let loginAlert = document.createElement("div");
            let warningText = document.createTextNode("Login musi składać się przynajmniej z 5 znaków.");
            loginAlert.setAttribute("class", "alert alert-danger");
            loginAlert.setAttribute("role", "alert");
            loginAlert.appendChild(warningText);
            alertDiv.appendChild(loginAlert);
            return false;
        }
        return true;
    }

    function checkPassword() {
        let password = document.getElementById(PASSWORD_ID);
        
        if (password.value.length < 8) {
            let loginAlert = document.createElement("div");
            let warningText = document.createTextNode("Hasło musi składać się przynajmniej z 8 znaków.");
            loginAlert.setAttribute("class", "alert alert-danger");
            loginAlert.setAttribute("role", "alert");
            loginAlert.appendChild(warningText);
            alertDiv.appendChild(loginAlert);
            return false;
        }

        if (password.value.match(/[a-z]+/) && password.value.match(/[A-Z]+/) 
            && password.value.match(/[0-9]+/) && password.value.match(/[!@#$%^&*]+/)) {
            return true;
        } else {
            let loginAlert = document.createElement("div");
            let warningText = document.createTextNode("Hasło musi zawierać dużą i małą literę, cyfrę oraz znak specjalny.");
            loginAlert.setAttribute("class", "alert alert-danger");
            loginAlert.setAttribute("role", "alert");
            loginAlert.appendChild(warningText);
            alertDiv.appendChild(loginAlert);
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

    function countEntropy(password) {
        let stat = {};

        for (let i = 0; i < password.length; i++) {
            let m = password.charAt(i);
            if (stat.hasOwnProperty(m)) {
                stat[m] += 1;
            } else {
                stat[m] = 1;
            }
        }
        
        let H = 0.0;
        for (let i = 0; i < Object.keys(stat).length; i++) {
            let pi = Object.values(stat)[i]/password.length;
            H = H - pi*Math.log2(pi);
        }
        console.log(H)
        return H;
    }

});