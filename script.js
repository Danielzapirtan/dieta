let mancaruriList = [];
let reteteList = [];
let regimuriList = [];
let czaList = [];
let laList = [];

const app = document.createElement("div");
app.id = "app";
document.body.appendChild(app);

const tabs = document.createElement("select");
tabs.id = "tabs";
tabs.innerHTML = ``;
tabLabels = [
  "retetar",
  "regimuri",
  "cza",
  "la"
];
tabLabels.forEach((label, index) => {
  const tab = document.createElement("option");
  tab.classList.add("tab");
  tab.name = label;
  tab.textContent = label;
  tabs.appendChild(tab);
});
tabs.selectedIndex = 0;
app.appendChild(tabs);

const retetar = document.createElement("div");
retetar.id = "retetar";
retetar.innerHTML = ``;
app.appendChild(retetar);
const retetarMenu = document.createElement("select");
const rmLabels = [
  "operatii CRUD mancaruri",
  "Selecteaza mancare",
  "operatii CRUD alimente"
];
rmLabels.forEach(label1 => {
  const rmItem = document.createElement("option");
  rmItem.name = label1;
  rmItem.textContent = label1;
  retetarMenu.appendChild(rmItem);
});
retetar.appendChild(retetarMenu);

const regimuri = document.createElement("div");
regimuri.id = "regimuri";
regimuri.innerHTML = `Placeholder pentru regimuri tab`;
app.appendChild(regimuri);

const cza = document.createElement("div");
cza.id = "cza";
cza.innerHTML = `Placeholder pentru cza tab`;
app.appendChild(cza);

const la = document.createElement("div");
la.id = "la";
la.innerHTML = `Placeholder pentru la tab`;
app.appendChild(la);

tabs.addEventListener('change', (event) => {
  retetar.classList.add('hidden');
  regimuri.classList.add('hidden');
  cza.classList.add('hidden');
  la.classList.add('hidden');
  switch (event.target.selectedIndex) {
    case 0:
      retetar.classList.remove('hidden');
      break;
    case 1:
      regimuri.classList.remove('hidden');
      break;
    case 2:
      cza.classList.remove('hidden');
      break;
    default:
      la.classList.remove('hidden');
  }
});

