document.addEventListener('DOMContentLoaded', function (event) {
    
    const GET = "GET";
    const URL = "https://localhost/";
    
    let HTTP_STATUS = {OK: 200, BAD_REQUEST: 400, NOT_FOUND: 404};

    getFiles();


    function getFiles() {
        let filesURL = URL + "files";

        let filesParams = {
            method: GET,
            redirect: "follow"
        };

        fetch(filesURL, filesParams)
            .then(response => getResponseData(response))
            .then(response => displayFiles(response))
    }

    function getResponseData(response) {
        let status = response.status;

        if (status === HTTP_STATUS.OK || status === HTTP_STATUS.BAD_REQUEST || status === HTTP_STATUS.NOT_FOUND) {
            return response.json()
        } else {
            console.error("Response status code: " + response.status);
            throw "Unexcepted response status: " + response.status;
        }
    }

    function displayFiles(response) {
        let files = response;
        let filesDiv = document.getElementById("user-files");
        let numberOfFiles = files.length;

        if(numberOfFiles != 0) {
            let tableElem = document.createElement("table");
            tableElem.setAttribute("class", "table table-striped")
            tableElem.setAttribute("id", "files-table");
            let tableHeadElem = document.createElement("thead");
            let tableBodyElem = document.createElement("tbody");
            let trHead = document.createElement("tr");
            let th1 = document.createElement("th");
            th1.setAttribute("scope", "col");
            th1Text = document.createTextNode("Nazwa pliku");
            th1.appendChild(th1Text);
            let th2 = document.createElement("th");
            th2.setAttribute("id", "downloadCol");
            th2.setAttribute("scope", "col");
            th2Text = document.createTextNode("Pobierz");
            th2.appendChild(th2Text);
            trHead.appendChild(th1);
            trHead.appendChild(th2);
            tableHeadElem.appendChild(trHead);
            
            for (let i = 0; i < files.length; i++) {
                let row = document.createElement("tr");
                
                let cell1 = document.createElement("td");
                let text1 = document.createTextNode(files[i]);
                cell1.appendChild(text1);

                let cell2 = document.createElement("td");
                let aElem = document.createElement("a")
                let file = files[i] + '';
                let link = URL + "download_file/" + file.split('.')[0];
                aElem.setAttribute("href", link)
                let text2 = document.createTextNode("Pobierz");
                aElem.appendChild(text2)
                cell2.appendChild(aElem);
                
                row.appendChild(cell1);
                row.appendChild(cell2);

                tableBodyElem.appendChild(row);
            }

            tableElem.appendChild(tableHeadElem);
            tableElem.appendChild(tableBodyElem);
            filesDiv.appendChild(tableElem);

        } else {
            let lackOfFilesElem = document.createElement('h5');
            let lackOfFilesContent = document.createTextNode("Brak plików!");
            lackOfFilesElem.setAttribute("id", "lackOfFiles");
            lackOfFilesElem.setAttribute("class", "text-center");
            lackOfFilesElem.appendChild(lackOfFilesContent);
            filesDiv.appendChild(lackOfFilesElem);
        }

    }

});