const docID = document.querySelector("#id");
const docName = document.querySelector("#name");
const docServer = document.querySelector("#server");
const docCheckType = document.querySelector("#check-type");
const docCheckCat = document.querySelector("#check-category");
const docService = document.querySelector("#service");
const docURL = document.querySelector("#url");
const docProgram = document.querySelector("#program");
const docInstanceCount = document.querySelector("#instance-count");
const docDatabase = document.querySelector("#database");
const docCompany = document.querySelector("#company");
const docBU = document.querySelector("#business-unit");
const docSystem = document.querySelector("#system");
const docJobID = document.querySelector("#job-id");
const docObjectType = document.querySelector("#object-type");
const docObjectID = document.querySelector("#object-id");

const docNextBtn = document.querySelector("#next-check-btn");
const docPrevBtn = document.querySelector("#prev-check-btn");
const docSaveBtn = document.querySelector("#save-btn");

docCheckType.addEventListener("change", e => {
    showFieldsFor(docCheckType.value);
});

docNextBtn.addEventListener("click", e => {
    window.location.href = `${parseInt(docID.value) + 1}`;
});

docPrevBtn.addEventListener("click", e => {
    window.location.href = `${parseInt(docID.value) - 1}`;
});

docSaveBtn.addEventListener("click", async e => {
    const response = await fetch("save", {
        method: 'POST',
        body: JSON.stringify(collectData())
    });
    const data = await response.json();
    console.log(data)
});

const showFieldsFor = (value) => {
    console.log(value);
    switch (value) {
        case "JOB": {
            hideHidables();
            unhide(docDatabase);
            unhide(docObjectType);
            unhide(docObjectID);
            break;
        }
        case "SERVICE": {
            hideHidables();
            unhide(docService);
            break;
        }
        case "PROGRAM": {
            hideHidables();
            unhide(docProgram);
            unhide(docInstanceCount);
            break;
        }
        case "SSIS": {
            hideHidables();
            unhide(docJobID);
            break;
        }
        case "URL": {
            hideHidables();
            unhide(docURL);
            break;
        }
    }
}

const hideHidables = () => {
    let hidables = document.querySelectorAll(".hidable");
    for(let h of hidables) {
        if (!h.classList.contains("is-hidden"))
            h.classList.add("is-hidden")
    }
}

const unhide = (el) => {
    if (el.id === "object-type")
        el.parentElement.parentElement.parentElement.classList.remove("is-hidden");
    else
        el.parentElement.parentElement.classList.remove("is-hidden");
}

const collectData = () => {
    return {
        id: docID.value,
        name: docName.value,
        server: docServer.value,
        checkType: docCheckType.value,
        checkCategory: docCheckCat.value,
        service: docService.value,
        url: docURL.value,
        program: docProgram.value,
        instanceCount: docInstanceCount.value,
        database: docDatabase.value,
        company: docCompany.value,
        businessUnit: docBU.value,
        system: docSystem.value,
        jobID: docJobID.value,
        objectType: docObjectType.value,
        objectID: docObjectID.value
    }
}

window.addEventListener("load", e => {
    showFieldsFor(docCheckType.value);
});