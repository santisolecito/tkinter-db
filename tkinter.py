import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import Error

# ─────────────────────────────────────────
#  CONFIGURACIÓN DE CONEXIÓN
# ─────────────────────────────────────────
DB_CONFIG = {
    "host":     "localhost",
    "port":     3306,
    "user":     "root",
    "password": "",
    "database": "agrocontrol"
}

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

def ejecutar(sql, params=(), fetch=False):
    try:
        conn = get_connection()
        # stored_results=True permite consumir múltiples resultados de un CALL
        cur  = conn.cursor()
        cur.execute(sql, params)
        if fetch:
            result = cur.fetchall()
            col_names = [d[0] for d in cur.description] if cur.description else []
            # Consumir resultados pendientes
            while conn.unread_result:
                cur.fetchall()
            cur.close(); conn.close()
            return result, col_names
        # Consumir todos los SELECT que devuelve el procedimiento
        while True:
            try:
                cur.fetchall()
            except Exception:
                pass
            if not cur.nextset():
                break
        conn.commit()
        cur.close(); conn.close()
        return True
    except Error as e:
        messagebox.showerror("Error de Base de Datos", str(e))
        return None

# ─────────────────────────────────────────
#  VENTANA PRINCIPAL
# ─────────────────────────────────────────
root = tk.Tk()
root.geometry("1400x800")
root.minsize(1100, 650)
root.title("AgroControl - Campos Fértiles S.A.")
root.configure(bg="#f0f4f0")

style = ttk.Style()
style.theme_use("clam")
style.configure("TNotebook", background="#2d5a27", tabmargins=[2, 5, 2, 0])
style.configure("TNotebook.Tab", background="#4a7c43", foreground="white",
                padding=[12, 6], font=("Segoe UI", 10, "bold"))
style.map("TNotebook.Tab",
          background=[("selected", "#f0f4f0")],
          foreground=[("selected", "#2d5a27")])
style.configure("TFrame", background="#f0f4f0")
style.configure("Treeview", font=("Segoe UI", 10), rowheight=26)
style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"),
                background="#2d5a27", foreground="white")
style.map("Treeview", background=[("selected", "#4a7c43")],
          foreground=[("selected", "white")])

header = tk.Frame(root, bg="#2d5a27", height=60)
header.pack(fill="x")
header.pack_propagate(False)
tk.Label(header, text="🌿 AGROCONTROL — Campos Fértiles S.A.",
         font=("Segoe UI", 16, "bold"), bg="#2d5a27", fg="white"
         ).pack(side="left", padx=20, pady=12)

conn_label = tk.Label(header, font=("Segoe UI", 10), bg="#2d5a27")
conn_label.pack(side="right", padx=20)
try:
    _test = get_connection(); _test.close()
    conn_label.config(text="🟢 Conectado a agrocontrol", fg="#90EE90")
except:
    conn_label.config(text="🔴 Sin conexión a BD", fg="#FF6B6B")

notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill="both", padx=10, pady=10)

tab_fincas     = ttk.Frame(notebook)
tab_cultivos   = ttk.Frame(notebook)
tab_insumos    = ttk.Frame(notebook)
tab_maquinaria = ttk.Frame(notebook)
tab_empleados  = ttk.Frame(notebook)
tab_cosechas   = ttk.Frame(notebook)
tab_clientes   = ttk.Frame(notebook)

notebook.add(tab_fincas,     text="  Fincas  ")
notebook.add(tab_cultivos,   text="  Cultivos  ")
notebook.add(tab_insumos,    text="  Insumos  ")
notebook.add(tab_maquinaria, text="  Maquinaria  ")
notebook.add(tab_empleados,  text="  Empleados  ")
notebook.add(tab_cosechas,   text="  Cosechas  ")
notebook.add(tab_clientes,   text="  Clientes  ")

LABEL_FONT = ("Segoe UI", 11)
ENTRY_FONT = ("Segoe UI", 11)
TITLE_FONT = ("Segoe UI", 14, "bold")
BG         = "#f0f4f0"

# ─────────────────────────────────────────
#  HELPERS DE FORMULARIO
# ─────────────────────────────────────────
def make_label_entry(parent, row, text, width=20):
    tk.Label(parent, text=text, font=LABEL_FONT, bg=BG, anchor="w"
             ).grid(row=row, column=0, sticky="w", padx=(0, 8), pady=5)
    e = tk.Entry(parent, width=width, font=ENTRY_FONT, relief="solid", bd=1)
    e.grid(row=row, column=1, sticky="w", pady=5)
    return e

def make_label_combo(parent, row, text, values, width=18):
    tk.Label(parent, text=text, font=LABEL_FONT, bg=BG, anchor="w"
             ).grid(row=row, column=0, sticky="w", padx=(0, 8), pady=5)
    c = ttk.Combobox(parent, values=values, width=width, font=ENTRY_FONT, state="readonly")
    c.grid(row=row, column=1, sticky="w", pady=5)
    return c

def clear_entries(entries):
    for w in entries.values():
        if isinstance(w, tk.Entry):    w.delete(0, tk.END)
        elif isinstance(w, tk.Text):   w.delete("1.0", tk.END)
        elif isinstance(w, ttk.Combobox): w.set("")

def get_val(entries, key):
    w = entries[key]
    if isinstance(w, tk.Text):
        return w.get("1.0", tk.END).strip()
    return w.get().strip()

def set_val(entries, key, value):
    w = entries[key]
    v = str(value) if value is not None else ""
    if isinstance(w, tk.Entry):
        w.delete(0, tk.END); w.insert(0, v)
    elif isinstance(w, tk.Text):
        w.delete("1.0", tk.END); w.insert("1.0", v)
    elif isinstance(w, ttk.Combobox):
        w.set(v)

# ─────────────────────────────────────────
#  CONSTRUCTOR DE PANEL (form + tabla)
# ─────────────────────────────────────────
def build_panel(tab, title, fields, color="#2d5a27"):
    btn_frame = tk.Frame(tab, bg=BG)
    btn_frame.pack(side="bottom", fill="x", pady=8)
    tk.Frame(tab, bg="#cccccc", height=1).pack(side="bottom", fill="x")

    paned = tk.PanedWindow(tab, orient="horizontal", bg=BG,
                           sashwidth=6, sashrelief="flat", bd=0)
    paned.pack(fill="both", expand=True)

    # Panel izquierdo — formulario
    left_outer = tk.Frame(paned, bg=BG)
    paned.add(left_outer, minsize=420)

    canvas    = tk.Canvas(left_outer, bg=BG, highlightthickness=0)
    scrollbar = ttk.Scrollbar(left_outer, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas, bg=BG)
    scroll_frame.bind("<Configure>",
                      lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    tk.Label(scroll_frame, text=title, font=TITLE_FONT, fg=color, bg=BG
             ).pack(pady=(14, 4))
    tk.Frame(scroll_frame, bg=color, height=2).pack(fill="x", padx=20, pady=(0, 10))

    form = tk.Frame(scroll_frame, bg=BG)
    form.pack(pady=4, anchor="w", padx=20)

    entries = {}
    for i, field in enumerate(fields):
        name, ftype, opts = field
        if ftype == "entry":
            entries[name] = make_label_entry(form, i, name + ":", 26)
        elif ftype == "combo":
            entries[name] = make_label_combo(form, i, name + ":", opts, 24)
        elif ftype == "text":
            tk.Label(form, text=name + ":", font=LABEL_FONT, bg=BG
                     ).grid(row=i, column=0, sticky="nw", padx=(0, 12), pady=6)
            t = tk.Text(form, width=26, height=4, font=ENTRY_FONT, relief="solid", bd=1)
            t.grid(row=i, column=1, sticky="w", pady=6)
            entries[name] = t

    # Panel derecho — tabla
    right = tk.Frame(paned, bg=BG)
    paned.add(right, minsize=500)

    search_bar = tk.Frame(right, bg=BG)
    search_bar.pack(fill="x", padx=12, pady=(14, 4))
    tk.Label(search_bar, text="🔍 Buscar:", font=("Segoe UI", 10, "bold"),
             bg=BG, fg="#2d5a27").pack(side="left")
    search_var = tk.StringVar()
    tk.Entry(search_bar, textvariable=search_var, font=("Segoe UI", 10),
             width=28, relief="solid", bd=1).pack(side="left", padx=8)
    tk.Label(search_bar, text="Registros:", font=("Segoe UI", 10),
             bg=BG, fg="#666").pack(side="right", padx=(0, 4))
    count_label = tk.Label(search_bar, text="0", font=("Segoe UI", 10, "bold"),
                           bg=BG, fg="#2d5a27")
    count_label.pack(side="right")

    tree_frame = tk.Frame(right, bg=BG)
    tree_frame.pack(fill="both", expand=True, padx=12, pady=(0, 8))
    tree = ttk.Treeview(tree_frame, show="headings", selectmode="browse")
    vsb  = ttk.Scrollbar(tree_frame, orient="vertical",   command=tree.yview)
    hsb  = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    tree.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    hsb.grid(row=1, column=0, sticky="ew")
    tree_frame.rowconfigure(0, weight=1)
    tree_frame.columnconfigure(0, weight=1)

    tree._count_label = count_label
    tree._search_var  = search_var

    # Posicionar la barra divisora DESPUÉS de agregar ambos paneles
    paned.update_idletasks()
    try:
        paned.sash_place(0, 430, 0)
    except Exception:
        pass

    return scroll_frame, entries, tree, search_var, btn_frame

def make_buttons(parent, save_cmd, update_cmd, delete_cmd, clear_cmd, refresh_cmd=None):
    frame = tk.Frame(parent, bg=BG)
    frame.pack(pady=14)
    buttons = [
        ("💾 Guardar",    "#4CAF50", save_cmd),
        ("✏️ Actualizar", "#2196F3", update_cmd),
        ("🗑️ Eliminar",  "#f44336", delete_cmd),
        ("🧹 Limpiar",   "#FF9800", clear_cmd),
    ]
    if refresh_cmd:
        buttons.append(("🔄 Actualizar lista", "#607D8B", refresh_cmd))
    for txt, bg, cmd in buttons:
        tk.Button(frame, text=txt, font=("Segoe UI", 10, "bold"), bg=bg, fg="white",
                  padx=10, pady=5, relief="flat", cursor="hand2",
                  command=cmd).pack(side="left", padx=4)

def load_tree(tree, sql, filter_text=""):
    result = ejecutar(sql, fetch=True)
    if result is None:
        return
    rows, cols = result
    tree["columns"] = cols
    for col in cols:
        tree.heading(col, text=col)
        tree.column(col, width=max(90, len(col)*10), minwidth=60)
    tree.delete(*tree.get_children())
    fl = filter_text.lower()
    count = 0
    for row in rows:
        values = [str(v) if v is not None else "" for v in row]
        if fl and not any(fl in v.lower() for v in values):
            continue
        tree.insert("", "end", values=values,
                    tags=("even" if count % 2 == 0 else "odd",))
        count += 1
    tree.tag_configure("even", background="#ffffff")
    tree.tag_configure("odd",  background="#eef4ee")
    tree._count_label.config(text=str(count))

def bind_search(tree, sql):
    def on_search(*_):
        load_tree(tree, sql, tree._search_var.get())
    tree._search_var.trace_add("write", on_search)

# ═══════════════════════════════════════════════════════════════
#  TAB FINCAS
#  SP usados: sp_insertar_finca · sp_actualizar_finca · sp_eliminar_finca
# ═══════════════════════════════════════════════════════════════
finca_fields = [
    ("Código Finca",        "entry", []),
    ("Nombre",              "entry", []),
    ("Ubicación",           "entry", []),
    ("Latitud",             "entry", []),
    ("Longitud",            "entry", []),
    ("Extensión (ha)",      "entry", []),
    ("Altitud (msnm)",      "entry", []),
    ("Temp. Promedio (°C)", "entry", []),
    ("Tipo de Suelo",       "combo", ["Franco","Arcilloso","Arenoso","Limoso","Franco-Arcilloso"]),
    ("Región",              "entry", []),
]
FINCA_SQL = "SELECT Finca_ID, Nombre, ubicacion, Hectareas, altitud, Temperatura, tipo_suelo, region FROM Fincas"
sf, ef, tree_f, sv_f, btn_f = build_panel(tab_fincas, "GESTIÓN DE FINCAS", finca_fields, "#2d5a27")

def finca_refresh():
    load_tree(tree_f, FINCA_SQL, sv_f.get())

def finca_on_select(event):
    sel = tree_f.selection()
    if not sel: return
    vals = tree_f.item(sel[0], "values")
    for k, v in zip(["Código Finca","Nombre","Ubicación","Extensión (ha)",
                      "Altitud (msnm)","Temp. Promedio (°C)","Tipo de Suelo","Región"], vals):
        set_val(ef, k, v)

tree_f.bind("<<TreeviewSelect>>", finca_on_select)
bind_search(tree_f, FINCA_SQL)

def finca_save():
    # CALL sp_insertar_finca(nombre, ubicacion, latitud, longitud, hectareas,
    #                        altitud, temperatura, tipo_suelo, region)
    params = (
        get_val(ef,"Nombre"),         get_val(ef,"Ubicación"),
        get_val(ef,"Latitud") or None, get_val(ef,"Longitud") or None,
        get_val(ef,"Extensión (ha)") or 0,
        get_val(ef,"Altitud (msnm)") or 0,
        get_val(ef,"Temp. Promedio (°C)") or 0,
        get_val(ef,"Tipo de Suelo"),  get_val(ef,"Región") or None,
    )
    if ejecutar("CALL sp_InsertFinca(%s,%s,%s,%s,%s,%s,%s,%s,%s)", params):
        messagebox.showinfo("Finca", "Finca guardada ✅")
        clear_entries(ef); finca_refresh()

def finca_update():
    fid = get_val(ef, "Código Finca")
    if not fid:
        messagebox.showwarning("Actualizar", "Selecciona una finca de la tabla."); return
    # CALL sp_actualizar_finca(id, nombre, ubicacion, latitud, longitud, hectareas,
    #                          altitud, temperatura, tipo_suelo, region)
    params = (
        fid,
        get_val(ef,"Nombre"),         get_val(ef,"Ubicación"),
        get_val(ef,"Latitud") or None, get_val(ef,"Longitud") or None,
        get_val(ef,"Extensión (ha)") or 0,
        get_val(ef,"Altitud (msnm)") or 0,
        get_val(ef,"Temp. Promedio (°C)") or 0,
        get_val(ef,"Tipo de Suelo"),  get_val(ef,"Región") or None,
    )
    if ejecutar("CALL sp_UpdateFinca(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", params):
        messagebox.showinfo("Finca", "Finca actualizada ✅"); finca_refresh()

def finca_delete():
    fid = get_val(ef, "Código Finca")
    if not fid:
        messagebox.showwarning("Eliminar", "Selecciona una finca de la tabla."); return
    if messagebox.askyesno("Confirmar", f"¿Eliminar finca ID {fid}?"):
        if ejecutar("CALL sp_DeleteFinca(%s)", (fid,)):
            messagebox.showinfo("Finca", "Finca eliminada ✅")
            clear_entries(ef); finca_refresh()

make_buttons(btn_f, finca_save, finca_update, finca_delete,
             lambda: clear_entries(ef), finca_refresh)
finca_refresh()

# ═══════════════════════════════════════════════════════════════
#  TAB CULTIVOS
#  SP usados: sp_insertar_cultivo · sp_actualizar_cultivo · sp_eliminar_cultivo
# ═══════════════════════════════════════════════════════════════
cultivo_fields = [
    ("Código Cultivo",        "entry", []),
    ("Nombre Científico",     "entry", []),
    ("Nombre Común",          "entry", []),
    ("Tiempo de Crecimiento", "entry", []),
    ("Temp. Óptima (°C)",     "entry", []),
    ("Req. Agua (mm/año)",    "entry", []),
]
CULTIVO_SQL = "SELECT cultivo_id, nombre_cientifico, nombre_comun, tiempo_crecimiento, temperatura_optima, agua FROM cultivos"
sc, ec, tree_c, sv_c, btn_c = build_panel(tab_cultivos, "GESTIÓN DE CULTIVOS", cultivo_fields, "#5a6e27")

def cultivo_refresh():
    load_tree(tree_c, CULTIVO_SQL, sv_c.get())

def cultivo_on_select(event):
    sel = tree_c.selection()
    if not sel: return
    vals = tree_c.item(sel[0], "values")
    for k, v in zip(["Código Cultivo","Nombre Científico","Nombre Común",
                      "Tiempo de Crecimiento","Temp. Óptima (°C)","Req. Agua (mm/año)"], vals):
        set_val(ec, k, v)

tree_c.bind("<<TreeviewSelect>>", cultivo_on_select)
bind_search(tree_c, CULTIVO_SQL)

def cultivo_save():
    # CALL sp_insertar_cultivo(nombre_cientifico, nombre_comun, tiempo, temperatura, agua)
    params = (
        get_val(ec,"Nombre Científico"), get_val(ec,"Nombre Común"),
        get_val(ec,"Tiempo de Crecimiento") or 0,
        get_val(ec,"Temp. Óptima (°C)") or 0,
        get_val(ec,"Req. Agua (mm/año)") or 0,
    )
    if ejecutar("CALL sp_InsertCultivo(%s,%s,%s,%s,%s)", params):
        messagebox.showinfo("Cultivo", "Cultivo guardado ✅")
        clear_entries(ec); cultivo_refresh()

def cultivo_update():
    cid = get_val(ec, "Código Cultivo")
    if not cid:
        messagebox.showwarning("Actualizar", "Selecciona un cultivo de la tabla."); return
    # CALL sp_actualizar_cultivo(id, nombre_cientifico, nombre_comun, tiempo, temperatura, agua)
    params = (
        cid,
        get_val(ec,"Nombre Científico"), get_val(ec,"Nombre Común"),
        get_val(ec,"Tiempo de Crecimiento") or 0,
        get_val(ec,"Temp. Óptima (°C)") or 0,
        get_val(ec,"Req. Agua (mm/año)") or 0,
    )
    if ejecutar("CALL sp_UpdateCultivo(%s,%s,%s,%s,%s,%s)", params):
        messagebox.showinfo("Cultivo", "Cultivo actualizado ✅"); cultivo_refresh()

def cultivo_delete():
    cid = get_val(ec, "Código Cultivo")
    if not cid:
        messagebox.showwarning("Eliminar", "Selecciona un cultivo de la tabla."); return
    if messagebox.askyesno("Confirmar", f"¿Eliminar cultivo ID {cid}?"):
        if ejecutar("CALL sp_DeleteCultivo(%s)", (cid,)):
            messagebox.showinfo("Cultivo", "Cultivo eliminado ✅")
            clear_entries(ec); cultivo_refresh()

make_buttons(btn_c, cultivo_save, cultivo_update, cultivo_delete,
             lambda: clear_entries(ec), cultivo_refresh)
cultivo_refresh()

# ═══════════════════════════════════════════════════════════════
#  TAB INSUMOS
#  SP usados: sp_insertar_insumo · sp_actualizar_insumo · sp_eliminar_insumo
# ═══════════════════════════════════════════════════════════════
insumo_fields = [
    ("Código Insumo",      "entry", []),
    ("Nombre Comercial",   "entry", []),
    ("Tipo",               "combo", ["Semilla","Fertilizante","Plaguicida","Herbicida","Fungicida","Otro"]),
    ("Unidad de Medida",   "combo", ["kg","litro","unidad","bulto","tonelada"]),
    ("Cantidad en Stock",  "entry", []),
    ("Ubicación Almacén",  "entry", []),
    ("Fecha de Caducidad", "entry", []),
    ("Precio Unitario",    "entry", []),
]
INSUMO_SQL = "SELECT Codigo_id, nombre_comercial, Tipo, unidad_medida, cantidad_stok, ubicacion, fecha_caducidad, precio FROM inventario"
si, ei, tree_i, sv_i, btn_i = build_panel(tab_insumos, "GESTIÓN DE INSUMOS", insumo_fields, "#7a5c1e")

def insumo_refresh():
    load_tree(tree_i, INSUMO_SQL, sv_i.get())

def insumo_on_select(event):
    sel = tree_i.selection()
    if not sel: return
    vals = tree_i.item(sel[0], "values")
    for k, v in zip(["Código Insumo","Nombre Comercial","Tipo","Unidad de Medida",
                      "Cantidad en Stock","Ubicación Almacén","Fecha de Caducidad","Precio Unitario"], vals):
        set_val(ei, k, v)

tree_i.bind("<<TreeviewSelect>>", insumo_on_select)
bind_search(tree_i, INSUMO_SQL)

def insumo_save():
    # CALL sp_insertar_insumo(nombre, tipo, unidad, ubicacion, cantidad, caducidad, precio)
    params = (
        get_val(ei,"Nombre Comercial"), get_val(ei,"Tipo"),
        get_val(ei,"Unidad de Medida"), get_val(ei,"Ubicación Almacén"),
        get_val(ei,"Cantidad en Stock") or 0,
        get_val(ei,"Fecha de Caducidad") or None,
        get_val(ei,"Precio Unitario") or 0,
    )
    if ejecutar("CALL sp_InsertInsumo(%s,%s,%s,%s,%s,%s,%s)", params):
        messagebox.showinfo("Insumo", "Insumo guardado ✅")
        clear_entries(ei); insumo_refresh()

def insumo_update():
    iid = get_val(ei, "Código Insumo")
    if not iid:
        messagebox.showwarning("Actualizar", "Selecciona un insumo de la tabla."); return
    # CALL sp_actualizar_insumo(id, nombre, tipo, unidad, ubicacion, cantidad, caducidad, precio)
    params = (
        iid,
        get_val(ei,"Nombre Comercial"), get_val(ei,"Tipo"),
        get_val(ei,"Unidad de Medida"), get_val(ei,"Ubicación Almacén"),
        get_val(ei,"Cantidad en Stock") or 0,
        get_val(ei,"Fecha de Caducidad") or None,
        get_val(ei,"Precio Unitario") or 0,
    )
    if ejecutar("CALL sp_UpdateInsumo(%s,%s,%s,%s,%s,%s,%s,%s)", params):
        messagebox.showinfo("Insumo", "Insumo actualizado ✅"); insumo_refresh()

def insumo_delete():
    iid = get_val(ei, "Código Insumo")
    if not iid:
        messagebox.showwarning("Eliminar", "Selecciona un insumo de la tabla."); return
    if messagebox.askyesno("Confirmar", f"¿Eliminar insumo ID {iid}?"):
        if ejecutar("CALL sp_DeleteInsumo(%s)", (iid,)):
            messagebox.showinfo("Insumo", "Insumo eliminado ✅")
            clear_entries(ei); insumo_refresh()

make_buttons(btn_i, insumo_save, insumo_update, insumo_delete,
             lambda: clear_entries(ei), insumo_refresh)
insumo_refresh()

# ═══════════════════════════════════════════════════════════════
#  TAB MAQUINARIA
#  SP usados: sp_insertar_maquinaria · sp_actualizar_maquinaria · sp_eliminar_maquinaria
# ═══════════════════════════════════════════════════════════════
maquinaria_fields = [
    ("Código Máquina",   "entry", []),
    ("Marca",            "entry", []),
    ("Modelo",           "entry", []),
    ("Año Fabricación",  "entry", []),
    ("Potencia (HP)",    "entry", []),
    ("Tipo Combustible", "combo", ["Diésel","Gasolina","Eléctrico","Gas"]),
    ("Horómetro (hrs)",  "entry", []),
    ("Estado Operativo", "combo", ["Operativa","En Mantenimiento","Fuera de Servicio"]),
]
MAQ_SQL = "SELECT codigo_maquina, marca, modelo, anio_fabricacion, potencia, tipo_combustible, horometro, estado FROM maquinaria"
sm, em, tree_m, sv_m, btn_m = build_panel(tab_maquinaria, "GESTIÓN DE MAQUINARIA", maquinaria_fields, "#3d5c7a")

def maq_refresh():
    load_tree(tree_m, MAQ_SQL, sv_m.get())

def maq_on_select(event):
    sel = tree_m.selection()
    if not sel: return
    vals = tree_m.item(sel[0], "values")
    for k, v in zip(["Código Máquina","Marca","Modelo","Año Fabricación",
                      "Potencia (HP)","Tipo Combustible","Horómetro (hrs)","Estado Operativo"], vals):
        set_val(em, k, v)

tree_m.bind("<<TreeviewSelect>>", maq_on_select)
bind_search(tree_m, MAQ_SQL)

def maq_save():
    # CALL sp_insertar_maquinaria(marca, modelo, anio, potencia, combustible, horometro, estado)
    params = (
        get_val(em,"Marca"), get_val(em,"Modelo"),
        get_val(em,"Año Fabricación") or 0,
        get_val(em,"Potencia (HP)") or 0,
        get_val(em,"Tipo Combustible"),
        get_val(em,"Horómetro (hrs)") or 0,
        get_val(em,"Estado Operativo"),
    )
    if ejecutar("CALL sp_InsertMaquinaria(%s,%s,%s,%s,%s,%s,%s)", params):
        messagebox.showinfo("Maquinaria", "Máquina guardada ✅")
        clear_entries(em); maq_refresh()

def maq_update():
    mid = get_val(em, "Código Máquina")
    if not mid:
        messagebox.showwarning("Actualizar", "Selecciona una máquina de la tabla."); return
    # CALL sp_actualizar_maquinaria(id, marca, modelo, anio, potencia, combustible, horometro, estado)
    params = (
        mid,
        get_val(em,"Marca"), get_val(em,"Modelo"),
        get_val(em,"Año Fabricación") or 0,
        get_val(em,"Potencia (HP)") or 0,
        get_val(em,"Tipo Combustible"),
        get_val(em,"Horómetro (hrs)") or 0,
        get_val(em,"Estado Operativo"),
    )
    if ejecutar("CALL sp_UpdateMaquinaria(%s,%s,%s,%s,%s,%s,%s,%s)", params):
        messagebox.showinfo("Maquinaria", "Máquina actualizada ✅"); maq_refresh()

def maq_delete():
    mid = get_val(em, "Código Máquina")
    if not mid:
        messagebox.showwarning("Eliminar", "Selecciona una máquina de la tabla."); return
    if messagebox.askyesno("Confirmar", f"¿Eliminar máquina ID {mid}?"):
        if ejecutar("CALL sp_DeleteMaquinaria(%s)", (mid,)):
            messagebox.showinfo("Maquinaria", "Máquina eliminada ✅")
            clear_entries(em); maq_refresh()

make_buttons(btn_m, maq_save, maq_update, maq_delete,
             lambda: clear_entries(em), maq_refresh)
maq_refresh()

# ═══════════════════════════════════════════════════════════════
#  TAB EMPLEADOS
#  SP usados: sp_insertar_empleado · sp_actualizar_empleado · sp_eliminar_empleado
# ═══════════════════════════════════════════════════════════════
empleado_fields = [
    ("Código Empleado",    "entry", []),
    ("DNI",                "entry", []),
    ("Nombres",            "entry", []),
    ("Apellidos",          "entry", []),
    ("Fecha Nacimiento",   "entry", []),
    ("Dirección",          "entry", []),
    ("Teléfono",           "entry", []),
    ("Especialidad",       "combo", ["Agrónomo","Agrónoma","Operario","Técnica agrícola",
                                     "Administrador","Conductor","Mecánico","Supervisora"]),
    ("Fecha Contratación", "entry", []),
    ("Salario",            "entry", []),
]
EMP_SQL = "SELECT empleados_id, DNI, nombres, apellidos, fecha_nacimiento, direccion, telefono, especialidad, fecha_contratacion, salario FROM empleados"
se, ee, tree_e, sv_e, btn_e = build_panel(tab_empleados, "GESTIÓN DE EMPLEADOS", empleado_fields, "#6b3d7a")

def emp_refresh():
    load_tree(tree_e, EMP_SQL, sv_e.get())

def emp_on_select(event):
    sel = tree_e.selection()
    if not sel: return
    vals = tree_e.item(sel[0], "values")
    for k, v in zip(["Código Empleado","DNI","Nombres","Apellidos","Fecha Nacimiento",
                      "Dirección","Teléfono","Especialidad","Fecha Contratación","Salario"], vals):
        set_val(ee, k, v)

tree_e.bind("<<TreeviewSelect>>", emp_on_select)
bind_search(tree_e, EMP_SQL)

def emp_save():
    # CALL sp_insertar_empleado(dni, nombres, apellidos, fec_nac, direccion,
    #                           telefono, especialidad, fec_contratacion, salario)
    params = (
        get_val(ee,"DNI"), get_val(ee,"Nombres"), get_val(ee,"Apellidos"),
        get_val(ee,"Fecha Nacimiento") or None,
        get_val(ee,"Dirección"),        get_val(ee,"Teléfono"),
        get_val(ee,"Especialidad"),
        get_val(ee,"Fecha Contratación") or None,
        get_val(ee,"Salario") or 0,
    )
    if ejecutar("CALL sp_InsertEmpleado(%s,%s,%s,%s,%s,%s,%s,%s,%s)", params):
        messagebox.showinfo("Empleado", "Empleado guardado ✅")
        clear_entries(ee); emp_refresh()

def emp_update():
    eid = get_val(ee, "Código Empleado")
    if not eid:
        messagebox.showwarning("Actualizar", "Selecciona un empleado de la tabla."); return
    # CALL sp_actualizar_empleado(id, dni, nombres, apellidos, fec_nac, direccion,
    #                             telefono, especialidad, fec_contratacion, salario)
    params = (
        eid,
        get_val(ee,"DNI"), get_val(ee,"Nombres"), get_val(ee,"Apellidos"),
        get_val(ee,"Fecha Nacimiento") or None,
        get_val(ee,"Dirección"),        get_val(ee,"Teléfono"),
        get_val(ee,"Especialidad"),
        get_val(ee,"Fecha Contratación") or None,
        get_val(ee,"Salario") or 0,
    )
    if ejecutar("CALL sp_UpdateEmpleado(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", params):
        messagebox.showinfo("Empleado", "Empleado actualizado ✅"); emp_refresh()

def emp_delete():
    eid = get_val(ee, "Código Empleado")
    if not eid:
        messagebox.showwarning("Eliminar", "Selecciona un empleado de la tabla."); return
    if messagebox.askyesno("Confirmar", f"¿Eliminar empleado ID {eid}?"):
        if ejecutar("CALL sp_DeleteEmpleado(%s)", (eid,)):
            messagebox.showinfo("Empleado", "Empleado eliminado ✅")
            clear_entries(ee); emp_refresh()

make_buttons(btn_e, emp_save, emp_update, emp_delete,
             lambda: clear_entries(ee), emp_refresh)
emp_refresh()

# ═══════════════════════════════════════════════════════════════
#  TAB COSECHAS
#  SP usados: sp_insertar_cosecha · sp_actualizar_cosecha · sp_eliminar_cosecha
# ═══════════════════════════════════════════════════════════════
cosecha_fields = [
    ("Código Cosecha", "entry", []),
    ("Parcela ID",     "entry", []),
    ("Cultivo ID",     "entry", []),
    ("Fecha Inicio",   "entry", []),
    ("Fecha Fin",      "entry", []),
    ("Cantidad (kg)",  "entry", []),
    ("Calidad",        "combo", ["Alta","Media","Baja","Premium","Primera","Segunda","Tercera"]),
    ("Método Cosecha", "combo", ["Manual","Mecanizada","Semi-mecanizada"]),
]
COS_SQL = "SELECT cosecha_id, parcela, cultivo, inicio, fin, cantidad, calidad_producto, metodo_cosecha FROM cosecha"
sh, eh, tree_h, sv_h, btn_h = build_panel(tab_cosechas, "REGISTRO DE COSECHAS", cosecha_fields, "#2d7a5a")

def cos_refresh():
    load_tree(tree_h, COS_SQL, sv_h.get())

def cos_on_select(event):
    sel = tree_h.selection()
    if not sel: return
    vals = tree_h.item(sel[0], "values")
    for k, v in zip(["Código Cosecha","Parcela ID","Cultivo ID","Fecha Inicio",
                      "Fecha Fin","Cantidad (kg)","Calidad","Método Cosecha"], vals):
        set_val(eh, k, v)

tree_h.bind("<<TreeviewSelect>>", cos_on_select)
bind_search(tree_h, COS_SQL)

def cos_save():
    # CALL sp_insertar_cosecha(parcela, cultivo, inicio, fin, cantidad, calidad, metodo)
    params = (
        get_val(eh,"Parcela ID") or None,  get_val(eh,"Cultivo ID") or None,
        get_val(eh,"Fecha Inicio") or None, get_val(eh,"Fecha Fin") or None,
        get_val(eh,"Cantidad (kg)") or 0,
        get_val(eh,"Calidad"),             get_val(eh,"Método Cosecha"),
    )
    if ejecutar("CALL sp_InsertCosecha(%s,%s,%s,%s,%s,%s,%s)", params):
        messagebox.showinfo("Cosecha", "Cosecha registrada ✅")
        clear_entries(eh); cos_refresh()

def cos_update():
    hid = get_val(eh, "Código Cosecha")
    if not hid:
        messagebox.showwarning("Actualizar", "Selecciona una cosecha de la tabla."); return
    # CALL sp_actualizar_cosecha(id, parcela, cultivo, inicio, fin, cantidad, calidad, metodo)
    params = (
        hid,
        get_val(eh,"Parcela ID") or None,  get_val(eh,"Cultivo ID") or None,
        get_val(eh,"Fecha Inicio") or None, get_val(eh,"Fecha Fin") or None,
        get_val(eh,"Cantidad (kg)") or 0,
        get_val(eh,"Calidad"),             get_val(eh,"Método Cosecha"),
    )
    if ejecutar("CALL sp_UpdateCosecha(%s,%s,%s,%s,%s,%s,%s,%s)", params):
        messagebox.showinfo("Cosecha", "Cosecha actualizada ✅"); cos_refresh()

def cos_delete():
    hid = get_val(eh, "Código Cosecha")
    if not hid:
        messagebox.showwarning("Eliminar", "Selecciona una cosecha de la tabla."); return
    if messagebox.askyesno("Confirmar", f"¿Eliminar cosecha ID {hid}?"):
        if ejecutar("CALL sp_DeleteCosecha(%s)", (hid,)):
            messagebox.showinfo("Cosecha", "Cosecha eliminada ✅")
            clear_entries(eh); cos_refresh()

make_buttons(btn_h, cos_save, cos_update, cos_delete,
             lambda: clear_entries(eh), cos_refresh)
cos_refresh()

# ═══════════════════════════════════════════════════════════════
#  TAB CLIENTES
#  SP usados: sp_insertar_cliente · sp_actualizar_cliente · sp_eliminar_cliente
# ═══════════════════════════════════════════════════════════════
cliente_fields = [
    ("Código Cliente",   "entry", []),
    ("Razón Social",     "entry", []),
    ("RUC / DNI",        "entry", []),
    ("Dirección Fiscal", "entry", []),
    ("Teléfono",         "entry", []),
    ("Correo",           "entry", []),
    ("Línea de Crédito", "entry", []),
    ("Tipo",             "combo", ["Minorista","Mayorista","Exportador","Distribuidor"]),
]
CLI_SQL = "SELECT cliente_id, nombre, RUC_o_DNI, direccion_fiscal, telefono, correo_electronico, linea_credito FROM clientes"
scl, ecl, tree_cl, sv_cl, btn_cl = build_panel(tab_clientes, "GESTIÓN DE CLIENTES", cliente_fields, "#7a3d2d")

def cli_refresh():
    load_tree(tree_cl, CLI_SQL, sv_cl.get())

def cli_on_select(event):
    sel = tree_cl.selection()
    if not sel: return
    vals = tree_cl.item(sel[0], "values")
    for k, v in zip(["Código Cliente","Razón Social","RUC / DNI","Dirección Fiscal",
                      "Teléfono","Correo","Línea de Crédito"], vals):
        set_val(ecl, k, v)

tree_cl.bind("<<TreeviewSelect>>", cli_on_select)
bind_search(tree_cl, CLI_SQL)

def cli_save():
    # CALL sp_insertar_cliente(nombre, ruc_dni, direccion, telefono, correo, linea_credito)
    params = (
        get_val(ecl,"Razón Social"),     get_val(ecl,"RUC / DNI"),
        get_val(ecl,"Dirección Fiscal"), get_val(ecl,"Teléfono"),
        get_val(ecl,"Correo"),           get_val(ecl,"Línea de Crédito") or 0,
    )
    if ejecutar("CALL sp_InsertCliente(%s,%s,%s,%s,%s,%s)", params):
        messagebox.showinfo("Cliente", "Cliente guardado ✅")
        clear_entries(ecl); cli_refresh()

def cli_update():
    cid = get_val(ecl, "Código Cliente")
    if not cid:
        messagebox.showwarning("Actualizar", "Selecciona un cliente de la tabla."); return
    # CALL sp_actualizar_cliente(id, nombre, ruc_dni, direccion, telefono, correo, linea_credito)
    params = (
        cid,
        get_val(ecl,"Razón Social"),     get_val(ecl,"RUC / DNI"),
        get_val(ecl,"Dirección Fiscal"), get_val(ecl,"Teléfono"),
        get_val(ecl,"Correo"),           get_val(ecl,"Línea de Crédito") or 0,
    )
    if ejecutar("CALL sp_UpdateCliente(%s,%s,%s,%s,%s,%s,%s)", params):
        messagebox.showinfo("Cliente", "Cliente actualizado ✅"); cli_refresh()

def cli_delete():
    cid = get_val(ecl, "Código Cliente")
    if not cid:
        messagebox.showwarning("Eliminar", "Selecciona un cliente de la tabla."); return
    if messagebox.askyesno("Confirmar", f"¿Eliminar cliente ID {cid}?"):
        if ejecutar("CALL sp_DeleteCliente(%s)", (cid,)):
            messagebox.showinfo("Cliente", "Cliente eliminado ✅")
            clear_entries(ecl); cli_refresh()

make_buttons(btn_cl, cli_save, cli_update, cli_delete,
             lambda: clear_entries(ecl), cli_refresh)
cli_refresh()

# ─────────────────────────────────────────────────────────────
root.mainloop()
