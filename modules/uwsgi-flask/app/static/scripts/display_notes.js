document.addEventListener('DOMContentLoaded', function (event) {
    
    const GET = "GET";
    const URL = "https://localhost/";
    
    let HTTP_STATUS = {OK: 200, BAD_REQUEST: 400};

    getPublicNotes();
    getTitlePrivateNotes();

    function getPublicNotes() {
        let publicNotesURL = URL + "notes";

        let publicNotesParams = {
            method: GET,
            redirect: "follow"
        };

        fetch(publicNotesURL, publicNotesParams)
            .then(response => getResponseData(response))
            .then(response => displayPublicNotes(response))
    }

    function getTitlePrivateNotes() {
        let privateNotesURL = URL + "encrypted_notes";

        let privateNotesParams = {
            method: GET,
            redirect: "follow"
        };

        fetch(privateNotesURL, privateNotesParams)
            .then(response => getResponseData(response))
            .then(response => displayPrivateNotes(response))
    }

    function getResponseData(response) {
        let status = response.status;

        if (status === HTTP_STATUS.OK) {
            return response.json()
        } else {
            console.error("Response status code: " + response.status);
            throw "Unexcepted response status: " + response.status;
        }
    }

    function displayPublicNotes(response) {
        let publicNotes = response;
        let publicNotesDiv = document.getElementById("public-notes");
        let numberOfNotes = publicNotes.length;

        if(numberOfNotes != 0) {
            let tableElem = document.createElement("table");
            tableElem.setAttribute("class", "table table-striped")
            tableElem.setAttribute("id", "public-notes-table");
            let tableHeadElem = document.createElement("thead");
            let tableBodyElem = document.createElement("tbody");
            let trHead = document.createElement("tr");
            let th1 = document.createElement("th");
            th1.setAttribute("scope", "col");
            th1Text = document.createTextNode("Użytkownik");
            th1.appendChild(th1Text);
            let th2 = document.createElement("th");
            th2.setAttribute("scope", "col");
            th2Text = document.createTextNode("Tytuł");
            th2.appendChild(th2Text);
            let th3 = document.createElement("th");
            th3.setAttribute("scope", "col");
            th3Text = document.createTextNode("Treść");
            th3.appendChild(th3Text);
            trHead.appendChild(th1);
            trHead.appendChild(th2);
            trHead.appendChild(th3);
            tableHeadElem.appendChild(trHead);
            
            for (let i = 0; i < response.length; i++) {
                let row = document.createElement("tr");
                
                let cell1 = document.createElement("td");
                let text1 = document.createTextNode(publicNotes[i].login);
                cell1.appendChild(text1);

                let cell2 = document.createElement("td");
                let text2 = document.createTextNode(publicNotes[i].title);
                cell2.appendChild(text2);

                let cell3 = document.createElement("td");
                let text3 = document.createTextNode(publicNotes[i].note);
                cell3.appendChild(text3);
                
                row.appendChild(cell1);
                row.appendChild(cell2);
                row.appendChild(cell3);

                tableBodyElem.appendChild(row);
            }

            tableElem.appendChild(tableHeadElem);
            tableElem.appendChild(tableBodyElem);
            publicNotesDiv.appendChild(tableElem);



        } else {
            let lackOfPublicNotesElem = document.createElement('h5');
            let lackOfPublicNotesContent = document.createTextNode("Brak publicznych notatek!");
            lackOfPublicNotesElem.setAttribute("id", "lackOfPublicNotes");
            lackOfPublicNotesElem.setAttribute("class", "text-center");
            lackOfPublicNotesElem.appendChild(lackOfPublicNotesContent);
            publicNotesDiv.appendChild(lackOfPublicNotesElem);
        }

    }

    function displayPrivateNotes(response) {
        let privateNotes = response;
        let privateNotesDiv = document.getElementById("private-notes");
        let numberOfNotes = privateNotes.length;

        if(numberOfNotes != 0) {
            let tableElem = document.createElement("table");
            tableElem.setAttribute("class", "table table-striped")
            tableElem.setAttribute("id", "private-notes-table");
            let tableHeadElem = document.createElement("thead");
            let tableBodyElem = document.createElement("tbody");
            let trHead = document.createElement("tr");
            let th1 = document.createElement("th");
            th1.setAttribute("scope", "col");
            th1Text = document.createTextNode("ID");
            th1.appendChild(th1Text);
            let th2 = document.createElement("th");
            th2.setAttribute("scope", "col");
            th2Text = document.createTextNode("Tytuł");
            th2.appendChild(th2Text);
            trHead.appendChild(th1);
            trHead.appendChild(th2);
            tableHeadElem.appendChild(trHead);
            
            for (let i = 0; i < response.length; i++) {
                let row = document.createElement("tr");
                
                let cell1 = document.createElement("td");
                let text1 = document.createTextNode(i+1);
                cell1.appendChild(text1);

                let cell2 = document.createElement("td");
                let text2 = document.createTextNode(privateNotes[i].title);
                cell2.appendChild(text2);
                
                row.appendChild(cell1);
                row.appendChild(cell2);

                tableBodyElem.appendChild(row);
            }

            tableElem.appendChild(tableHeadElem);
            tableElem.appendChild(tableBodyElem);
            privateNotesDiv.appendChild(tableElem);



        } else {
            let lackOfPrivateNotesElem = document.createElement('h5');
            let lackOfPrivateNotesContent = document.createTextNode("Brak prywatnych notatek!");
            lackOfPrivateNotesElem.setAttribute("id", "lackOfPrivateNotes");
            lackOfPrivateNotesElem.setAttribute("class", "text-center");
            lackOfPrivateNotesElem.appendChild(lackOfPrivateNotesContent);
            privateNotesDiv.appendChild(lackOfPrivateNotesElem);
        }

    }
    

});