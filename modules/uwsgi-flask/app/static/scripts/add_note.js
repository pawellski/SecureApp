document.addEventListener('DOMContentLoaded', function (event) {
    
    const POST = "POST";
    const URL = "https://localhost/";

    const TITLE_ID = "title-input";
    const NOTE_ID = "textarea-note";
    
    let HTTP_STATUS = {BAD_REQUEST: 400, OK: 200, CONFLICT: 409};
    let addNoteForm = document.getElementById("add-note-form");
    let selectNote = document.getElementById("select-note");
    let passwordField = document.getElementById("password-note");
    let alertDiv = document.getElementById("alert-div");
    
    addNoteForm.addEventListener("submit", function(e) {
        e.preventDefault();
        alertDiv.innerHTML = "";
        let c1 = checkTitle();
        let c2 = checkNote();

        if (c1 == true && c2 == true) {
            submitAddNoteForm();
        }
    });

    function submitAddNoteForm() {
        let addNoteUrl = URL + "add_note";

        let addNoteParams = {
            method: POST,
            body: new FormData(addNoteForm),
            redirect: "follow"
        };

        fetch(addNoteUrl, addNoteParams)
                .then(response => getAddNoteResponseData(response))
                .then(response => displayInformation(response))
                .catch(err => {
                    console.log("Caught error: " + err);
                });
    }

    function getAddNoteResponseData(response) {
        let status = response.status;

        if (status === HTTP_STATUS.OK || status === HTTP_STATUS.BAD_REQUEST || status === HTTP_STATUS.CONFLICT) {
            return response.json();
        } else {
            console.error("Response status code: " + response.status);
            throw "Unexpected response status: " + response.status;
        }
    }

    function displayInformation(response) {
        if (response.add_note == "Correct") {
            addNoteForm.reset();
            passwordField.disabled = false;
            let successAlert = document.createElement("div");
            let successText = document.createTextNode("Notatka została dodana pomyślnie.");
            successAlert.setAttribute("class", "alert alert-success");
            successAlert.setAttribute("role", "alert");
            successAlert.appendChild(successText);
            alertDiv.appendChild(successAlert);
        }
        else if (response.add_note == "Already title exists.") {
            let titleAlert = document.createElement("div");
            let warningText = document.createTextNode("Notatka o podanym tytule istnieje.");
            titleAlert.setAttribute("class", "alert alert-warning");
            titleAlert.setAttribute("role", "alert");
            titleAlert.appendChild(warningText);
            alertDiv.appendChild(titleAlert);
        }
    }

    selectNote.addEventListener("change", function(event) {
        console.log(selectNote.value);
        let form = new FormData(addNoteForm);
        console.log(form);
        if (selectNote.value == "Szyfrowana") {
            passwordField.disabled = false;
        } else {
            passwordField.value = "";
            passwordField.disabled = true;
        }
    });

    function checkTitle() {
        let title = document.getElementById(TITLE_ID);
        let alphaNumCharacters = /^[a-z0-9]+$/i;
        if (!title.value.replaceAll(" ", "").match(alphaNumCharacters)) {
            let titleAlert = document.createElement("div");
            let warningText = document.createTextNode("Tytuł musi składać się ze znaków alfanumerycznych.");
            titleAlert.setAttribute("class", "alert alert-danger");
            titleAlert.setAttribute("role", "alert");
            titleAlert.appendChild(warningText);
            alertDiv.appendChild(titleAlert);
            return false;
        }
        return true;
    }

    function checkNote() {
        let noteField = document.getElementById(NOTE_ID);
        chars = "";
        if (noteField.value.includes("--")) {
            chars = "--";
        }
        if (noteField.value.includes("'")) {
            chars = chars + ", '";
        }
        if (noteField.value.includes("/*")) {
            chars = chars + ", /*";
        }
        if (noteField.value.includes("#")) {
            chars = chars + ", #";
        }
        if (noteField.value.includes(";")) {
            chars = chars + ", ;";
        }

        if (chars !== "") {
            let noteAlert = document.createElement("div");
            let warningText = document.createTextNode("Notatka zawiera niedozwolone znaki: " + chars);
            noteAlert.setAttribute("class", "alert alert-danger");
            noteAlert.setAttribute("role", "alert");
            noteAlert.appendChild(warningText);
            alertDiv.appendChild(noteAlert);
            return false;
        }
        return true;
    }

    


});