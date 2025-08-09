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
tabLabels.forEach(label => {
  const tab = document.createElement("option");
  tab.classList.add("tab");
  tab.name = label;
  tab.textContent = label;
  tabs.appendChild(tab);
});
app.appendChild(tabs);

const retetar = document.createElement("div");
retetar.id = "retetar";
retetar.innerHTML = `Hello retetar`;
app.appendChild(retetar);

const regimuri = document.createElement("div");
regimuri.id = "regimuri";
regimuri.innerHTML = `Hello regimuri`;
app.appendChild(regimuri);

const cza = document.createElement("div");
cza.id = "cza";
cza.innerHTML = `Hello cza`;
app.appendChild(cza);

const la = document.createElement("div");
la.id = "la";
la.innerHTML = `Hello la`;
app.appendChild(la);

