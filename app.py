import os
import sqlite3
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)
DATABASE = os.environ.get("DATABASE_PATH", "taskmanager.db")

ESTADOS_VALIDOS = {"Pendiente", "En proceso", "Terminada"}
PRIORIDADES_VALIDAS = {"Alta", "Media", "Baja"}


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS tareas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT DEFAULT '',
            estado TEXT NOT NULL DEFAULT 'Pendiente',
            prioridad TEXT NOT NULL DEFAULT 'Media'
        )
        """
    )
    conn.commit()
    conn.close()


init_db()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "TaskManager-DevOps"}), 200


# RF02: Consultar tareas
@app.route("/api/tareas", methods=["GET"])
def obtener_tareas():
    conn = get_db_connection()
    tareas = conn.execute("SELECT * FROM tareas ORDER BY id DESC").fetchall()
    conn.close()
    return jsonify([dict(t) for t in tareas]), 200


# RF01: Registrar tareas
@app.route("/api/tareas", methods=["POST"])
def crear_tarea():
    datos = request.get_json(silent=True) or {}
    nombre = (datos.get("nombre") or "").strip()
    descripcion = (datos.get("descripcion") or "").strip()
    prioridad = (datos.get("prioridad") or "Media").strip()
    estado = (datos.get("estado") or "Pendiente").strip()

    if not nombre:
        return jsonify({"error": "El nombre de la tarea es obligatorio"}), 400
    if prioridad not in PRIORIDADES_VALIDAS:
        return jsonify({"error": "Prioridad inválida. Use Alta, Media o Baja"}), 400
    if estado not in ESTADOS_VALIDOS:
        return jsonify({"error": "Estado inválido"}), 400

    conn = get_db_connection()
    cursor = conn.execute(
        "INSERT INTO tareas (nombre, descripcion, estado, prioridad) VALUES (?, ?, ?, ?)",
        (nombre, descripcion, estado, prioridad),
    )
    tarea_id = cursor.lastrowid
    conn.commit()
    tarea = conn.execute("SELECT * FROM tareas WHERE id = ?", (tarea_id,)).fetchone()
    conn.close()

    return jsonify({"mensaje": "Tarea registrada correctamente", "tarea": dict(tarea)}), 201


# RF03, RF05 y RF06: Editar tarea, cambiar estado y asignar prioridad
@app.route("/api/tareas/<int:tarea_id>", methods=["PUT"])
def actualizar_tarea(tarea_id):
    datos = request.get_json(silent=True) or {}
    conn = get_db_connection()
    existente = conn.execute("SELECT * FROM tareas WHERE id = ?", (tarea_id,)).fetchone()

    if existente is None:
        conn.close()
        return jsonify({"error": "Tarea no encontrada"}), 404

    nombre = (datos.get("nombre") if "nombre" in datos else existente["nombre"] or "").strip()
    descripcion = (datos.get("descripcion") if "descripcion" in datos else existente["descripcion"] or "").strip()
    estado = (datos.get("estado") if "estado" in datos else existente["estado"]).strip()
    prioridad = (datos.get("prioridad") if "prioridad" in datos else existente["prioridad"]).strip()

    if not nombre:
        conn.close()
        return jsonify({"error": "El nombre de la tarea es obligatorio"}), 400
    if estado not in ESTADOS_VALIDOS:
        conn.close()
        return jsonify({"error": "Estado inválido"}), 400
    if prioridad not in PRIORIDADES_VALIDAS:
        conn.close()
        return jsonify({"error": "Prioridad inválida"}), 400

    conn.execute(
        """
        UPDATE tareas
        SET nombre = ?, descripcion = ?, estado = ?, prioridad = ?
        WHERE id = ?
        """,
        (nombre, descripcion, estado, prioridad, tarea_id),
    )
    conn.commit()
    actualizada = conn.execute("SELECT * FROM tareas WHERE id = ?", (tarea_id,)).fetchone()
    conn.close()

    return jsonify({"mensaje": "Tarea actualizada correctamente", "tarea": dict(actualizada)}), 200


# RF04: Eliminar tareas
@app.route("/api/tareas/<int:tarea_id>", methods=["DELETE"])
def eliminar_tarea(tarea_id):
    conn = get_db_connection()
    existente = conn.execute("SELECT * FROM tareas WHERE id = ?", (tarea_id,)).fetchone()

    if existente is None:
        conn.close()
        return jsonify({"error": "Tarea no encontrada"}), 404

    conn.execute("DELETE FROM tareas WHERE id = ?", (tarea_id,))
    conn.commit()
    conn.close()
    return jsonify({"mensaje": "Tarea eliminada correctamente"}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)