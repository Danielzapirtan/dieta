const app = document.createElement("div");
app.id = "app";
document.body.appendChild(app);

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

regimuri.classList.add('hidden');

