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
