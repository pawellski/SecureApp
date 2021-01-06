document.addEventListener('DOMContentLoaded', function (event) {
    
    const POST = "POST";
    const URL = "https://localhost/";
    
    const EMAIL_ID = "email";
    
    let HTTP_STATUS = {OK: 200, BAD_REQUEST: 400};
    let restorePasswordForm = document.getElementById("restore-form")
    let alertDiv = document.getElementById("restore-alert")

    restorePasswordForm.addEventListener("submit", function (event) {
        event.preventDefault();
        alertDiv.innerHTML = "";
        if (checkEmail() == true) {
            submitRestorePasswordForm();
        }
    });

    function submitRestorePasswordForm() {
        let restoreUrl = URL + "restore";

        let restoreParams = {
            method: POST,
            body: new FormData(restorePasswordForm),
            redirect: "follow"
        };

        fetch(restoreUrl, restoreParams)
                .then(response => getRestoreResponseData(response))
                .then(response => displayRestoreAlert(response))
                .catch(err => {
                    console.log("Caught error: " + err);
                });
    }

    function getRestoreResponseData(response) {
        let status = response.status;

        if (status === HTTP_STATUS.OK || status === HTTP_STATUS.BAD_REQUEST) {
            return response.json();
        } else {
            console.error("Response status code: " + response.status);
            throw "Unexpected response status: " + response.status;
        }
    }

    function displayRestoreAlert(response) {
        alertDiv.innerHTML = "";
        if (response.send_message == "Accept") {
            let successAlert = document.createElement("div");
            let successText = document.createTextNode("Wysłano wiadomość pomyślnie.");
            successAlert.setAttribute("class", "alert alert-success");
            successAlert.setAttribute("role", "alert");
            successAlert.appendChild(successText);
            alertDiv.appendChild(successAlert);
        } else {
            let dangerAlert = document.createElement("div");
            let dangerText = document.createTextNode("Niepoprawny adres e-mail.");
            dangerAlert.setAttribute("class", "alert alert-danger");
            dangerAlert.setAttribute("role", "alert");
            dangerAlert.appendChild(dangerText);
            alertDiv.appendChild(dangerAlert);
        }
    }

    function checkEmail() {
        let email = document.getElementById(EMAIL_ID);
        let emailCharacters = /[^@]+@[^@]+\.[^@]+/;
        alertDiv.innerHTML = "";
        if (!email.value.match(emailCharacters)) {
            let dangerAlert = document.createElement("div");
            let dangerText = document.createTextNode("Niepoprawny adres e-mail.");
            dangerAlert.setAttribute("class", "alert alert-danger");
            dangerAlert.setAttribute("role", "alert");
            dangerAlert.appendChild(dangerText);
            alertDiv.appendChild(dangerAlert);
            return false;
        }
        return true;
    }
});