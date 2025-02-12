import fetch from "node-fetch";

const csvUrl = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQe997zmYQN79SbSc5uMuV85f7CrAUr0Jiqa5-oXTDqYNkE-marAU_0OC3gyhF8HL48hz1thkW4tCnf/pub?gid=0&single=true&output=csv";

async function fetchCSV() {
    const response = await fetch(csvUrl);
    const csvText = await response.text();
    console.log(csvText);
}

fetchCSV();
