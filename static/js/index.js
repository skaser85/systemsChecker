const docChecksTable = document.querySelector("#checks-table");
const docCheckRows = docChecksTable.querySelectorAll("tr");

const docViewCheckBtn = document.querySelector("#view-edit-check-btn");
const docAddCheckBtn = document.querySelector("#add-check-btn");

let activeRow;

for (let row of docCheckRows) {
    row.addEventListener("click", e => {
        if (activeRow) {
            activeRow.classList.remove("is-selected");
        }
        activeRow = row;
        activeRow.classList.add("is-selected");
    });
}

const getActiveRowID = () => {
    return activeRow ? activeRow.children[0].innerText : 0;
}

docViewCheckBtn.addEventListener("click", e => {
    window.location.href = `edit/${getActiveRowID()}`;
});

docAddCheckBtn.addEventListener("click", e => {
    window.location.href = "add";
})