const form = document.getElementById("form-tarea");
const listaTareas = document.getElementById("lista-tareas");
const alerta = document.getElementById("alerta");
const inputId = document.getElementById("tarea-id");
const inputNombre = document.getElementById("nombre");
const inputDescripcion = document.getElementById("descripcion");
const selectPrioridad = document.getElementById("prioridad");
const selectEstado = document.getElementById("estado");
const formTitulo = document.getElementById("form-titulo");
const btnCancelar = document.getElementById("btn-cancelar");

function mostrarAlerta(texto, tipo = "ok") {
  alerta.textContent = texto;
  alerta.className = `alerta ${tipo}`;
  setTimeout(() => { alerta.className = "alerta oculto"; }, 3200);
}

async function cargarTareas() {
  const res = await fetch("/api/tareas");
  const tareas = await res.json();

  if (tareas.length === 0) {
    listaTareas.innerHTML = "<p>No hay tareas registradas todavía.</p>";
    return;
  }

  listaTareas.innerHTML = tareas.map(t => `
    <div class="tarea-item">
      <div class="tarea-info">
        <h3>${escaparHTML(t.nombre)}</h3>
        <p>${escaparHTML(t.descripcion || "Sin descripción")}</p>
        <div class="badges">
          <span class="badge prio-${t.prioridad}">Prioridad: ${t.prioridad}</span>
          <span class="badge est-${t.estado.split(" ")[0]}">Estado: ${t.estado}</span>
        </div>
      </div>
      <div class="tarea-controles">
        <select onchange="cambiarEstado(${t.id}, this.value)" aria-label="Cambiar estado">
          <option value="Pendiente" ${t.estado === "Pendiente" ? "selected" : ""}>Pendiente</option>
          <option value="En proceso" ${t.estado === "En proceso" ? "selected" : ""}>En proceso</option>
          <option value="Terminada" ${t.estado === "Terminada" ? "selected" : ""}>Terminada</option>
        </select>
        <div class="botones-fila">
          <button class="btn-editar" onclick='prepararEdicion(${JSON.stringify(t)})'>Editar</button>
          <button class="btn-eliminar" onclick="eliminarTarea(${t.id})">Eliminar</button>
        </div>
      </div>
    </div>
  `).join("");
}

function escaparHTML(str) {
  return str.replace(/[&<>"']/g, m => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[m]));
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const payload = {
    nombre: inputNombre.value,
    descripcion: inputDescripcion.value,
    prioridad: selectPrioridad.value,
    estado: selectEstado.value
  };

  const id = inputId.value;
  const url = id ? `/api/tareas/${id}` : "/api/tareas";
  const method = id ? "PUT" : "POST";

  const res = await fetch(url, {
    method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  const data = await res.json();
  if (!res.ok) {
    mostrarAlerta(data.error || "Ocurrió un error", "err");
    return;
  }

  mostrarAlerta(data.mensaje, "ok");
  resetearFormulario();
  cargarTareas();
});

function prepararEdicion(tarea) {
  inputId.value = tarea.id;
  inputNombre.value = tarea.nombre;
  inputDescripcion.value = tarea.descripcion;
  selectPrioridad.value = tarea.prioridad;
  selectEstado.value = tarea.estado;
  formTitulo.textContent = `Editando Tarea #${tarea.id}`;
  btnCancelar.classList.remove("oculto");
}

function resetearFormulario() {
  form.reset();
  inputId.value = "";
  formTitulo.textContent = "Nueva Tarea";
  btnCancelar.classList.add("oculto");
}

btnCancelar.addEventListener("click", resetearFormulario);

async function cambiarEstado(id, nuevoEstado) {
  const res = await fetch(`/api/tareas/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ estado: nuevoEstado })
  });
  const data = await res.json();
  if (res.ok) {
    mostrarAlerta(data.mensaje, "ok");
    cargarTareas();
  }
}

async function eliminarTarea(id) {
  const res = await fetch(`/api/tareas/${id}`, { method: "DELETE" });
  const data = await res.json();
  if (res.ok) {
    mostrarAlerta(data.mensaje, "ok");
    cargarTareas();
  }
}

cargarTareas();