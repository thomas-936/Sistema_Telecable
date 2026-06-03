import tkinter as tk
from tkinter import ttk, messagebox
import os
from PIL import Image, ImageTk
from db import ejecutar_query

def crear_admin_default():
    resultado = ejecutar_query("SELECT COUNT(*) FROM admin", fetch_one=True)
    if resultado and resultado[0] == 0:
        ejecutar_query("""
            INSERT INTO admin (nombre, apellido, usuario, contraseña, correo, telefono)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, ("Administrador", "Sistema", "admin", "1234", "admin@cable.com", "00000000"), commit=True)
        print("Administrador 'admin' creado con contraseña '1234'")

def centrar_ventana(ventana, ancho, alto):
    pantalla_ancho = ventana.winfo_screenwidth()
    pantalla_alto = ventana.winfo_screenheight()
    x = (pantalla_ancho - ancho) // 2
    y = (pantalla_alto - alto) // 2
    ventana.geometry(f"{ancho}x{alto}+{x}+{y}")

def ventana_login():
    ventana = tk.Tk()
    ventana.title("Cable Internet - Inicio de Sesión")
    ventana.attributes('-fullscreen', True)
    ventana.bind("<Escape>", lambda e: ventana.destroy())

    ancho = ventana.winfo_screenwidth()
    alto = ventana.winfo_screenheight()

    ruta_base = os.path.dirname(__file__)
    ruta_fondo = os.path.join(ruta_base, "imagenes_telecable", "fondo.png")
    ruta_logo = os.path.join(ruta_base, "imagenes_telecable", "logo.png")

    if not os.path.exists(ruta_fondo):
        messagebox.showerror("Error", f"No se encontró: {ruta_fondo}")
        ventana.destroy()
        return
    if not os.path.exists(ruta_logo):
        messagebox.showerror("Error", f"No se encontró: {ruta_logo}")
        ventana.destroy()
        return

    fondo = Image.open(ruta_fondo)
    fondo = fondo.resize((ancho, alto), Image.Resampling.LANCZOS)
    fondo_tk = ImageTk.PhotoImage(fondo)

    lienzo = tk.Canvas(ventana, width=ancho, height=alto)
    lienzo.pack(fill="both", expand=True)
    lienzo.create_image(0, 0, image=fondo_tk, anchor="nw")

    logo = Image.open(ruta_logo)
    logo = logo.resize((250, 250), Image.Resampling.LANCZOS)
    logo_tk = ImageTk.PhotoImage(logo)
    lienzo.create_image(ancho // 2, 150, image=logo_tk)

    lienzo.create_text(ancho // 2, 320, text="Inicio de Sesión", font=("Arial", 24, "bold"), fill="white")

    lienzo.create_text(ancho // 2, 370, text="Usuario:", font=("Arial", 14), fill="white")
    entry_usuario = tk.Entry(ventana, font=("Arial", 14), width=25, justify="center")
    lienzo.create_window(ancho // 2, 400, window=entry_usuario)

    lienzo.create_text(ancho // 2, 450, text="Contraseña:", font=("Arial", 14), fill="white")
    entry_pass = tk.Entry(ventana, font=("Arial", 14), width=25, show="*", justify="center")
    lienzo.create_window(ancho // 2, 480, window=entry_pass)

    def verificar():
        usuario = entry_usuario.get().strip()
        password = entry_pass.get().strip()

        if not usuario or not password:
            messagebox.showwarning("Datos incompletos", "Ingrese usuario y contraseña")
            return

        query_admin = "SELECT nombre, apellido, 'administrador' as rol FROM admin WHERE usuario=%s AND contraseña=%s"
        admin_data = ejecutar_query(query_admin, (usuario, password), fetch_one=True)

        if admin_data:
            nombre, apellido, rol = admin_data
            nombre_completo = f"{nombre} {apellido}"
            messagebox.showinfo("Bienvenido", f"Hola {nombre_completo}\nRol: {rol}")
            ventana.destroy()
            abrir_panel_principal(nombre_completo, rol)
            return

        query_tecnico = "SELECT nombre, apellido, 'tecnico' as rol FROM tecnico WHERE usuario=%s AND contraseña=%s"
        tecnico_data = ejecutar_query(query_tecnico, (usuario, password), fetch_one=True)

        if tecnico_data:
            nombre, apellido, rol = tecnico_data
            nombre_completo = f"{nombre} {apellido}"
            messagebox.showinfo("Bienvenido", f"Hola {nombre_completo}\nRol: {rol}")
            ventana.destroy()
            abrir_panel_principal(nombre_completo, rol)
            return

        query_cobrador = "SELECT nombre, apellido, 'cobrador' as rol FROM cobrador WHERE usuario=%s AND contraseña=%s"
        cobrador_data = ejecutar_query(query_cobrador, (usuario, password), fetch_one=True)

        if cobrador_data:
            nombre, apellido, rol = cobrador_data
            nombre_completo = f"{nombre} {apellido}"
            messagebox.showinfo("Bienvenido", f"Hola {nombre_completo}\nRol: {rol}")
            ventana.destroy()
            abrir_panel_principal(nombre_completo, rol)
            return

        messagebox.showerror("Error", "Usuario o contraseña incorrectos")
        entry_pass.delete(0, tk.END)
        entry_pass.focus()

    btn_login = tk.Button(ventana, text="Iniciar Sesión", command=verificar, bg="#4CAF50", fg="white", font=("Arial", 14), width=20)
    lienzo.create_window(ancho // 2, 530, window=btn_login)

    btn_salir = tk.Button(ventana, text="Salir", command=ventana.destroy, bg="#f44336", fg="white", font=("Arial", 14), width=20)
    lienzo.create_window(ancho // 2, 580, window=btn_salir)

    entry_usuario.bind("<Return>", lambda e: entry_pass.focus())
    entry_pass.bind("<Return>", lambda e: verificar())

    ventana.fondo_tk = fondo_tk
    ventana.logo_tk = logo_tk

    entry_usuario.focus()
    ventana.mainloop()

def ventana_gestion_clientes():
    ventana = tk.Toplevel()
    ventana.title("Gestión de Clientes y Teléfonos - Cable Internet")
    ventana.attributes('-fullscreen', True)
    ventana.transient()
    ventana.grab_set()
    ventana.bind("<Escape>", lambda e: ventana.destroy())

    cliente_seleccionado_id = tk.IntVar()

    panel_principal = tk.PanedWindow(ventana, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, sashwidth=5)
    panel_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    frame_lista = tk.LabelFrame(panel_principal, text="Clientes Registrados", font=("Arial", 12, "bold"))
    panel_principal.add(frame_lista, width=600)

    frame_buscar = tk.Frame(frame_lista)
    frame_buscar.pack(fill="x", padx=5, pady=5)
    tk.Label(frame_buscar, text="Buscar:", font=("Arial", 10)).pack(side="left")
    entry_buscar = tk.Entry(frame_buscar, font=("Arial", 10), width=30)
    entry_buscar.pack(side="left", padx=5)

    columnas_clientes = ("ID", "Nombre", "Apellido", "DPI")
    tree_clientes = ttk.Treeview(frame_lista, columns=columnas_clientes, show="headings", height=15)
    for col in columnas_clientes:
        tree_clientes.heading(col, text=col)
        tree_clientes.column(col, width=120)
    tree_clientes.pack(side="left", fill="both", expand=True, padx=5, pady=5)

    scroll_clientes = ttk.Scrollbar(frame_lista, orient="vertical", command=tree_clientes.yview)
    tree_clientes.configure(yscrollcommand=scroll_clientes.set)
    scroll_clientes.pack(side="right", fill="y")

    panel_derecho = tk.Frame(panel_principal)
    panel_principal.add(panel_derecho, width=500)

    frame_form = tk.LabelFrame(panel_derecho, text="Datos del Cliente", font=("Arial", 12, "bold"))
    frame_form.pack(fill="x", pady=5)

    campos = [
        ("Nombre *:", "nombre"), ("Apellido *:", "apellido"),
        ("DPI *:", "dpi"), ("Barrio *:", "barrio"),
        ("Zona *:", "zona"), ("Calle *:", "calle"),
        ("Número de Casa *:", "num_casa")
    ]

    entries = {}
    for i, (label, key) in enumerate(campos):
        fila = i // 2
        columna = (i % 2) * 2
        tk.Label(frame_form, text=label, font=("Arial", 10)).grid(row=fila, column=columna, padx=5, pady=5, sticky="e")
        entry = tk.Entry(frame_form, font=("Arial", 10), width=30)
        entry.grid(row=fila, column=columna + 1, padx=5, pady=5, sticky="w")
        entries[key] = entry

    frame_botones_form = tk.Frame(frame_form)
    frame_botones_form.grid(row=4, column=0, columnspan=4, pady=10)

    btn_guardar = tk.Button(frame_botones_form, text="Guardar Cliente", bg="#4CAF50", fg="white", width=12)
    btn_guardar.pack(side="left", padx=5)
    btn_actualizar = tk.Button(frame_botones_form, text="Actualizar Cliente", bg="#2196F3", fg="white", width=14, state="disabled")
    btn_actualizar.pack(side="left", padx=5)
    btn_eliminar = tk.Button(frame_botones_form, text="Eliminar Cliente", bg="#f44336", fg="white", width=12, state="disabled")
    btn_eliminar.pack(side="left", padx=5)
    btn_nuevo = tk.Button(frame_botones_form, text="Nuevo Cliente", bg="#FF9800", fg="white", width=12)
    btn_nuevo.pack(side="left", padx=5)

    frame_tels = tk.LabelFrame(panel_derecho, text="Teléfonos del Cliente", font=("Arial", 12, "bold"))
    frame_tels.pack(fill="both", expand=True, pady=10)

    columnas_tels = ("ID", "Teléfono")
    tree_tels = ttk.Treeview(frame_tels, columns=columnas_tels, show="headings", height=6)
    tree_tels.heading("ID", text="ID")
    tree_tels.heading("Teléfono", text="Número")
    tree_tels.column("ID", width=50)
    tree_tels.column("Teléfono", width=200)
    tree_tels.pack(side="left", fill="both", expand=True, padx=5, pady=5)

    scroll_tels = ttk.Scrollbar(frame_tels, orient="vertical", command=tree_tels.yview)
    tree_tels.configure(yscrollcommand=scroll_tels.set)
    scroll_tels.pack(side="right", fill="y")

    frame_nuevo_tel = tk.Frame(frame_tels)
    frame_nuevo_tel.pack(fill="x", pady=5)
    tk.Label(frame_nuevo_tel, text="Nuevo Teléfono:", font=("Arial", 10)).pack(side="left", padx=5)
    entry_telefono = tk.Entry(frame_nuevo_tel, font=("Arial", 10), width=20)
    entry_telefono.pack(side="left", padx=5)
    btn_agregar_tel = tk.Button(frame_nuevo_tel, text="Agregar", bg="#4CAF50", fg="white", width=10)
    btn_agregar_tel.pack(side="left", padx=5)
    btn_eliminar_tel = tk.Button(frame_nuevo_tel, text="Eliminar", bg="#f44336", fg="white", width=10)
    btn_eliminar_tel.pack(side="left", padx=5)

    btn_cerrar = tk.Button(panel_derecho, text="Cerrar", command=ventana.destroy, bg="#f44336", fg="white", width=15)
    btn_cerrar.pack(pady=10)

    def limpiar_formulario():
        for entry in entries.values():
            entry.delete(0, tk.END)
        entries["nombre"].focus()
        btn_actualizar.config(state="disabled", text="Actualizar Cliente")
        btn_eliminar.config(state="disabled")
        cliente_seleccionado_id.set(0)

    def cargar_clientes(busqueda=""):
        for item in tree_clientes.get_children():
            tree_clientes.delete(item)
        if busqueda.isdigit():
            query = "SELECT id_cliente, nombre, apellido, dpi FROM cliente WHERE id_cliente = %s"
            params = (int(busqueda),)
            registros = ejecutar_query(query, params, fetch_all=True)
        elif busqueda:
            query = "SELECT id_cliente, nombre, apellido, dpi FROM cliente WHERE nombre LIKE %s OR apellido LIKE %s OR dpi LIKE %s"
            params = (f"%{busqueda}%", f"%{busqueda}%", f"%{busqueda}%")
            registros = ejecutar_query(query, params, fetch_all=True)
        else:
            query = "SELECT id_cliente, nombre, apellido, dpi FROM cliente ORDER BY id_cliente DESC"
            registros = ejecutar_query(query, fetch_all=True)
        if registros:
            for reg in registros:
                tree_clientes.insert("", "end", values=(reg[0], reg[1], reg[2], reg[3]))
        else:
            tree_clientes.insert("", "end", values=("No hay datos", "", "", ""))

    def cargar_telefonos():
        for item in tree_tels.get_children():
            tree_tels.delete(item)
        id_cliente = cliente_seleccionado_id.get()
        if id_cliente:
            query = "SELECT id_telefono, num_telefono FROM telefono WHERE id_cliente = %s"
            telefonos = ejecutar_query(query, (id_cliente,), fetch_all=True)
            if telefonos:
                for tel in telefonos:
                    tree_tels.insert("", "end", values=(tel[0], tel[1]))
            else:
                tree_tels.insert("", "end", values=("", "Sin teléfonos registrados"))

    def guardar_cliente():
        datos = {key: entry.get().strip() for key, entry in entries.items()}
        for key, valor in datos.items():
            if not valor:
                messagebox.showwarning("Datos incompletos", f"El campo '{key}' es obligatorio")
                entries[key].focus()
                return
        query = """
            INSERT INTO cliente (nombre, apellido, dpi, barrio, zona, calle, num_casa)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        resultado = ejecutar_query(query, (datos["nombre"], datos["apellido"], datos["dpi"], datos["barrio"], datos["zona"], datos["calle"], datos["num_casa"]), commit=True)
        if resultado:
            messagebox.showinfo("Éxito", f"Cliente '{datos['nombre']} {datos['apellido']}' registrado")
            limpiar_formulario()
            cargar_clientes()
        else:
            messagebox.showerror("Error", "No se pudo guardar el cliente")

    def actualizar_cliente():
        id_cliente = cliente_seleccionado_id.get()
        if not id_cliente:
            messagebox.showwarning("Sin selección", "Seleccione un cliente de la lista")
            return
        datos = {key: entry.get().strip() for key, entry in entries.items()}
        for key, valor in datos.items():
            if not valor:
                messagebox.showwarning("Datos incompletos", f"El campo '{key}' es obligatorio")
                entries[key].focus()
                return
        query = """
            UPDATE cliente SET nombre=%s, apellido=%s, dpi=%s, barrio=%s, zona=%s, calle=%s, num_casa=%s
            WHERE id_cliente=%s
        """
        resultado = ejecutar_query(query, (datos["nombre"], datos["apellido"], datos["dpi"], datos["barrio"], datos["zona"], datos["calle"], datos["num_casa"], id_cliente), commit=True)
        if resultado is not None:
            messagebox.showinfo("Éxito", "Datos del cliente actualizados")
            cargar_clientes()
            cargar_telefonos()
        else:
            messagebox.showerror("Error", "No se pudo actualizar")

    def eliminar_cliente():
        id_cliente = cliente_seleccionado_id.get()
        if not id_cliente:
            messagebox.showwarning("Sin selección", "Seleccione un cliente de la lista")
            return
        nombre = entries["nombre"].get().strip()
        confirmar = messagebox.askyesno("Confirmar", f"¿Eliminar al cliente '{nombre}' y TODOS sus teléfonos?")
        if confirmar:
            ejecutar_query("DELETE FROM telefono WHERE id_cliente = %s", (id_cliente,), commit=True)
            ejecutar_query("DELETE FROM cliente WHERE id_cliente = %s", (id_cliente,), commit=True)
            messagebox.showinfo("Éxito", "Cliente eliminado")
            limpiar_formulario()
            cargar_clientes()

    def on_cliente_seleccionado(event):
        seleccion = tree_clientes.selection()
        if seleccion:
            valores = tree_clientes.item(seleccion[0])["values"]
            if valores[0] != "No hay datos":
                id_cliente = valores[0]
                cliente_seleccionado_id.set(id_cliente)
                query = "SELECT nombre, apellido, dpi, barrio, zona, calle, num_casa FROM cliente WHERE id_cliente = %s"
                datos_cliente = ejecutar_query(query, (id_cliente,), fetch_one=True)
                if datos_cliente:
                    entries["nombre"].delete(0, tk.END); entries["nombre"].insert(0, datos_cliente[0] or "")
                    entries["apellido"].delete(0, tk.END); entries["apellido"].insert(0, datos_cliente[1] or "")
                    entries["dpi"].delete(0, tk.END); entries["dpi"].insert(0, datos_cliente[2] or "")
                    entries["barrio"].delete(0, tk.END); entries["barrio"].insert(0, datos_cliente[3] or "")
                    entries["zona"].delete(0, tk.END); entries["zona"].insert(0, datos_cliente[4] or "")
                    entries["calle"].delete(0, tk.END); entries["calle"].insert(0, datos_cliente[5] or "")
                    entries["num_casa"].delete(0, tk.END); entries["num_casa"].insert(0, datos_cliente[6] or "")
                btn_actualizar.config(state="normal", text="Actualizar Cliente")
                btn_eliminar.config(state="normal")
                cargar_telefonos()
                entry_telefono.focus()
        else:
            limpiar_formulario()

    def agregar_telefono():
        id_cliente = cliente_seleccionado_id.get()
        if not id_cliente:
            messagebox.showwarning("Sin cliente", "Seleccione un cliente de la lista")
            return
        telefono = entry_telefono.get().strip()
        if not telefono:
            messagebox.showwarning("Datos incompletos", "Ingrese un número de teléfono")
            return
        query = "INSERT INTO telefono (num_telefono, id_cliente) VALUES (%s, %s)"
        resultado = ejecutar_query(query, (telefono, id_cliente), commit=True)
        if resultado:
            messagebox.showinfo("Éxito", "Teléfono agregado")
            entry_telefono.delete(0, tk.END)
            cargar_telefonos()
        else:
            messagebox.showerror("Error", "No se pudo agregar el teléfono")

    def eliminar_telefono():
        seleccion = tree_tels.selection()
        if not seleccion:
            messagebox.showwarning("Selección", "Seleccione un teléfono de la lista")
            return
        valores = tree_tels.item(seleccion[0])["values"]
        id_telefono = valores[0]
        if id_telefono:
            confirmar = messagebox.askyesno("Confirmar", f"¿Eliminar el teléfono '{valores[1]}'?")
            if confirmar:
                ejecutar_query("DELETE FROM telefono WHERE id_telefono = %s", (id_telefono,), commit=True)
                cargar_telefonos()

    def buscar_clientes():
        texto = entry_buscar.get().strip()
        cargar_clientes(texto)

    def limpiar_busqueda():
        entry_buscar.delete(0, tk.END)
        cargar_clientes()

    def nuevo_cliente():
        limpiar_formulario()
        cargar_telefonos()
        entries["nombre"].focus()

    btn_guardar.config(command=guardar_cliente)
    btn_actualizar.config(command=actualizar_cliente)
    btn_eliminar.config(command=eliminar_cliente)
    btn_nuevo.config(command=nuevo_cliente)
    btn_agregar_tel.config(command=agregar_telefono)
    btn_eliminar_tel.config(command=eliminar_telefono)
    btn_buscar = tk.Button(frame_buscar, text="Buscar", command=buscar_clientes, bg="#2196F3", fg="white")
    btn_buscar.pack(side="left", padx=5)
    btn_refrescar = tk.Button(frame_buscar, text="Refrescar", command=limpiar_busqueda, bg="#9E9E9E", fg="white")
    btn_refrescar.pack(side="left", padx=5)

    tree_clientes.bind("<<TreeviewSelect>>", on_cliente_seleccionado)
    entry_buscar.bind("<Return>", lambda e: buscar_clientes())

    cargar_clientes()

def ventana_gestion_tecnicos():
    ventana = tk.Toplevel()
    ventana.title("Gestión de Técnicos - Cable Internet")
    ventana.attributes('-fullscreen', True)
    ventana.transient()
    ventana.grab_set()
    ventana.bind("<Escape>", lambda e: ventana.destroy())

    tecnico_seleccionado_id = tk.IntVar()

    panel_principal = tk.PanedWindow(ventana, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, sashwidth=5)
    panel_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    frame_lista = tk.LabelFrame(panel_principal, text="Técnicos Registrados", font=("Arial", 12, "bold"))
    panel_principal.add(frame_lista, width=600)

    frame_buscar = tk.Frame(frame_lista)
    frame_buscar.pack(fill="x", padx=5, pady=5)
    tk.Label(frame_buscar, text="Buscar:", font=("Arial", 10)).pack(side="left")
    entry_buscar = tk.Entry(frame_buscar, font=("Arial", 10), width=30)
    entry_buscar.pack(side="left", padx=5)

    columnas_tecnicos = ("ID", "Nombre", "Apellido", "DPI", "Teléfono", "Usuario")
    tree_tecnicos = ttk.Treeview(frame_lista, columns=columnas_tecnicos, show="headings", height=15)
    anchos = {"ID": 50, "Nombre": 120, "Apellido": 120, "DPI": 120, "Teléfono": 100, "Usuario": 100}
    for col in columnas_tecnicos:
        tree_tecnicos.heading(col, text=col)
        tree_tecnicos.column(col, width=anchos.get(col, 100))
    tree_tecnicos.pack(side="left", fill="both", expand=True, padx=5, pady=5)

    scroll_tecnicos = ttk.Scrollbar(frame_lista, orient="vertical", command=tree_tecnicos.yview)
    tree_tecnicos.configure(yscrollcommand=scroll_tecnicos.set)
    scroll_tecnicos.pack(side="right", fill="y")

    panel_derecho = tk.Frame(panel_principal)
    panel_principal.add(panel_derecho, width=500)

    frame_form = tk.LabelFrame(panel_derecho, text="Datos del Técnico", font=("Arial", 12, "bold"))
    frame_form.pack(fill="x", pady=5)

    campos = [
        ("Nombre *:", "nombre"),
        ("Apellido *:", "apellido"),
        ("DPI *:", "dpi"),
        ("Teléfono *:", "telefono"),
        ("Usuario *:", "usuario"),
        ("Contraseña *:", "contraseña")
    ]

    entries = {}
    for i, (label, key) in enumerate(campos):
        tk.Label(frame_form, text=label, font=("Arial", 10)).grid(row=i, column=0, padx=5, pady=5, sticky="e")
        entry = tk.Entry(frame_form, font=("Arial", 10), width=40)
        if key == "contraseña":
            entry.config(show="*")
        entry.grid(row=i, column=1, padx=5, pady=5, sticky="w")
        entries[key] = entry

    frame_botones_form = tk.Frame(frame_form)
    frame_botones_form.grid(row=len(campos), column=0, columnspan=2, pady=10)

    btn_guardar = tk.Button(frame_botones_form, text="Guardar Técnico", bg="#4CAF50", fg="white", width=12)
    btn_guardar.pack(side="left", padx=5)
    btn_actualizar = tk.Button(frame_botones_form, text="Actualizar Técnico", bg="#2196F3", fg="white", width=14, state="disabled")
    btn_actualizar.pack(side="left", padx=5)
    btn_eliminar = tk.Button(frame_botones_form, text="Eliminar Técnico", bg="#f44336", fg="white", width=12, state="disabled")
    btn_eliminar.pack(side="left", padx=5)
    btn_nuevo = tk.Button(frame_botones_form, text="Nuevo Técnico", bg="#FF9800", fg="white", width=12)
    btn_nuevo.pack(side="left", padx=5)

    btn_cerrar = tk.Button(panel_derecho, text="Cerrar", command=ventana.destroy, bg="#f44336", fg="white", width=15)
    btn_cerrar.pack(pady=10)

    def limpiar_formulario():
        for entry in entries.values():
            entry.delete(0, tk.END)
        entries["nombre"].focus()
        btn_actualizar.config(state="disabled")
        btn_eliminar.config(state="disabled")
        tecnico_seleccionado_id.set(0)

    def cargar_tecnicos(busqueda=""):
        for item in tree_tecnicos.get_children():
            tree_tecnicos.delete(item)
        if busqueda.isdigit():
            query = "SELECT id_tecnico, nombre, apellido, dpi, telefono, usuario FROM tecnico WHERE id_tecnico = %s"
            params = (int(busqueda),)
            registros = ejecutar_query(query, params, fetch_all=True)
        elif busqueda:
            query = "SELECT id_tecnico, nombre, apellido, dpi, telefono, usuario FROM tecnico WHERE nombre LIKE %s OR apellido LIKE %s OR dpi LIKE %s"
            params = (f"%{busqueda}%", f"%{busqueda}%", f"%{busqueda}%")
            registros = ejecutar_query(query, params, fetch_all=True)
        else:
            query = "SELECT id_tecnico, nombre, apellido, dpi, telefono, usuario FROM tecnico ORDER BY id_tecnico DESC"
            registros = ejecutar_query(query, fetch_all=True)
        if registros:
            for reg in registros:
                tree_tecnicos.insert("", "end", values=(reg[0], reg[1], reg[2], reg[3], reg[4] or "", reg[5] or ""))
        else:
            tree_tecnicos.insert("", "end", values=("No hay datos", "", "", "", "", ""))

    def guardar_tecnico():
        datos = {key: entry.get().strip() for key, entry in entries.items()}
        for key in ["nombre", "apellido", "dpi", "telefono", "usuario", "contraseña"]:
            if not datos.get(key):
                messagebox.showwarning("Datos incompletos", f"El campo '{key}' es obligatorio")
                entries[key].focus()
                return
        query = "INSERT INTO tecnico (nombre, apellido, dpi, telefono, usuario, contraseña) VALUES (%s, %s, %s, %s, %s, %s)"
        resultado = ejecutar_query(query, (datos["nombre"], datos["apellido"], datos["dpi"], datos["telefono"], datos["usuario"], datos["contraseña"]), commit=True)
        if resultado:
            messagebox.showinfo("Éxito", f"Técnico '{datos['nombre']} {datos['apellido']}' registrado con usuario '{datos['usuario']}'")
            limpiar_formulario()
            cargar_tecnicos()
        else:
            messagebox.showerror("Error", "No se pudo guardar. Verifique que el DPI o usuario no esté duplicado.")

    def actualizar_tecnico():
        id_tecnico = tecnico_seleccionado_id.get()
        if not id_tecnico:
            messagebox.showwarning("Sin selección", "Seleccione un técnico de la lista")
            return
        datos = {key: entry.get().strip() for key, entry in entries.items()}
        for key in ["nombre", "apellido", "dpi", "telefono", "usuario", "contraseña"]:
            if not datos.get(key):
                messagebox.showwarning("Datos incompletos", f"El campo '{key}' es obligatorio")
                entries[key].focus()
                return
        query = "UPDATE tecnico SET nombre=%s, apellido=%s, dpi=%s, telefono=%s, usuario=%s, contraseña=%s WHERE id_tecnico=%s"
        resultado = ejecutar_query(query, (datos["nombre"], datos["apellido"], datos["dpi"], datos["telefono"], datos["usuario"], datos["contraseña"], id_tecnico), commit=True)
        if resultado is not None:
            messagebox.showinfo("Éxito", "Datos del técnico actualizados")
            cargar_tecnicos()
        else:
            messagebox.showerror("Error", "No se pudo atualizar")

    def eliminar_tecnico():
        id_tecnico = tecnico_seleccionado_id.get()
        if not id_tecnico:
            messagebox.showwarning("Sin selección", "Seleccione un técnico de la lista")
            return
        nombre = entries["nombre"].get().strip()
        confirmar = messagebox.askyesno("Confirmar", f"¿Eliminar al técnico '{nombre}'?")
        if confirmar:
            ejecutar_query("DELETE FROM tecnico WHERE id_tecnico = %s", (id_tecnico,), commit=True)
            messagebox.showinfo("Éxito", "Técnico eliminado")
            limpiar_formulario()
            cargar_tecnicos()

    def on_tecnico_seleccionado(event):
        seleccion = tree_tecnicos.selection()
        if seleccion:
            valores = tree_tecnicos.item(seleccion[0])["values"]
            if valores[0] != "No hay datos":
                id_tecnico = valores[0]
                tecnico_seleccionado_id.set(id_tecnico)
                query = "SELECT nombre, apellido, dpi, telefono, usuario, contraseña FROM tecnico WHERE id_tecnico = %s"
                datos_tecnico = ejecutar_query(query, (id_tecnico,), fetch_one=True)
                if datos_tecnico:
                    entries["nombre"].delete(0, tk.END)
                    entries["nombre"].insert(0, datos_tecnico[0] or "")
                    entries["apellido"].delete(0, tk.END)
                    entries["apellido"].insert(0, datos_tecnico[1] or "")
                    entries["dpi"].delete(0, tk.END)
                    entries["dpi"].insert(0, datos_tecnico[2] or "")
                    entries["telefono"].delete(0, tk.END)
                    entries["telefono"].insert(0, datos_tecnico[3] or "")
                    entries["usuario"].delete(0, tk.END)
                    entries["usuario"].insert(0, datos_tecnico[4] or "")
                    entries["contraseña"].delete(0, tk.END)
                    entries["contraseña"].insert(0, datos_tecnico[5] or "")
                btn_actualizar.config(state="normal")
                btn_eliminar.config(state="normal")
        else:
            limpiar_formulario()

    def buscar_tecnicos():
        texto = entry_buscar.get().strip()
        cargar_tecnicos(texto)

    def limpiar_busqueda():
        entry_buscar.delete(0, tk.END)
        cargar_tecnicos()

    def nuevo_tecnico():
        limpiar_formulario()

    btn_guardar.config(command=guardar_tecnico)
    btn_actualizar.config(command=actualizar_tecnico)
    btn_eliminar.config(command=eliminar_tecnico)
    btn_nuevo.config(command=nuevo_tecnico)
    btn_buscar = tk.Button(frame_buscar, text="Buscar", command=buscar_tecnicos, bg="#2196F3", fg="white")
    btn_buscar.pack(side="left", padx=5)
    btn_refrescar = tk.Button(frame_buscar, text="Refrescar", command=limpiar_busqueda, bg="#9E9E9E", fg="white")
    btn_refrescar.pack(side="left", padx=5)

    tree_tecnicos.bind("<<TreeviewSelect>>", on_tecnico_seleccionado)
    entry_buscar.bind("<Return>", lambda e: buscar_tecnicos())

    cargar_tecnicos()

def ventana_gestion_cobradores():
    ventana = tk.Toplevel()
    ventana.title("Gestión de Cobradores - Cable Internet")
    ventana.attributes('-fullscreen', True)
    ventana.transient()
    ventana.grab_set()
    ventana.bind("<Escape>", lambda e: ventana.destroy())

    cobrador_seleccionado_id = tk.IntVar()

    panel_principal = tk.PanedWindow(ventana, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, sashwidth=5)
    panel_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    frame_lista = tk.LabelFrame(panel_principal, text="Cobradores Registrados", font=("Arial", 12, "bold"))
    panel_principal.add(frame_lista, width=600)

    frame_buscar = tk.Frame(frame_lista)
    frame_buscar.pack(fill="x", padx=5, pady=5)
    tk.Label(frame_buscar, text="Buscar:", font=("Arial", 10)).pack(side="left")
    entry_buscar = tk.Entry(frame_buscar, font=("Arial", 10), width=30)
    entry_buscar.pack(side="left", padx=5)

    columnas_cobradores = ("ID", "Nombre", "Apellido", "DPI", "Teléfono", "Usuario")
    tree_cobradores = ttk.Treeview(frame_lista, columns=columnas_cobradores, show="headings", height=15)
    anchos = {"ID": 50, "Nombre": 120, "Apellido": 120, "DPI": 120, "Teléfono": 100, "Usuario": 100}
    for col in columnas_cobradores:
        tree_cobradores.heading(col, text=col)
        tree_cobradores.column(col, width=anchos.get(col, 100))
    tree_cobradores.pack(side="left", fill="both", expand=True, padx=5, pady=5)

    scroll_cobradores = ttk.Scrollbar(frame_lista, orient="vertical", command=tree_cobradores.yview)
    tree_cobradores.configure(yscrollcommand=scroll_cobradores.set)
    scroll_cobradores.pack(side="right", fill="y")

    panel_derecho = tk.Frame(panel_principal)
    panel_principal.add(panel_derecho, width=500)

    frame_form = tk.LabelFrame(panel_derecho, text="Datos del Cobrador", font=("Arial", 12, "bold"))
    frame_form.pack(fill="x", pady=5)

    campos = [
        ("Nombre *:", "nombre"),
        ("Apellido *:", "apellido"),
        ("DPI *:", "dpi"),
        ("Teléfono *:", "telefono"),
        ("Usuario *:", "usuario"),
        ("Contraseña *:", "contraseña")
    ]

    entries = {}
    for i, (label, key) in enumerate(campos):
        tk.Label(frame_form, text=label, font=("Arial", 10)).grid(row=i, column=0, padx=5, pady=5, sticky="e")
        entry = tk.Entry(frame_form, font=("Arial", 10), width=40)
        if key == "contraseña":
            entry.config(show="*")
        entry.grid(row=i, column=1, padx=5, pady=5, sticky="w")
        entries[key] = entry

    frame_botones_form = tk.Frame(frame_form)
    frame_botones_form.grid(row=len(campos), column=0, columnspan=2, pady=10)

    btn_guardar = tk.Button(frame_botones_form, text="Guardar Cobrador", bg="#4CAF50", fg="white", width=12)
    btn_guardar.pack(side="left", padx=5)
    btn_actualizar = tk.Button(frame_botones_form, text="Actualizar Cobrador", bg="#2196F3", fg="white", width=14, state="disabled")
    btn_actualizar.pack(side="left", padx=5)
    btn_eliminar = tk.Button(frame_botones_form, text="Eliminar Cobrador", bg="#f44336", fg="white", width=12, state="disabled")
    btn_eliminar.pack(side="left", padx=5)
    btn_nuevo = tk.Button(frame_botones_form, text="Nuevo Cobrador", bg="#FF9800", fg="white", width=12)
    btn_nuevo.pack(side="left", padx=5)

    btn_cerrar = tk.Button(panel_derecho, text="Cerrar", command=ventana.destroy, bg="#f44336", fg="white", width=15)
    btn_cerrar.pack(pady=10)

    def limpiar_formulario():
        for entry in entries.values():
            entry.delete(0, tk.END)
        entries["nombre"].focus()
        btn_actualizar.config(state="disabled")
        btn_eliminar.config(state="disabled")
        cobrador_seleccionado_id.set(0)

    def cargar_cobradores(busqueda=""):
        for item in tree_cobradores.get_children():
            tree_cobradores.delete(item)
        if busqueda.isdigit():
            query = "SELECT id_cobrador, nombre, apellido, dpi, telefono, usuario FROM cobrador WHERE id_cobrador = %s"
            params = (int(busqueda),)
            registros = ejecutar_query(query, params, fetch_all=True)
        elif busqueda:
            query = "SELECT id_cobrador, nombre, apellido, dpi, telefono, usuario FROM cobrador WHERE nombre LIKE %s OR apellido LIKE %s OR dpi LIKE %s"
            params = (f"%{busqueda}%", f"%{busqueda}%", f"%{busqueda}%")
            registros = ejecutar_query(query, params, fetch_all=True)
        else:
            query = "SELECT id_cobrador, nombre, apellido, dpi, telefono, usuario FROM cobrador ORDER BY id_cobrador DESC"
            registros = ejecutar_query(query, fetch_all=True)
        if registros:
            for reg in registros:
                tree_cobradores.insert("", "end", values=(reg[0], reg[1], reg[2], reg[3], reg[4] or "", reg[5] or ""))
        else:
            tree_cobradores.insert("", "end", values=("No hay datos", "", "", "", "", ""))

    def guardar_cobrador():
        datos = {key: entry.get().strip() for key, entry in entries.items()}
        for key in ["nombre", "apellido", "dpi", "telefono", "usuario", "contraseña"]:
            if not datos.get(key):
                messagebox.showwarning("Datos incompletos", f"El campo '{key}' es obligatorio")
                entries[key].focus()
                return
        query = "INSERT INTO cobrador (nombre, apellido, dpi, telefono, usuario, contraseña) VALUES (%s, %s, %s, %s, %s, %s)"
        resultado = ejecutar_query(query, (datos["nombre"], datos["apellido"], datos["dpi"], datos["telefono"], datos["usuario"], datos["contraseña"]), commit=True)
        if resultado:
            messagebox.showinfo("Éxito", f"Cobrador '{datos['nombre']} {datos['apellido']}' registrado con usuario '{datos['usuario']}'")
            limpiar_formulario()
            cargar_cobradores()
        else:
            messagebox.showerror("Error", "No se pudo guardar. Verifique que el DPI o usuario no esté duplicado.")

    def actualizar_cobrador():
        id_cobrador = cobrador_seleccionado_id.get()
        if not id_cobrador:
            messagebox.showwarning("Sin selección", "Seleccione un cobrador de la lista")
            return
        datos = {key: entry.get().strip() for key, entry in entries.items()}
        for key in ["nombre", "apellido", "dpi", "telefono", "usuario", "contraseña"]:
            if not datos.get(key):
                messagebox.showwarning("Datos incompletos", f"El campo '{key}' es obligatorio")
                entries[key].focus()
                return
        query = "UPDATE cobrador SET nombre=%s, apellido=%s, dpi=%s, telefono=%s, usuario=%s, contraseña=%s WHERE id_cobrador=%s"
        resultado = ejecutar_query(query, (datos["nombre"], datos["apellido"], datos["dpi"], datos["telefono"], datos["usuario"], datos["contraseña"], id_cobrador), commit=True)
        if resultado is not None:
            messagebox.showinfo("Éxito", "Datos del cobrador actualizados")
            cargar_cobradores()
        else:
            messagebox.showerror("Error", "No se pudo actualizar")

    def eliminar_cobrador():
        id_cobrador = cobrador_seleccionado_id.get()
        if not id_cobrador:
            messagebox.showwarning("Sin selección", "Seleccione un cobrador de la lista")
            return
        nombre = entries["nombre"].get().strip()
        confirmar = messagebox.askyesno("Confirmar", f"¿Eliminar al cobrador '{nombre}'?")
        if confirmar:
            ejecutar_query("DELETE FROM cobrador WHERE id_cobrador = %s", (id_cobrador,), commit=True)
            messagebox.showinfo("Éxito", "Cobrador eliminado")
            limpiar_formulario()
            cargar_cobradores()

    def on_cobrador_seleccionado(event):
        seleccion = tree_cobradores.selection()
        if seleccion:
            valores = tree_cobradores.item(seleccion[0])["values"]
            if valores[0] != "No hay datos":
                id_cobrador = valores[0]
                cobrador_seleccionado_id.set(id_cobrador)
                query = "SELECT nombre, apellido, dpi, telefono, usuario, contraseña FROM cobrador WHERE id_cobrador = %s"
                datos_cobrador = ejecutar_query(query, (id_cobrador,), fetch_one=True)
                if datos_cobrador:
                    entries["nombre"].delete(0, tk.END); entries["nombre"].insert(0, datos_cobrador[0] or "")
                    entries["apellido"].delete(0, tk.END); entries["apellido"].insert(0, datos_cobrador[1] or "")
                    entries["dpi"].delete(0, tk.END); entries["dpi"].insert(0, datos_cobrador[2] or "")
                    entries["telefono"].delete(0, tk.END); entries["telefono"].insert(0, datos_cobrador[3] or "")
                    entries["usuario"].delete(0, tk.END); entries["usuario"].insert(0, datos_cobrador[4] or "")
                    entries["contraseña"].delete(0, tk.END); entries["contraseña"].insert(0, datos_cobrador[5] or "")
                btn_actualizar.config(state="normal")
                btn_eliminar.config(state="normal")
        else:
            limpiar_formulario()

    def buscar_cobradores():
        texto = entry_buscar.get().strip()
        cargar_cobradores(texto)

    def limpiar_busqueda():
        entry_buscar.delete(0, tk.END)
        cargar_cobradores()

    def nuevo_cobrador():
        limpiar_formulario()

    btn_guardar.config(command=guardar_cobrador)
    btn_actualizar.config(command=actualizar_cobrador)
    btn_eliminar.config(command=eliminar_cobrador)
    btn_nuevo.config(command=nuevo_cobrador)
    btn_buscar = tk.Button(frame_buscar, text="Buscar", command=buscar_cobradores, bg="#2196F3", fg="white")
    btn_buscar.pack(side="left", padx=5)
    btn_refrescar = tk.Button(frame_buscar, text="Refrescar", command=limpiar_busqueda, bg="#9E9E9E", fg="white")
    btn_refrescar.pack(side="left", padx=5)

    tree_cobradores.bind("<<TreeviewSelect>>", on_cobrador_seleccionado)
    entry_buscar.bind("<Return>", lambda e: buscar_cobradores())

    cargar_cobradores()

def ventana_gestion_servicios():
    ventana = tk.Toplevel()
    ventana.title("Gestión de Servicios - Cable Internet")
    ventana.attributes('-fullscreen', True)
    ventana.transient()
    ventana.grab_set()
    ventana.bind("<Escape>", lambda e: ventana.destroy())

    servicio_seleccionado_id = tk.IntVar()

    precios_servicios = {
        "Cable TV (Mensualidad)": 75.00,
        "Internet 30 Mbps": 125.00,
        "Internet 60 Mbps": 150.00,
        "Internet 150 Mbps": 250.00,
        "Internet 250 Mbps": 300.00,
        "Internet 30 Mbps + Cable": 200.00,
        "Internet 60 Mbps + Cable": 225.00,
        "Internet 150 Mbps + Cable": 325.00,
        "Internet 250 Mbps + Cable": 375.00
    }

    panel_principal = tk.PanedWindow(ventana, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, sashwidth=5)
    panel_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    frame_lista = tk.LabelFrame(panel_principal, text="Servicios Registrados", font=("Arial", 12, "bold"))
    panel_principal.add(frame_lista, width=600)

    frame_buscar = tk.Frame(frame_lista)
    frame_buscar.pack(fill="x", padx=5, pady=5)
    tk.Label(frame_buscar, text="Buscar:", font=("Arial", 10)).pack(side="left")
    entry_buscar = tk.Entry(frame_buscar, font=("Arial", 10), width=30)
    entry_buscar.pack(side="left", padx=5)

    columnas_servicios = ("ID", "Tipo", "Estado", "Precio")
    tree_servicios = ttk.Treeview(frame_lista, columns=columnas_servicios, show="headings", height=15)
    anchos = {"ID": 50, "Tipo": 350, "Estado": 120, "Precio": 120}
    for col in columnas_servicios:
        tree_servicios.heading(col, text=col)
        tree_servicios.column(col, width=anchos.get(col, 100))
    tree_servicios.pack(side="left", fill="both", expand=True, padx=5, pady=5)

    scroll_servicios = ttk.Scrollbar(frame_lista, orient="vertical", command=tree_servicios.yview)
    tree_servicios.configure(yscrollcommand=scroll_servicios.set)
    scroll_servicios.pack(side="right", fill="y")

    panel_derecho = tk.Frame(panel_principal)
    panel_principal.add(panel_derecho, width=500)

    frame_form = tk.LabelFrame(panel_derecho, text="Datos del Servicio", font=("Arial", 12, "bold"))
    frame_form.pack(fill="x", pady=5)

    tk.Label(frame_form, text="Tipo de Servicio *:", font=("Arial", 10)).grid(row=0, column=0, padx=5, pady=5, sticky="e")
    combo_tipo = ttk.Combobox(frame_form, font=("Arial", 10), width=38, values=list(precios_servicios.keys()))
    combo_tipo.grid(row=0, column=1, padx=5, pady=5, sticky="w")
    combo_tipo.set("Seleccione un servicio...")

    def actualizar_precio_automatico(*args):
        tipo = combo_tipo.get()
        if tipo in precios_servicios:
            entry_precio.delete(0, tk.END)
            entry_precio.insert(0, str(precios_servicios[tipo]))

    combo_tipo.bind("<<ComboboxSelected>>", actualizar_precio_automatico)

    tk.Label(frame_form, text="Estado:", font=("Arial", 10)).grid(row=1, column=0, padx=5, pady=5, sticky="e")
    combo_estado = ttk.Combobox(frame_form, font=("Arial", 10), width=38)
    combo_estado['values'] = ("ACTIVO", "INACTIVO", "EN MANTENIMIENTO")
    combo_estado.current(0)
    combo_estado.grid(row=1, column=1, padx=5, pady=5, sticky="w")

    tk.Label(frame_form, text="Precio Mensual (Q) *:", font=("Arial", 10)).grid(row=2, column=0, padx=5, pady=5, sticky="e")
    entry_precio = tk.Entry(frame_form, font=("Arial", 10), width=40)
    entry_precio.grid(row=2, column=1, padx=5, pady=5, sticky="w")

    frame_botones_form = tk.Frame(frame_form)
    frame_botones_form.grid(row=3, column=0, columnspan=2, pady=10)

    btn_guardar = tk.Button(frame_botones_form, text="Guardar Servicio", bg="#4CAF50", fg="white", width=12)
    btn_guardar.pack(side="left", padx=5)
    btn_actualizar = tk.Button(frame_botones_form, text="Actualizar Servicio", bg="#2196F3", fg="white", width=14, state="disabled")
    btn_actualizar.pack(side="left", padx=5)
    btn_eliminar = tk.Button(frame_botones_form, text="Eliminar Servicio", bg="#f44336", fg="white", width=12, state="disabled")
    btn_eliminar.pack(side="left", padx=5)
    btn_nuevo = tk.Button(frame_botones_form, text="Nuevo Servicio", bg="#FF9800", fg="white", width=12)
    btn_nuevo.pack(side="left", padx=5)

    btn_cerrar = tk.Button(panel_derecho, text="Cerrar", command=ventana.destroy, bg="#f44336", fg="white", width=15)
    btn_cerrar.pack(pady=10)

    def limpiar_formulario():
        combo_tipo.set("Seleccione un servicio...")
        combo_estado.current(0)
        entry_precio.delete(0, tk.END)
        combo_tipo.focus()
        btn_actualizar.config(state="disabled")
        btn_eliminar.config(state="disabled")
        servicio_seleccionado_id.set(0)

    def cargar_servicios(busqueda=""):
        for item in tree_servicios.get_children():
            tree_servicios.delete(item)
        if busqueda.isdigit():
            query = "SELECT id_servicio, tipo, estado, precio FROM servicio WHERE id_servicio = %s"
            params = (int(busqueda),)
            registros = ejecutar_query(query, params, fetch_all=True)
        elif busqueda:
            query = "SELECT id_servicio, tipo, estado, precio FROM servicio WHERE tipo LIKE %s"
            params = (f"%{busqueda}%",)
            registros = ejecutar_query(query, params, fetch_all=True)
        else:
            query = "SELECT id_servicio, tipo, estado, precio FROM servicio ORDER BY id_servicio DESC"
            registros = ejecutar_query(query, fetch_all=True)
        if registros:
            for reg in registros:
                tree_servicios.insert("", "end", values=(reg[0], reg[1], reg[2], f"Q{reg[3]:.2f}"))
        else:
            tree_servicios.insert("", "end", values=("No hay datos", "", "", ""))

    def guardar_servicio():
        tipo = combo_tipo.get().strip()
        estado = combo_estado.get()
        if tipo == "Seleccione un servicio..." or not tipo:
            messagebox.showwarning("Datos incompletos", "Seleccione un tipo de servicio válido")
            combo_tipo.focus()
            return
        try:
            precio = float(entry_precio.get().strip())
            if precio <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Datos inválidos", "Ingrese un precio válido mayor a 0")
            entry_precio.focus()
            return
        query = "INSERT INTO servicio (tipo, estado, precio) VALUES (%s, %s, %s)"
        resultado = ejecutar_query(query, (tipo, estado, precio), commit=True)
        if resultado:
            messagebox.showinfo("Éxito", f"Servicio '{tipo}' registrado")
            limpiar_formulario()
            cargar_servicios()
        else:
            messagebox.showerror("Error", "No se pudo guardar el servicio")

    def actualizar_servicio():
        id_servicio = servicio_seleccionado_id.get()
        if not id_servicio:
            messagebox.showwarning("Sin selección", "Seleccione un servicio de la lista")
            return
        tipo = combo_tipo.get().strip()
        estado = combo_estado.get()
        if tipo == "Seleccione un servicio..." or not tipo:
            messagebox.showwarning("Datos incompletos", "Seleccione un tipo de servicio válido")
            combo_tipo.focus()
            return
        try:
            precio = float(entry_precio.get().strip())
            if precio <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Datos inválidos", "Ingrese un precio válido mayor a 0")
            entry_precio.focus()
            return
        query = "UPDATE servicio SET tipo=%s, estado=%s, precio=%s WHERE id_servicio=%s"
        resultado = ejecutar_query(query, (tipo, estado, precio, id_servicio), commit=True)
        if resultado is not None:
            messagebox.showinfo("Éxito", "Servicio actualizado")
            cargar_servicios()
        else:
            messagebox.showerror("Error", "No se pudo actualizar")

    def eliminar_servicio():
        id_servicio = servicio_seleccionado_id.get()
        if not id_servicio:
            messagebox.showwarning("Sin selección", "Seleccione un servicio de la lista")
            return
        tipo = combo_tipo.get().strip()
        confirmar = messagebox.askyesno("Confirmar", f"¿Eliminar el servicio '{tipo}'?")
        if confirmar:
            ejecutar_query("DELETE FROM servicio WHERE id_servicio = %s", (id_servicio,), commit=True)
            messagebox.showinfo("Éxito", "Servicio eliminado")
            limpiar_formulario()
            cargar_servicios()

    def on_servicio_seleccionado(event):
        seleccion = tree_servicios.selection()
        if seleccion:
            valores = tree_servicios.item(seleccion[0])["values"]
            if valores[0] != "No hay datos":
                id_servicio = valores[0]
                servicio_seleccionado_id.set(id_servicio)
                query = "SELECT tipo, estado, precio FROM servicio WHERE id_servicio = %s"
                datos_servicio = ejecutar_query(query, (id_servicio,), fetch_one=True)
                if datos_servicio:
                    combo_tipo.set(datos_servicio[0] or "")
                    combo_estado.set(datos_servicio[1] or "ACTIVO")
                    entry_precio.delete(0, tk.END)
                    entry_precio.insert(0, str(datos_servicio[2]) if datos_servicio[2] else "")
                btn_actualizar.config(state="normal")
                btn_eliminar.config(state="normal")
        else:
            limpiar_formulario()

    def buscar_servicios():
        texto = entry_buscar.get().strip()
        cargar_servicios(texto)

    def limpiar_busqueda():
        entry_buscar.delete(0, tk.END)
        cargar_servicios()

    def nuevo_servicio():
        limpiar_formulario()

    btn_guardar.config(command=guardar_servicio)
    btn_actualizar.config(command=actualizar_servicio)
    btn_eliminar.config(command=eliminar_servicio)
    btn_nuevo.config(command=nuevo_servicio)
    btn_buscar = tk.Button(frame_buscar, text="Buscar", command=buscar_servicios, bg="#2196F3", fg="white")
    btn_buscar.pack(side="left", padx=5)
    btn_refrescar = tk.Button(frame_buscar, text="Refrescar", command=limpiar_busqueda, bg="#9E9E9E", fg="white")
    btn_refrescar.pack(side="left", padx=5)

    tree_servicios.bind("<<TreeviewSelect>>", on_servicio_seleccionado)
    entry_buscar.bind("<Return>", lambda e: buscar_servicios())

    cargar_servicios()

def ventana_asignar_servicio_cliente():
    ventana = tk.Toplevel()
    ventana.title("Asignar Servicio a Cliente")
    ventana.attributes('-fullscreen', True)
    ventana.transient()
    ventana.grab_set()
    ventana.bind("<Escape>", lambda e: ventana.destroy())

    panel_principal = tk.PanedWindow(ventana, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, sashwidth=5)
    panel_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    frame_clientes = tk.LabelFrame(panel_principal, text="Clientes Registrados", font=("Arial", 12, "bold"))
    panel_principal.add(frame_clientes, width=600)

    frame_buscar = tk.Frame(frame_clientes)
    frame_buscar.pack(fill="x", padx=5, pady=5)
    tk.Label(frame_buscar, text="Buscar Cliente:", font=("Arial", 10)).pack(side="left")
    entry_buscar = tk.Entry(frame_buscar, font=("Arial", 10), width=30)
    entry_buscar.pack(side="left", padx=5)

    columnas_clientes = ("ID", "Nombre", "Apellido", "DPI", "Teléfono")
    tree_clientes = ttk.Treeview(frame_clientes, columns=columnas_clientes, show="headings", height=18)
    anchos = {"ID": 50, "Nombre": 150, "Apellido": 150, "DPI": 120, "Teléfono": 120}
    for col in columnas_clientes:
        tree_clientes.heading(col, text=col)
        tree_clientes.column(col, width=anchos.get(col, 100))
    tree_clientes.pack(side="left", fill="both", expand=True, padx=5, pady=5)

    scroll_clientes = ttk.Scrollbar(frame_clientes, orient="vertical", command=tree_clientes.yview)
    tree_clientes.configure(yscrollcommand=scroll_clientes.set)
    scroll_clientes.pack(side="right", fill="y")

    panel_derecho = tk.Frame(panel_principal)
    panel_principal.add(panel_derecho, width=500)

    frame_detalle = tk.LabelFrame(panel_derecho, text="Asignar Servicio", font=("Arial", 12, "bold"))
    frame_detalle.pack(fill="both", expand=True, pady=5)

    tk.Label(frame_detalle, text="Cliente seleccionado:", font=("Arial", 11, "bold")).pack(pady=5)
    lbl_cliente = tk.Label(frame_detalle, text="Ninguno", font=("Arial", 11), fg="blue")
    lbl_cliente.pack(pady=5)

    tk.Label(frame_detalle, text="Seleccione un servicio:", font=("Arial", 11, "bold")).pack(pady=10)
    combo_servicios = ttk.Combobox(frame_detalle, font=("Arial", 11), width=40)
    combo_servicios.pack(pady=5)

    tk.Label(frame_detalle, text="Estado del servicio:", font=("Arial", 11, "bold")).pack(pady=5)
    combo_estado = ttk.Combobox(frame_detalle, font=("Arial", 11), width=40)
    combo_estado['values'] = ("ACTIVO", "SUSPENDIDO", "CANCELADO")
    combo_estado.current(0)
    combo_estado.pack(pady=5)

    frame_botones = tk.Frame(frame_detalle)
    frame_botones.pack(pady=20)

    btn_asignar = tk.Button(frame_botones, text="Asignar Servicio", bg="#4CAF50", fg="white", font=("Arial", 11), width=20)
    btn_asignar.pack(side="left", padx=5)

    btn_ver_asignaciones = tk.Button(frame_botones, text="Ver Servicios del Cliente", bg="#2196F3", fg="white", font=("Arial", 11), width=22)
    btn_ver_asignaciones.pack(side="left", padx=5)

    btn_cerrar = tk.Button(frame_detalle, text="Cerrar", command=ventana.destroy, bg="#f44336", fg="white", width=15)
    btn_cerrar.pack(pady=10)

    cliente_seleccionado_id = tk.IntVar()
    cliente_seleccionado_nombre = tk.StringVar()
    servicios_data = []

    def cargar_clientes(busqueda=""):
        for item in tree_clientes.get_children():
            tree_clientes.delete(item)
        if busqueda.isdigit():
            query = "SELECT id_cliente, nombre, apellido, dpi FROM cliente WHERE id_cliente = %s"
            params = (int(busqueda),)
            registros = ejecutar_query(query, params, fetch_all=True)
        elif busqueda:
            query = "SELECT id_cliente, nombre, apellido, dpi FROM cliente WHERE nombre LIKE %s OR apellido LIKE %s OR dpi LIKE %s"
            params = (f"%{busqueda}%", f"%{busqueda}%", f"%{busqueda}%")
            registros = ejecutar_query(query, params, fetch_all=True)
        else:
            query = "SELECT id_cliente, nombre, apellido, dpi FROM cliente ORDER BY id_cliente DESC"
            registros = ejecutar_query(query, fetch_all=True)
        if registros:
            for reg in registros:
                tree_clientes.insert("", "end", values=(reg[0], reg[1], reg[2], reg[3], ""))
        else:
            tree_clientes.insert("", "end", values=("No hay datos", "", "", "", ""))

    def cargar_servicios():
        nonlocal servicios_data
        query = "SELECT id_servicio, tipo, precio FROM servicio WHERE estado = 'ACTIVO' ORDER BY tipo"
        servicios_data = ejecutar_query(query, fetch_all=True) or []
        combo_servicios['values'] = [f"{s[0]} - {s[1]} (Q{s[2]:.2f})" for s in servicios_data]

    def on_cliente_seleccionado(event):
        seleccion = tree_clientes.selection()
        if seleccion:
            valores = tree_clientes.item(seleccion[0])["values"]
            if valores[0] != "No hay datos":
                id_cliente = valores[0]
                cliente_seleccionado_id.set(id_cliente)
                cliente_seleccionado_nombre.set(f"{valores[1]} {valores[2]}")
                lbl_cliente.config(text=f"{cliente_seleccionado_nombre.get()} (ID: {id_cliente})")

    def asignar_servicio():
        id_cliente = cliente_seleccionado_id.get()
        if not id_cliente:
            messagebox.showwarning("Sin selección", "Seleccione un cliente de la lista")
            return
        seleccion = combo_servicios.current()
        if seleccion < 0 or not servicios_data:
            messagebox.showwarning("Sin selección", "Seleccione un servicio")
            return
        id_servicio = servicios_data[seleccion][0]
        estado = combo_estado.get()
        query = "INSERT INTO cliente_servico (id_cliente, servicio_id) VALUES (%s, %s)"
        resultado = ejecutar_query(query, (id_cliente, id_servicio), commit=True)
        if resultado:
            messagebox.showinfo("Éxito", f"Servicio asignado a {cliente_seleccionado_nombre.get()}")
        else:
            messagebox.showerror("Error", "No se pudo asignar el servicio")

    def ver_asignaciones():
        id_cliente = cliente_seleccionado_id.get()
        if not id_cliente:
            messagebox.showwarning("Sin selección", "Seleccione un cliente de la lista")
            return
        query = """
            SELECT s.id_servicio, s.tipo, s.precio
            FROM cliente_servico cs
            JOIN servicio s ON cs.servicio_id = s.id_servicio
            WHERE cs.id_cliente = %s
        """
        asignaciones = ejecutar_query(query, (id_cliente,), fetch_all=True)
        if asignaciones:
            msg = f"Servicios de {cliente_seleccionado_nombre.get()}:\n\n"
            for a in asignaciones:
                msg += f"ID: {a[0]} - {a[1]} (Q{a[2]:.2f})\n"
            messagebox.showinfo("Servicios del Cliente", msg)
        else:
            messagebox.showinfo("Servicios del Cliente", f"{cliente_seleccionado_nombre.get()} no tiene servicios asignados")

    def buscar_clientes_btn():
        texto = entry_buscar.get().strip()
        cargar_clientes(texto)

    def limpiar_busqueda():
        entry_buscar.delete(0, tk.END)
        cargar_clientes()

    btn_buscar = tk.Button(frame_buscar, text="Buscar", command=buscar_clientes_btn, bg="#2196F3", fg="white")
    btn_buscar.pack(side="left", padx=5)
    btn_refrescar = tk.Button(frame_buscar, text="Refrescar", command=limpiar_busqueda, bg="#9E9E9E", fg="white")
    btn_refrescar.pack(side="left", padx=5)

    tree_clientes.bind("<<TreeviewSelect>>", on_cliente_seleccionado)
    entry_buscar.bind("<Return>", lambda e: buscar_clientes_btn())
    btn_asignar.config(command=asignar_servicio)
    btn_ver_asignaciones.config(command=ver_asignaciones)

    cargar_clientes()
    cargar_servicios()

def ventana_ordenes_trabajo_admin():
    ventana = tk.Toplevel()
    ventana.title("Órdenes de Trabajo - Admin (CRUD)")
    ventana.attributes('-fullscreen', True)
    ventana.transient()
    ventana.grab_set()
    ventana.bind("<Escape>", lambda e: ventana.destroy())

    orden_seleccionado_id = tk.IntVar()

    panel_principal = tk.PanedWindow(ventana, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, sashwidth=5)
    panel_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    frame_lista = tk.LabelFrame(panel_principal, text="Órdenes de Trabajo", font=("Arial", 12, "bold"))
    panel_principal.add(frame_lista, width=600)

    frame_buscar = tk.Frame(frame_lista)
    frame_buscar.pack(fill="x", padx=5, pady=5)
    tk.Label(frame_buscar, text="Buscar:", font=("Arial", 10)).pack(side="left")
    entry_buscar = tk.Entry(frame_buscar, font=("Arial", 10), width=30)
    entry_buscar.pack(side="left", padx=5)

    columnas_ordenes = ("ID", "Cliente", "Fecha", "Estado")
    tree_ordenes = ttk.Treeview(frame_lista, columns=columnas_ordenes, show="headings", height=15)
    anchos = {"ID": 50, "Cliente": 250, "Fecha": 120, "Estado": 120}
    for col in columnas_ordenes:
        tree_ordenes.heading(col, text=col)
        tree_ordenes.column(col, width=anchos.get(col, 100))
    tree_ordenes.pack(side="left", fill="both", expand=True, padx=5, pady=5)

    scroll_ordenes = ttk.Scrollbar(frame_lista, orient="vertical", command=tree_ordenes.yview)
    tree_ordenes.configure(yscrollcommand=scroll_ordenes.set)
    scroll_ordenes.pack(side="right", fill="y")

    panel_derecho = tk.Frame(panel_principal)
    panel_principal.add(panel_derecho, width=500)

    frame_form = tk.LabelFrame(panel_derecho, text="Datos de la Orden", font=("Arial", 12, "bold"))
    frame_form.pack(fill="x", pady=5)

    tk.Label(frame_form, text="Cliente *:", font=("Arial", 10)).grid(row=0, column=0, padx=5, pady=5, sticky="e")
    combo_cliente = ttk.Combobox(frame_form, font=("Arial", 10), width=38)
    combo_cliente.grid(row=0, column=1, padx=5, pady=5, sticky="w")

    tk.Label(frame_form, text="Fecha:", font=("Arial", 10)).grid(row=1, column=0, padx=5, pady=5, sticky="e")
    entry_fecha = tk.Entry(frame_form, font=("Arial", 10), width=38)
    entry_fecha.grid(row=1, column=1, padx=5, pady=5, sticky="w")
    from datetime import datetime
    entry_fecha.insert(0, datetime.now().strftime("%Y-%m-%d"))

    tk.Label(frame_form, text="Estado:", font=("Arial", 10)).grid(row=2, column=0, padx=5, pady=5, sticky="e")
    combo_estado = ttk.Combobox(frame_form, font=("Arial", 10), width=38)
    combo_estado['values'] = ("PENDIENTE", "EN PROCESO", "COMPLETADA", "CANCELADA")
    combo_estado.current(0)
    combo_estado.grid(row=2, column=1, padx=5, pady=5, sticky="w")

    frame_botones_form = tk.Frame(frame_form)
    frame_botones_form.grid(row=3, column=0, columnspan=2, pady=10)

    btn_guardar = tk.Button(frame_botones_form, text="Guardar Orden", bg="#4CAF50", fg="white", width=12)
    btn_guardar.pack(side="left", padx=5)
    btn_actualizar = tk.Button(frame_botones_form, text="Actualizar Orden", bg="#2196F3", fg="white", width=14, state="disabled")
    btn_actualizar.pack(side="left", padx=5)
    btn_eliminar = tk.Button(frame_botones_form, text="Eliminar Orden", bg="#f44336", fg="white", width=12, state="disabled")
    btn_eliminar.pack(side="left", padx=5)
    btn_nuevo = tk.Button(frame_botones_form, text="Nueva Orden", bg="#FF9800", fg="white", width=12)
    btn_nuevo.pack(side="left", padx=5)

    btn_cerrar = tk.Button(panel_derecho, text="Cerrar", command=ventana.destroy, bg="#f44336", fg="white", width=15)
    btn_cerrar.pack(pady=10)

    clientes_data = []

    def cargar_clientes():
        nonlocal clientes_data
        query = "SELECT id_cliente, nombre, apellido FROM cliente ORDER BY nombre"
        clientes_data = ejecutar_query(query, fetch_all=True) or []
        combo_cliente['values'] = [f"{c[0]} - {c[1]} {c[2]}" for c in clientes_data]

    def limpiar_formulario():
        combo_cliente.set("")
        entry_fecha.delete(0, tk.END)
        entry_fecha.insert(0, datetime.now().strftime("%Y-%m-%d"))
        combo_estado.current(0)
        btn_actualizar.config(state="disabled")
        btn_eliminar.config(state="disabled")
        orden_seleccionado_id.set(0)

    def cargar_ordenes(busqueda=""):
        for item in tree_ordenes.get_children():
            tree_ordenes.delete(item)
        if busqueda.isdigit():
            query = """
                SELECT o.id_orden, c.nombre, c.apellido, o.fecha, o.estado
                FROM orden_instalacion o
                JOIN cliente c ON o.id_cliente = c.id_cliente
                WHERE o.id_orden = %s
            """
            params = (int(busqueda),)
            registros = ejecutar_query(query, params, fetch_all=True)
        elif busqueda:
            query = """
                SELECT o.id_orden, c.nombre, c.apellido, o.fecha, o.estado
                FROM orden_instalacion o
                JOIN cliente c ON o.id_cliente = c.id_cliente
                WHERE c.nombre LIKE %s OR c.apellido LIKE %s
            """
            params = (f"%{busqueda}%", f"%{busqueda}%")
            registros = ejecutar_query(query, params, fetch_all=True)
        else:
            query = """
                SELECT o.id_orden, c.nombre, c.apellido, o.fecha, o.estado
                FROM orden_instalacion o
                JOIN cliente c ON o.id_cliente = c.id_cliente
                ORDER BY o.id_orden DESC
            """
            registros = ejecutar_query(query, fetch_all=True)
        if registros:
            for reg in registros:
                tree_ordenes.insert("", "end", values=(reg[0], f"{reg[1]} {reg[2]}", reg[3], reg[4]))
        else:
            tree_ordenes.insert("", "end", values=("No hay datos", "", "", ""))

    def guardar_orden():
        seleccion = combo_cliente.current()
        if seleccion < 0 or not clientes_data:
            messagebox.showwarning("Datos incompletos", "Seleccione un cliente")
            combo_cliente.focus()
            return
        id_cliente = clientes_data[seleccion][0]
        fecha = entry_fecha.get().strip()
        estado = combo_estado.get()
        if not fecha:
            fecha = datetime.now().strftime("%Y-%m-%d")
        query = "INSERT INTO orden_instalacion (id_cliente, fecha, estado) VALUES (%s, %s, %s)"
        resultado = ejecutar_query(query, (id_cliente, fecha, estado), commit=True)
        if resultado:
            messagebox.showinfo("Éxito", f"Orden de trabajo creada")
            limpiar_formulario()
            cargar_ordenes()
        else:
            messagebox.showerror("Error", "No se pudo guardar la orden")

    def actualizar_orden():
        id_orden = orden_seleccionado_id.get()
        if not id_orden:
            messagebox.showwarning("Sin selección", "Seleccione una orden de la lista")
            return
        seleccion = combo_cliente.current()
        if seleccion < 0 or not clientes_data:
            messagebox.showwarning("Datos incompletos", "Seleccione un cliente")
            return
        id_cliente = clientes_data[seleccion][0]
        fecha = entry_fecha.get().strip()
        estado = combo_estado.get()
        query = "UPDATE orden_instalacion SET id_cliente=%s, fecha=%s, estado=%s WHERE id_orden=%s"
        resultado = ejecutar_query(query, (id_cliente, fecha, estado, id_orden), commit=True)
        if resultado is not None:
            messagebox.showinfo("Éxito", "Orden actualizada")
            cargar_ordenes()
        else:
            messagebox.showerror("Error", "No se pudo actualizar")

    def eliminar_orden():
        id_orden = orden_seleccionado_id.get()
        if not id_orden:
            messagebox.showwarning("Sin selección", "Seleccione una orden de la lista")
            return
        confirmar = messagebox.askyesno("Confirmar", f"¿Eliminar la orden #{id_orden}?")
        if confirmar:
            ejecutar_query("DELETE FROM orden_instalacion WHERE id_orden = %s", (id_orden,), commit=True)
            messagebox.showinfo("Éxito", "Orden eliminada")
            limpiar_formulario()
            cargar_ordenes()

    def on_orden_seleccionado(event):
        seleccion = tree_ordenes.selection()
        if seleccion:
            valores = tree_ordenes.item(seleccion[0])["values"]
            if valores[0] != "No hay datos":
                id_orden = valores[0]
                orden_seleccionado_id.set(id_orden)
                query = "SELECT id_cliente, fecha, estado FROM orden_instalacion WHERE id_orden = %s"
                datos_orden = ejecutar_query(query, (id_orden,), fetch_one=True)
                if datos_orden:
                    id_cliente = datos_orden[0]
                    for i, c in enumerate(clientes_data):
                        if c[0] == id_cliente:
                            combo_cliente.current(i)
                            break
                    entry_fecha.delete(0, tk.END)
                    entry_fecha.insert(0, datos_orden[1] or "")
                    combo_estado.set(datos_orden[2] or "PENDIENTE")
                btn_actualizar.config(state="normal")
                btn_eliminar.config(state="normal")
        else:
            limpiar_formulario()

    def buscar_ordenes():
        texto = entry_buscar.get().strip()
        cargar_ordenes(texto)

    def limpiar_busqueda():
        entry_buscar.delete(0, tk.END)
        cargar_ordenes()

    def nuevo_orden():
        limpiar_formulario()

    btn_guardar.config(command=guardar_orden)
    btn_actualizar.config(command=actualizar_orden)
    btn_eliminar.config(command=eliminar_orden)
    btn_nuevo.config(command=nuevo_orden)
    btn_buscar = tk.Button(frame_buscar, text="Buscar", command=buscar_ordenes, bg="#2196F3", fg="white")
    btn_buscar.pack(side="left", padx=5)
    btn_refrescar = tk.Button(frame_buscar, text="Refrescar", command=limpiar_busqueda, bg="#9E9E9E", fg="white")
    btn_refrescar.pack(side="left", padx=5)

    tree_ordenes.bind("<<TreeviewSelect>>", on_orden_seleccionado)
    entry_buscar.bind("<Return>", lambda e: buscar_ordenes())

    cargar_clientes()
    cargar_ordenes()

def ventana_ordenes_trabajo_tecnico():
    ventana = tk.Toplevel()
    ventana.title("Órdenes de Trabajo - Cable Internet (Técnico)")
    ventana.attributes('-fullscreen', True)
    ventana.transient()
    ventana.grab_set()
    ventana.bind("<Escape>", lambda e: ventana.destroy())

    panel_principal = tk.PanedWindow(ventana, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, sashwidth=5)
    panel_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    frame_lista = tk.LabelFrame(panel_principal, text="Órdenes de Trabajo", font=("Arial", 12, "bold"))
    panel_principal.add(frame_lista, width=600)

    frame_buscar = tk.Frame(frame_lista)
    frame_buscar.pack(fill="x", padx=5, pady=5)
    tk.Label(frame_buscar, text="Buscar:", font=("Arial", 10)).pack(side="left")
    entry_buscar = tk.Entry(frame_buscar, font=("Arial", 10), width=30)
    entry_buscar.pack(side="left", padx=5)

    columnas_ordenes = ("ID", "Cliente", "Dirección", "Fecha", "Estado")
    tree_ordenes = ttk.Treeview(frame_lista, columns=columnas_ordenes, show="headings", height=18)
    anchos = {"ID": 50, "Cliente": 200, "Dirección": 280, "Fecha": 100, "Estado": 100}
    for col in columnas_ordenes:
        tree_ordenes.heading(col, text=col)
        tree_ordenes.column(col, width=anchos.get(col, 100))
    tree_ordenes.pack(side="left", fill="both", expand=True, padx=5, pady=5)

    scroll_ordenes = ttk.Scrollbar(frame_lista, orient="vertical", command=tree_ordenes.yview)
    tree_ordenes.configure(yscrollcommand=scroll_ordenes.set)
    scroll_ordenes.pack(side="right", fill="y")

    panel_derecho = tk.Frame(panel_principal)
    panel_principal.add(panel_derecho, width=500)

    frame_detalle = tk.LabelFrame(panel_derecho, text="Detalle de la Orden", font=("Arial", 12, "bold"))
    frame_detalle.pack(fill="both", expand=True, pady=5)

    texto_detalle = tk.Text(frame_detalle, font=("Arial", 11), wrap="word", height=20)
    texto_detalle.pack(fill="both", expand=True, padx=10, pady=10)

    btn_cerrar = tk.Button(panel_derecho, text="Cerrar", command=ventana.destroy, bg="#f44336", fg="white", width=15)
    btn_cerrar.pack(pady=10)

    def cargar_ordenes(busqueda=""):
        for item in tree_ordenes.get_children():
            tree_ordenes.delete(item)
        if busqueda.isdigit():
            query = """
                SELECT o.id_orden, c.nombre, c.apellido, 
                       CONCAT(c.barrio, ', Zona ', c.zona, ', ', c.calle, ' ', c.num_casa) as direccion,
                       o.fecha, o.estado
                FROM orden_instalacion o
                JOIN cliente c ON o.id_cliente = c.id_cliente
                WHERE o.id_orden = %s
            """
            params = (int(busqueda),)
            registros = ejecutar_query(query, params, fetch_all=True)
        elif busqueda:
            query = """
                SELECT o.id_orden, c.nombre, c.apellido,
                       CONCAT(c.barrio, ', Zona ', c.zona, ', ', c.calle, ' ', c.num_casa) as direccion,
                       o.fecha, o.estado
                FROM orden_instalacion o
                JOIN cliente c ON o.id_cliente = c.id_cliente
                WHERE c.nombre LIKE %s OR c.apellido LIKE %s
            """
            params = (f"%{busqueda}%", f"%{busqueda}%")
            registros = ejecutar_query(query, params, fetch_all=True)
        else:
            query = """
                SELECT o.id_orden, c.nombre, c.apellido,
                       CONCAT(c.barrio, ', Zona ', c.zona, ', ', c.calle, ' ', c.num_casa) as direccion,
                       o.fecha, o.estado
                FROM orden_instalacion o
                JOIN cliente c ON o.id_cliente = c.id_cliente
                ORDER BY o.id_orden DESC
            """
            registros = ejecutar_query(query, fetch_all=True)
        if registros:
            for reg in registros:
                tree_ordenes.insert("", "end", values=(reg[0], f"{reg[1]} {reg[2]}", reg[3], reg[4], reg[5]))
        else:
            tree_ordenes.insert("", "end", values=("No hay datos", "", "", "", ""))

    def mostrar_detalle(event):
        seleccion = tree_ordenes.selection()
        if seleccion:
            valores = tree_ordenes.item(seleccion[0])["values"]
            if valores[0] != "No hay datos":
                id_orden = valores[0]
                query = """
                    SELECT o.id_orden, c.nombre, c.apellido, c.dpi,
                           c.barrio, c.zona, c.calle, c.num_casa,
                           o.fecha, o.estado
                    FROM orden_instalacion o
                    JOIN cliente c ON o.id_cliente = c.id_cliente
                    WHERE o.id_orden = %s
                """
                datos = ejecutar_query(query, (id_orden,), fetch_one=True)
                if datos:
                    detalle = f"""
=== ORDEN DE TRABAJO #{datos[0]} ===

DATOS DEL CLIENTE:
Nombre: {datos[1]} {datos[2]}
DPI: {datos[3]}
Dirección: {datos[4]}, Zona {datos[5]}, {datos[6]} {datos[7]}

DATOS DE LA ORDEN:
Fecha: {datos[8]}
Estado: {datos[9]}
                    """
                    texto_detalle.delete(1.0, tk.END)
                    texto_detalle.insert(1.0, detalle)
                else:
                    texto_detalle.delete(1.0, tk.END)
                    texto_detalle.insert(1.0, "No se pudo cargar el detalle")

    def buscar_ordenes():
        texto = entry_buscar.get().strip()
        cargar_ordenes(texto)

    def limpiar_busqueda():
        entry_buscar.delete(0, tk.END)
        cargar_ordenes()

    btn_buscar = tk.Button(frame_buscar, text="Buscar", command=buscar_ordenes, bg="#2196F3", fg="white")
    btn_buscar.pack(side="left", padx=5)
    btn_refrescar = tk.Button(frame_buscar, text="Refrescar", command=limpiar_busqueda, bg="#9E9E9E", fg="white")
    btn_refrescar.pack(side="left", padx=5)

    tree_ordenes.bind("<<TreeviewSelect>>", mostrar_detalle)
    entry_buscar.bind("<Return>", lambda e: buscar_ordenes())

    cargar_ordenes()

def ventana_instalaciones_tecnico():
    ventana = tk.Toplevel()
    ventana.title("Mis Instalaciones Asignadas - Cable Internet")
    ventana.attributes('-fullscreen', True)
    ventana.transient()
    ventana.grab_set()
    ventana.bind("<Escape>", lambda e: ventana.destroy())

    instalacion_seleccionado_id = tk.IntVar()

    panel_principal = tk.PanedWindow(ventana, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, sashwidth=5)
    panel_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    frame_lista = tk.LabelFrame(panel_principal, text="Instalaciones Asignadas", font=("Arial", 12, "bold"))
    panel_principal.add(frame_lista, width=600)

    frame_buscar = tk.Frame(frame_lista)
    frame_buscar.pack(fill="x", padx=5, pady=5)
    tk.Label(frame_buscar, text="Buscar:", font=("Arial", 10)).pack(side="left")
    entry_buscar = tk.Entry(frame_buscar, font=("Arial", 10), width=30)
    entry_buscar.pack(side="left", padx=5)

    columnas_instalaciones = ("ID", "Cliente", "Dirección", "Fecha", "Estado")
    tree_instalaciones = ttk.Treeview(frame_lista, columns=columnas_instalaciones, show="headings", height=18)
    anchos = {"ID": 50, "Cliente": 200, "Dirección": 280, "Fecha": 100, "Estado": 100}
    for col in columnas_instalaciones:
        tree_instalaciones.heading(col, text=col)
        tree_instalaciones.column(col, width=anchos.get(col, 100))
    tree_instalaciones.pack(side="left", fill="both", expand=True, padx=5, pady=5)

    scroll_instalaciones = ttk.Scrollbar(frame_lista, orient="vertical", command=tree_instalaciones.yview)
    tree_instalaciones.configure(yscrollcommand=scroll_instalaciones.set)
    scroll_instalaciones.pack(side="right", fill="y")

    panel_derecho = tk.Frame(panel_principal)
    panel_principal.add(panel_derecho, width=500)

    frame_detalle = tk.LabelFrame(panel_derecho, text="Detalle de la Instalación", font=("Arial", 12, "bold"))
    frame_detalle.pack(fill="both", expand=True, pady=5)

    texto_detalle = tk.Text(frame_detalle, font=("Arial", 11), wrap="word", height=12)
    texto_detalle.pack(fill="both", expand=True, padx=10, pady=10)

    frame_estado = tk.LabelFrame(panel_derecho, text="Cambiar Estado", font=("Arial", 12, "bold"))
    frame_estado.pack(fill="x", pady=5)

    tk.Label(frame_estado, text="Nuevo Estado:", font=("Arial", 11)).pack(side="left", padx=10, pady=10)
    combo_estado = ttk.Combobox(frame_estado, font=("Arial", 11), width=25)
    combo_estado['values'] = ("PENDIENTE", "EN PROCESO", "COMPLETADA", "CANCELADA")
    combo_estado.current(0)
    combo_estado.pack(side="left", padx=10, pady=10)

    btn_actualizar_estado = tk.Button(frame_estado, text="Actualizar Estado", bg="#2196F3", fg="white", font=("Arial", 11), width=18)
    btn_actualizar_estado.pack(side="left", padx=10, pady=10)

    btn_cerrar = tk.Button(panel_derecho, text="Cerrar", command=ventana.destroy, bg="#f44336", fg="white", width=15)
    btn_cerrar.pack(pady=10)

    def cargar_instalaciones(busqueda=""):
        for item in tree_instalaciones.get_children():
            tree_instalaciones.delete(item)
        if busqueda.isdigit():
            query = """
                SELECT i.id_instalacion, c.nombre, c.apellido, 
                       CONCAT(c.barrio, ', Zona ', c.zona, ', ', c.calle, ' ', c.num_casa) as direccion,
                       i.fecha, i.estado
                FROM instalacion i
                JOIN orden_instalacion o ON i.id_orden_instalacion = o.id_orden
                JOIN cliente c ON o.id_cliente = c.id_cliente
                WHERE i.id_instalacion = %s
            """
            params = (int(busqueda),)
            registros = ejecutar_query(query, params, fetch_all=True)
        elif busqueda:
            query = """
                SELECT i.id_instalacion, c.nombre, c.apellido,
                       CONCAT(c.barrio, ', Zona ', c.zona, ', ', c.calle, ' ', c.num_casa) as direccion,
                       i.fecha, i.estado
                FROM instalacion i
                JOIN orden_instalacion o ON i.id_orden_instalacion = o.id_orden
                JOIN cliente c ON o.id_cliente = c.id_cliente
                WHERE c.nombre LIKE %s OR c.apellido LIKE %s
            """
            params = (f"%{busqueda}%", f"%{busqueda}%")
            registros = ejecutar_query(query, params, fetch_all=True)
        else:
            query = """
                SELECT i.id_instalacion, c.nombre, c.apellido,
                       CONCAT(c.barrio, ', Zona ', c.zona, ', ', c.calle, ' ', c.num_casa) as direccion,
                       i.fecha, i.estado
                FROM instalacion i
                JOIN orden_instalacion o ON i.id_orden_instalacion = o.id_orden
                JOIN cliente c ON o.id_cliente = c.id_cliente
                ORDER BY i.fecha DESC
            """
            registros = ejecutar_query(query, fetch_all=True)
        if registros:
            for reg in registros:
                tree_instalaciones.insert("", "end", values=(reg[0], f"{reg[1]} {reg[2]}", reg[3], reg[4], reg[5]))
        else:
            tree_instalaciones.insert("", "end", values=("No hay datos", "", "", "", ""))

    def mostrar_detalle(event):
        seleccion = tree_instalaciones.selection()
        if seleccion:
            valores = tree_instalaciones.item(seleccion[0])["values"]
            if valores[0] != "No hay datos":
                id_instalacion = valores[0]
                instalacion_seleccionado_id.set(id_instalacion)
                query = """
                    SELECT i.id_instalacion, c.nombre, c.apellido, c.dpi,
                           c.barrio, c.zona, c.calle, c.num_casa,
                           i.fecha, i.estado, o.id_orden
                    FROM instalacion i
                    JOIN orden_instalacion o ON i.id_orden_instalacion = o.id_orden
                    JOIN cliente c ON o.id_cliente = c.id_cliente
                    WHERE i.id_instalacion = %s
                """
                datos = ejecutar_query(query, (id_instalacion,), fetch_one=True)
                if datos:
                    detalle = f"""
=== INSTALACIÓN #{datos[0]} ===

DATOS DEL CLIENTE:
Nombre: {datos[1]} {datos[2]}
DPI: {datos[3]}
Dirección: {datos[4]}, Zona {datos[5]}, {datos[6]} {datos[7]}

DATOS DE LA INSTALACIÓN:
Fecha: {datos[8]}
Estado actual: {datos[9]}
Orden de Trabajo #: {datos[10]}
                    """
                    texto_detalle.delete(1.0, tk.END)
                    texto_detalle.insert(1.0, detalle)
                    combo_estado.set(datos[9] or "PENDIENTE")
                else:
                    texto_detalle.delete(1.0, tk.END)
                    texto_detalle.insert(1.0, "No se pudo cargar el detalle")
        else:
            instalacion_seleccionado_id.set(0)
            texto_detalle.delete(1.0, tk.END)
            combo_estado.set("PENDIENTE")

    def actualizar_estado():
        id_instalacion = instalacion_seleccionado_id.get()
        if not id_instalacion:
            messagebox.showwarning("Sin selección", "Seleccione una instalación de la lista")
            return
        nuevo_estado = combo_estado.get()
        query = "UPDATE instalacion SET estado = %s WHERE id_instalacion = %s"
        resultado = ejecutar_query(query, (nuevo_estado, id_instalacion), commit=True)
        if resultado is not None:
            messagebox.showinfo("Éxito", f"Estado de instalación #{id_instalacion} actualizado a '{nuevo_estado}'")
            cargar_instalaciones()
            mostrar_detalle(None)
        else:
            messagebox.showerror("Error", "No se pudo actualizar el estado")

    def buscar_instalaciones():
        texto = entry_buscar.get().strip()
        cargar_instalaciones(texto)

    def limpiar_busqueda():
        entry_buscar.delete(0, tk.END)
        cargar_instalaciones()

    btn_buscar = tk.Button(frame_buscar, text="Buscar", command=buscar_instalaciones, bg="#2196F3", fg="white")
    btn_buscar.pack(side="left", padx=5)
    btn_refrescar = tk.Button(frame_buscar, text="Refrescar", command=limpiar_busqueda, bg="#9E9E9E", fg="white")
    btn_refrescar.pack(side="left", padx=5)

    tree_instalaciones.bind("<<TreeviewSelect>>", mostrar_detalle)
    entry_buscar.bind("<Return>", lambda e: buscar_instalaciones())
    btn_actualizar_estado.config(command=actualizar_estado)

    cargar_instalaciones()

def ventana_chequeos_tecnico():
    ventana = tk.Toplevel()
    ventana.title("Mis Chequeos Asignados - Cable Internet")
    ventana.attributes('-fullscreen', True)
    ventana.transient()
    ventana.grab_set()
    ventana.bind("<Escape>", lambda e: ventana.destroy())

    chequeo_seleccionado_id = tk.IntVar()

    panel_principal = tk.PanedWindow(ventana, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, sashwidth=5)
    panel_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    frame_lista = tk.LabelFrame(panel_principal, text="Chequeos Asignados", font=("Arial", 12, "bold"))
    panel_principal.add(frame_lista, width=600)

    frame_buscar = tk.Frame(frame_lista)
    frame_buscar.pack(fill="x", padx=5, pady=5)
    tk.Label(frame_buscar, text="Buscar:", font=("Arial", 10)).pack(side="left")
    entry_buscar = tk.Entry(frame_buscar, font=("Arial", 10), width=30)
    entry_buscar.pack(side="left", padx=5)

    columnas_chequeos = ("ID", "Cliente", "Servicio", "Observaciones", "Estado")
    tree_chequeos = ttk.Treeview(frame_lista, columns=columnas_chequeos, show="headings", height=18)
    anchos = {"ID": 50, "Cliente": 200, "Servicio": 180, "Observaciones": 200, "Estado": 100}
    for col in columnas_chequeos:
        tree_chequeos.heading(col, text=col)
        tree_chequeos.column(col, width=anchos.get(col, 100))
    tree_chequeos.pack(side="left", fill="both", expand=True, padx=5, pady=5)

    scroll_chequeos = ttk.Scrollbar(frame_lista, orient="vertical", command=tree_chequeos.yview)
    tree_chequeos.configure(yscrollcommand=scroll_chequeos.set)
    scroll_chequeos.pack(side="right", fill="y")

    panel_derecho = tk.Frame(panel_principal)
    panel_principal.add(panel_derecho, width=500)

    frame_detalle = tk.LabelFrame(panel_derecho, text="Detalle del Chequeo", font=("Arial", 12, "bold"))
    frame_detalle.pack(fill="both", expand=True, pady=5)

    texto_detalle = tk.Text(frame_detalle, font=("Arial", 11), wrap="word", height=12)
    texto_detalle.pack(fill="both", expand=True, padx=10, pady=10)

    frame_estado = tk.LabelFrame(panel_derecho, text="Cambiar Estado", font=("Arial", 12, "bold"))
    frame_estado.pack(fill="x", pady=5)

    tk.Label(frame_estado, text="Nuevo Estado:", font=("Arial", 11)).pack(side="left", padx=10, pady=10)
    combo_estado = ttk.Combobox(frame_estado, font=("Arial", 11), width=25)
    combo_estado['values'] = ("PENDIENTE", "EN PROCESO", "COMPLETADO", "CANCELADO")
    combo_estado.current(0)
    combo_estado.pack(side="left", padx=10, pady=10)

    frame_observaciones = tk.LabelFrame(panel_derecho, text="Agregar Observación", font=("Arial", 12, "bold"))
    frame_observaciones.pack(fill="x", pady=5)

    entry_observacion = tk.Entry(frame_observaciones, font=("Arial", 11), width=40)
    entry_observacion.pack(side="left", padx=10, pady=10)
    btn_agregar_obs = tk.Button(frame_observaciones, text="Agregar", bg="#4CAF50", fg="white", font=("Arial", 11), width=12)
    btn_agregar_obs.pack(side="left", padx=10, pady=10)

    frame_botones = tk.Frame(panel_derecho)
    frame_botones.pack(fill="x", pady=5)

    btn_actualizar_estado = tk.Button(frame_botones, text="Actualizar Estado", bg="#2196F3", fg="white", font=("Arial", 11), width=18)
    btn_actualizar_estado.pack(side="left", padx=10, pady=10)

    btn_cerrar = tk.Button(frame_botones, text="Cerrar", command=ventana.destroy, bg="#f44336", fg="white", width=15)
    btn_cerrar.pack(side="right", padx=10, pady=10)

    def cargar_chequeos(busqueda=""):
        for item in tree_chequeos.get_children():
            tree_chequeos.delete(item)
        if busqueda.isdigit():
            query = """
                SELECT ch.id_chequeo, c.nombre, c.apellido, s.tipo, ch.observaciones, ch.estado
                FROM chequeo ch
                JOIN cliente_servico cs ON ch.id_cliente_servicio = cs.id_cliente_servicio
                JOIN cliente c ON cs.id_cliente = c.id_cliente
                JOIN servicio s ON cs.servicio_id = s.id_servicio
                WHERE ch.id_chequeo = %s
            """
            params = (int(busqueda),)
            registros = ejecutar_query(query, params, fetch_all=True)
        elif busqueda:
            query = """
                SELECT ch.id_chequeo, c.nombre, c.apellido, s.tipo, ch.observaciones, ch.estado
                FROM chequeo ch
                JOIN cliente_servico cs ON ch.id_cliente_servicio = cs.id_cliente_servicio
                JOIN cliente c ON cs.id_cliente = c.id_cliente
                JOIN servicio s ON cs.servicio_id = s.id_servicio
                WHERE c.nombre LIKE %s OR c.apellido LIKE %s
            """
            params = (f"%{busqueda}%", f"%{busqueda}%")
            registros = ejecutar_query(query, params, fetch_all=True)
        else:
            query = """
                SELECT ch.id_chequeo, c.nombre, c.apellido, s.tipo, ch.observaciones, ch.estado
                FROM chequeo ch
                JOIN cliente_servico cs ON ch.id_cliente_servicio = cs.id_cliente_servicio
                JOIN cliente c ON cs.id_cliente = c.id_cliente
                JOIN servicio s ON cs.servicio_id = s.id_servicio
                ORDER BY ch.id_chequeo DESC
            """
            registros = ejecutar_query(query, fetch_all=True)
        if registros:
            for reg in registros:
                tree_chequeos.insert("", "end", values=(reg[0], f"{reg[1]} {reg[2]}", reg[3], reg[4] or "", reg[5] or "PENDIENTE"))
        else:
            tree_chequeos.insert("", "end", values=("No hay datos", "", "", "", ""))

    def mostrar_detalle(event):
        seleccion = tree_chequeos.selection()
        if seleccion:
            valores = tree_chequeos.item(seleccion[0])["values"]
            if valores[0] != "No hay datos":
                id_chequeo = valores[0]
                chequeo_seleccionado_id.set(id_chequeo)
                query = """
                    SELECT ch.id_chequeo, c.nombre, c.apellido, c.dpi,
                           c.barrio, c.zona, c.calle, c.num_casa,
                           s.tipo, s.precio, ch.observaciones, ch.estado
                    FROM chequeo ch
                    JOIN cliente_servico cs ON ch.id_cliente_servicio = cs.id_cliente_servicio
                    JOIN cliente c ON cs.id_cliente = c.id_cliente
                    JOIN servicio s ON cs.servicio_id = s.id_servicio
                    WHERE ch.id_chequeo = %s
                """
                datos = ejecutar_query(query, (id_chequeo,), fetch_one=True)
                if datos:
                    detalle = f"""
=== CHEQUEO #{datos[0]} ===

DATOS DEL CLIENTE:
Nombre: {datos[1]} {datos[2]}
DPI: {datos[3]}
Dirección: {datos[4]}, Zona {datos[5]}, {datos[6]} {datos[7]}

SERVICIO:
Tipo: {datos[8]}
Precio: Q{datos[9]:.2f}

OBSERVACIONES ACTUALES:
{datos[10] or 'Ninguna'}

ESTADO ACTUAL: {datos[11] or 'PENDIENTE'}
                    """
                    texto_detalle.delete(1.0, tk.END)
                    texto_detalle.insert(1.0, detalle)
                    combo_estado.set(datos[11] or "PENDIENTE")
                else:
                    texto_detalle.delete(1.0, tk.END)
                    texto_detalle.insert(1.0, "No se pudo cargar el detalle")
        else:
            chequeo_seleccionado_id.set(0)
            texto_detalle.delete(1.0, tk.END)
            combo_estado.set("PENDIENTE")
            entry_observacion.delete(0, tk.END)

    def actualizar_estado():
        id_chequeo = chequeo_seleccionado_id.get()
        if not id_chequeo:
            messagebox.showwarning("Sin selección", "Seleccione un chequeo de la lista")
            return
        nuevo_estado = combo_estado.get()
        query = "UPDATE chequeo SET estado = %s WHERE id_chequeo = %s"
        resultado = ejecutar_query(query, (nuevo_estado, id_chequeo), commit=True)
        if resultado is not None:
            messagebox.showinfo("Éxito", f"Estado del chequeo #{id_chequeo} actualizado a '{nuevo_estado}'")
            cargar_chequeos()
            mostrar_detalle(None)
        else:
            messagebox.showerror("Error", "No se pudo actualizar el estado")

    def agregar_observacion():
        id_chequeo = chequeo_seleccionado_id.get()
        if not id_chequeo:
            messagebox.showwarning("Sin selección", "Seleccione un chequeo de la lista")
            return
        nueva_obs = entry_observacion.get().strip()
        if not nueva_obs:
            messagebox.showwarning("Datos incompletos", "Ingrese una observación")
            entry_observacion.focus()
            return
        query = "SELECT observaciones FROM chequeo WHERE id_chequeo = %s"
        obs_actual = ejecutar_query(query, (id_chequeo,), fetch_one=True)
        if obs_actual and obs_actual[0]:
            obs_nueva = f"{obs_actual[0]} | {nueva_obs}"
        else:
            obs_nueva = nueva_obs
        query = "UPDATE chequeo SET observaciones = %s WHERE id_chequeo = %s"
        resultado = ejecutar_query(query, (obs_nueva, id_chequeo), commit=True)
        if resultado is not None:
            messagebox.showinfo("Éxito", "Observación agregada correctamente")
            entry_observacion.delete(0, tk.END)
            cargar_chequeos()
            mostrar_detalle(None)
        else:
            messagebox.showerror("Error", "No se pudo agregar la observación")

    def buscar_chequeos():
        texto = entry_buscar.get().strip()
        cargar_chequeos(texto)

    def limpiar_busqueda():
        entry_buscar.delete(0, tk.END)
        cargar_chequeos()

    btn_buscar = tk.Button(frame_buscar, text="Buscar", command=buscar_chequeos, bg="#2196F3", fg="white")
    btn_buscar.pack(side="left", padx=5)
    btn_refrescar = tk.Button(frame_buscar, text="Refrescar", command=limpiar_busqueda, bg="#9E9E9E", fg="white")
    btn_refrescar.pack(side="left", padx=5)

    tree_chequeos.bind("<<TreeviewSelect>>", mostrar_detalle)
    entry_buscar.bind("<Return>", lambda e: buscar_chequeos())
    btn_actualizar_estado.config(command=actualizar_estado)
    btn_agregar_obs.config(command=agregar_observacion)

    cargar_chequeos()

def ventana_facturar_tecnico():
    ventana = tk.Toplevel()
    ventana.title("Facturar Instalación o Chequeo - Cable Internet")
    ventana.attributes('-fullscreen', True)
    ventana.transient()
    ventana.grab_set()
    ventana.bind("<Escape>", lambda e: ventana.destroy())

    tk.Label(ventana, text="Facturar Instalación/Chequeo", font=("Arial", 20, "bold")).pack(pady=20)

    notebook = ttk.Notebook(ventana)
    notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    frame_instalaciones = tk.Frame(notebook)
    notebook.add(frame_instalaciones, text="Instalaciones Completadas")

    frame_chequeos = tk.Frame(notebook)
    notebook.add(frame_chequeos, text="Chequeos Completados")

    frame_buscar_inst = tk.Frame(frame_instalaciones)
    frame_buscar_inst.pack(fill="x", padx=10, pady=10)
    tk.Label(frame_buscar_inst, text="Buscar:", font=("Arial", 12)).pack(side="left")
    entry_buscar_inst = tk.Entry(frame_buscar_inst, font=("Arial", 12), width=30)
    entry_buscar_inst.pack(side="left", padx=10)
    btn_buscar_inst = tk.Button(frame_buscar_inst, text="Buscar", bg="#2196F3", fg="white", font=("Arial", 12))
    btn_buscar_inst.pack(side="left")

    columnas_inst = ("ID", "Cliente", "Dirección", "Fecha", "Precio")
    tree_inst = ttk.Treeview(frame_instalaciones, columns=columnas_inst, show="headings", height=15)
    anchos = {"ID": 50, "Cliente": 200, "Dirección": 300, "Fecha": 100, "Precio": 100}
    for col in columnas_inst:
        tree_inst.heading(col, text=col)
        tree_inst.column(col, width=anchos.get(col, 100))
    tree_inst.pack(fill="both", expand=True, padx=10, pady=10)

    scroll_inst = ttk.Scrollbar(frame_instalaciones, orient="vertical", command=tree_inst.yview)
    tree_inst.configure(yscrollcommand=scroll_inst.set)
    scroll_inst.pack(side="right", fill="y")

    frame_buscar_cheq = tk.Frame(frame_chequeos)
    frame_buscar_cheq.pack(fill="x", padx=10, pady=10)
    tk.Label(frame_buscar_cheq, text="Buscar:", font=("Arial", 12)).pack(side="left")
    entry_buscar_cheq = tk.Entry(frame_buscar_cheq, font=("Arial", 12), width=30)
    entry_buscar_cheq.pack(side="left", padx=10)
    btn_buscar_cheq = tk.Button(frame_buscar_cheq, text="Buscar", bg="#2196F3", fg="white", font=("Arial", 12))
    btn_buscar_cheq.pack(side="left")

    columnas_cheq = ("ID", "Cliente", "Servicio", "Observaciones", "Precio")
    tree_cheq = ttk.Treeview(frame_chequeos, columns=columnas_cheq, show="headings", height=15)
    anchos_cheq = {"ID": 50, "Cliente": 200, "Servicio": 200, "Observaciones": 200, "Precio": 100}
    for col in columnas_cheq:
        tree_cheq.heading(col, text=col)
        tree_cheq.column(col, width=anchos_cheq.get(col, 100))
    tree_cheq.pack(fill="both", expand=True, padx=10, pady=10)

    scroll_cheq = ttk.Scrollbar(frame_chequeos, orient="vertical", command=tree_cheq.yview)
    tree_cheq.configure(yscrollcommand=scroll_cheq.set)
    scroll_cheq.pack(side="right", fill="y")

    frame_botones = tk.Frame(ventana)
    frame_botones.pack(pady=20)

    btn_facturar = tk.Button(frame_botones, text="Generar Factura", bg="#4CAF50", fg="white", font=("Arial", 14), width=25)
    btn_facturar.pack(side="left", padx=10)

    btn_cerrar = tk.Button(frame_botones, text="Cerrar", command=ventana.destroy, bg="#f44336", fg="white", font=("Arial", 14), width=15)
    btn_cerrar.pack(side="left", padx=10)

    instalacion_seleccionada_id = tk.IntVar()
    chequeo_seleccionado_id = tk.IntVar()

    def cargar_instalaciones_completadas(busqueda=""):
        for item in tree_inst.get_children():
            tree_inst.delete(item)
        if busqueda.isdigit():
            query = """
                SELECT i.id_instalacion, c.nombre, c.apellido,
                       CONCAT(c.barrio, ', Zona ', c.zona, ', ', c.calle, ' ', c.num_casa) as direccion,
                       i.fecha, s.precio
                FROM instalacion i
                JOIN orden_instalacion o ON i.id_orden_instalacion = o.id_orden
                JOIN cliente c ON o.id_cliente = c.id_cliente
                JOIN cliente_servico cs ON o.id_cliente = cs.id_cliente
                JOIN servicio s ON cs.servicio_id = s.id_servicio
                WHERE i.estado = 'COMPLETADA' AND i.id_instalacion = %s
            """
            params = (int(busqueda),)
            registros = ejecutar_query(query, params, fetch_all=True)
        elif busqueda:
            query = """
                SELECT i.id_instalacion, c.nombre, c.apellido,
                       CONCAT(c.barrio, ', Zona ', c.zona, ', ', c.calle, ' ', c.num_casa) as direccion,
                       i.fecha, s.precio
                FROM instalacion i
                JOIN orden_instalacion o ON i.id_orden_instalacion = o.id_orden
                JOIN cliente c ON o.id_cliente = c.id_cliente
                JOIN cliente_servico cs ON o.id_cliente = cs.id_cliente
                JOIN servicio s ON cs.servicio_id = s.id_servicio
                WHERE i.estado = 'COMPLETADA' AND (c.nombre LIKE %s OR c.apellido LIKE %s)
            """
            params = (f"%{busqueda}%", f"%{busqueda}%")
            registros = ejecutar_query(query, params, fetch_all=True)
        else:
            query = """
                SELECT i.id_instalacion, c.nombre, c.apellido,
                       CONCAT(c.barrio, ', Zona ', c.zona, ', ', c.calle, ' ', c.num_casa) as direccion,
                       i.fecha, s.precio
                FROM instalacion i
                JOIN orden_instalacion o ON i.id_orden_instalacion = o.id_orden
                JOIN cliente c ON o.id_cliente = c.id_cliente
                JOIN cliente_servico cs ON o.id_cliente = cs.id_cliente
                JOIN servicio s ON cs.servicio_id = s.id_servicio
                WHERE i.estado = 'COMPLETADA'
                ORDER BY i.fecha DESC
            """
            registros = ejecutar_query(query, fetch_all=True)
        if registros:
            for reg in registros:
                tree_inst.insert("", "end", values=(reg[0], f"{reg[1]} {reg[2]}", reg[3], reg[4], f"Q{reg[5]:.2f}"))
        else:
            tree_inst.insert("", "end", values=("No hay datos", "", "", "", ""))

    def cargar_chequeos_completados(busqueda=""):
        for item in tree_cheq.get_children():
            tree_cheq.delete(item)
        if busqueda.isdigit():
            query = """
                SELECT ch.id_chequeo, c.nombre, c.apellido, s.tipo, ch.observaciones, s.precio
                FROM chequeo ch
                JOIN cliente_servico cs ON ch.id_cliente_servicio = cs.id_cliente_servicio
                JOIN cliente c ON cs.id_cliente = c.id_cliente
                JOIN servicio s ON cs.servicio_id = s.id_servicio
                WHERE ch.estado = 'COMPLETADO' AND ch.id_chequeo = %s
            """
            params = (int(busqueda),)
            registros = ejecutar_query(query, params, fetch_all=True)
        elif busqueda:
            query = """
                SELECT ch.id_chequeo, c.nombre, c.apellido, s.tipo, ch.observaciones, s.precio
                FROM chequeo ch
                JOIN cliente_servico cs ON ch.id_cliente_servicio = cs.id_cliente_servicio
                JOIN cliente c ON cs.id_cliente = c.id_cliente
                JOIN servicio s ON cs.servicio_id = s.id_servicio
                WHERE ch.estado = 'COMPLETADO' AND (c.nombre LIKE %s OR c.apellido LIKE %s)
            """
            params = (f"%{busqueda}%", f"%{busqueda}%")
            registros = ejecutar_query(query, params, fetch_all=True)
        else:
            query = """
                SELECT ch.id_chequeo, c.nombre, c.apellido, s.tipo, ch.observaciones, s.precio
                FROM chequeo ch
                JOIN cliente_servico cs ON ch.id_cliente_servicio = cs.id_cliente_servicio
                JOIN cliente c ON cs.id_cliente = c.id_cliente
                JOIN servicio s ON cs.servicio_id = s.id_servicio
                WHERE ch.estado = 'COMPLETADO'
                ORDER BY ch.id_chequeo DESC
            """
            registros = ejecutar_query(query, fetch_all=True)
        if registros:
            for reg in registros:
                tree_cheq.insert("", "end", values=(reg[0], f"{reg[1]} {reg[2]}", reg[3], reg[4] or "", f"Q{reg[5]:.2f}"))
        else:
            tree_cheq.insert("", "end", values=("No hay datos", "", "", "", ""))

    def on_instalacion_seleccionada(event):
        seleccion = tree_inst.selection()
        if seleccion:
            valores = tree_inst.item(seleccion[0])["values"]
            if valores[0] != "No hay datos":
                instalacion_seleccionada_id.set(valores[0])

    def on_chequeo_seleccionado(event):
        seleccion = tree_cheq.selection()
        if seleccion:
            valores = tree_cheq.item(seleccion[0])["values"]
            if valores[0] != "No hay datos":
                chequeo_seleccionado_id.set(valores[0])

    def generar_factura():
        pestaña_actual = notebook.index(notebook.select())
        from datetime import datetime
        fecha = datetime.now().strftime("%Y-%m-%d")

        if pestaña_actual == 0:
            id_instalacion = instalacion_seleccionada_id.get()
            if not id_instalacion:
                messagebox.showwarning("Sin selección", "Seleccione una instalación de la lista")
                return
            query = """
                SELECT s.id_servicio, s.precio
                FROM instalacion i
                JOIN orden_instalacion o ON i.id_orden_instalacion = o.id_orden
                JOIN cliente_servico cs ON o.id_cliente = cs.id_cliente
                JOIN servicio s ON cs.servicio_id = s.id_servicio
                WHERE i.id_instalacion = %s
            """
            datos = ejecutar_query(query, (id_instalacion,), fetch_one=True)
            if datos:
                id_servicio, precio = datos
                query_insert = "INSERT INTO factura (fecha_emicion, total, id_cliente_servicio, tipo_factura) VALUES (%s, %s, %s, %s)"
                resultado = ejecutar_query(query_insert, (fecha, precio, id_servicio, "INSTALACION"), commit=True)
                if resultado:
                    messagebox.showinfo("Éxito", f"Factura generada para instalación #{id_instalacion}\nTotal: Q{precio:.2f}")
                    cargar_instalaciones_completadas()
                    instalacion_seleccionada_id.set(0)
                else:
                    messagebox.showerror("Error", "No se pudo generar la factura")
        else:
            id_chequeo = chequeo_seleccionado_id.get()
            if not id_chequeo:
                messagebox.showwarning("Sin selección", "Seleccione un chequeo de la lista")
                return
            query = """
                SELECT s.id_servicio, s.precio
                FROM chequeo ch
                JOIN cliente_servico cs ON ch.id_cliente_servicio = cs.id_cliente_servicio
                JOIN servicio s ON cs.servicio_id = s.id_servicio
                WHERE ch.id_chequeo = %s
            """
            datos = ejecutar_query(query, (id_chequeo,), fetch_one=True)
            if datos:
                id_servicio, precio = datos
                query_insert = "INSERT INTO factura (fecha_emicion, total, id_cliente_servicio, tipo_factura) VALUES (%s, %s, %s, %s)"
                resultado = ejecutar_query(query_insert, (fecha, precio, id_servicio, "CHEQUEO"), commit=True)
                if resultado:
                    messagebox.showinfo("Éxito", f"Factura generada para chequeo #{id_chequeo}\nTotal: Q{precio:.2f}")
                    cargar_chequeos_completados()
                    chequeo_seleccionado_id.set(0)
                else:
                    messagebox.showerror("Error", "No se pudo generar la factura")

    def buscar_instalaciones():
        texto = entry_buscar_inst.get().strip()
        cargar_instalaciones_completadas(texto)

    def buscar_chequeos():
        texto = entry_buscar_cheq.get().strip()
        cargar_chequeos_completados(texto)

    def limpiar_busqueda_inst():
        entry_buscar_inst.delete(0, tk.END)
        cargar_instalaciones_completadas()

    def limpiar_busqueda_cheq():
        entry_buscar_cheq.delete(0, tk.END)
        cargar_chequeos_completados()

    btn_buscar_inst.config(command=buscar_instalaciones)
    btn_buscar_cheq.config(command=buscar_chequeos)

    btn_refrescar_inst = tk.Button(frame_buscar_inst, text="Refrescar", command=limpiar_busqueda_inst, bg="#9E9E9E", fg="white")
    btn_refrescar_inst.pack(side="left", padx=5)
    btn_refrescar_cheq = tk.Button(frame_buscar_cheq, text="Refrescar", command=limpiar_busqueda_cheq, bg="#9E9E9E", fg="white")
    btn_refrescar_cheq.pack(side="left", padx=5)

    tree_inst.bind("<<TreeviewSelect>>", on_instalacion_seleccionada)
    tree_cheq.bind("<<TreeviewSelect>>", on_chequeo_seleccionado)
    entry_buscar_inst.bind("<Return>", lambda e: buscar_instalaciones())
    entry_buscar_cheq.bind("<Return>", lambda e: buscar_chequeos())
    btn_facturar.config(command=generar_factura)

    cargar_instalaciones_completadas()
    cargar_chequeos_completados()

def ventana_asignar_cliente_servicio_cobrador():
    ventana = tk.Toplevel()
    ventana.title("Asignar Cliente con Servicio a Cobrador")
    ventana.attributes('-fullscreen', True)
    ventana.transient()
    ventana.grab_set()
    ventana.bind("<Escape>", lambda e: ventana.destroy())

    tk.Label(ventana, text="Asignar Cliente con Servicio a Cobrador", font=("Arial", 20, "bold")).pack(pady=20)

    panel_principal = tk.PanedWindow(ventana, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, sashwidth=5)
    panel_principal.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    frame_clientes = tk.LabelFrame(panel_principal, text="Clientes con Servicios Contratados", font=("Arial", 12, "bold"))
    panel_principal.add(frame_clientes, width=700)

    frame_buscar = tk.Frame(frame_clientes)
    frame_buscar.pack(fill="x", padx=10, pady=10)
    tk.Label(frame_buscar, text="Buscar:", font=("Arial", 12)).pack(side="left")
    entry_buscar = tk.Entry(frame_buscar, font=("Arial", 12), width=30)
    entry_buscar.pack(side="left", padx=10)
    btn_buscar = tk.Button(frame_buscar, text="Buscar", bg="#2196F3", fg="white", font=("Arial", 12))
    btn_buscar.pack(side="left")
    btn_refrescar = tk.Button(frame_buscar, text="Refrescar", bg="#9E9E9E", fg="white", font=("Arial", 12))
    btn_refrescar.pack(side="left", padx=5)

    columnas_clientes = ("ID", "Cliente", "Teléfono", "Dirección", "Servicio", "Precio")
    tree_clientes = ttk.Treeview(frame_clientes, columns=columnas_clientes, show="headings", height=15)
    anchos = {"ID": 50, "Cliente": 200, "Teléfono": 100, "Dirección": 200, "Servicio": 180, "Precio": 80}
    for col in columnas_clientes:
        tree_clientes.heading(col, text=col)
        tree_clientes.column(col, width=anchos.get(col, 100))
    tree_clientes.pack(fill="both", expand=True, padx=10, pady=10)

    scroll_clientes = ttk.Scrollbar(frame_clientes, orient="vertical", command=tree_clientes.yview)
    tree_clientes.configure(yscrollcommand=scroll_clientes.set)
    scroll_clientes.pack(side="right", fill="y")

    frame_cobradores = tk.LabelFrame(panel_principal, text="Cobradores", font=("Arial", 12, "bold"))
    panel_principal.add(frame_cobradores, width=350)

    tk.Label(frame_cobradores, text="Seleccione un Cobrador:", font=("Arial", 12)).pack(pady=10)
    combo_cobradores = ttk.Combobox(frame_cobradores, font=("Arial", 12), width=30)
    combo_cobradores.pack(pady=5)

    tk.Label(frame_cobradores, text="Asignaciones actuales de este Cobrador:", font=("Arial", 12, "bold")).pack(pady=10)
    tree_asignaciones = ttk.Treeview(frame_cobradores, columns=("Cliente", "Servicio"), show="headings", height=12)
    tree_asignaciones.heading("Cliente", text="Cliente")
    tree_asignaciones.heading("Servicio", text="Servicio")
    tree_asignaciones.column("Cliente", width=150)
    tree_asignaciones.column("Servicio", width=150)
    tree_asignaciones.pack(fill="both", expand=True, padx=10, pady=10)

    scroll_asignaciones = ttk.Scrollbar(frame_cobradores, orient="vertical", command=tree_asignaciones.yview)
    tree_asignaciones.configure(yscrollcommand=scroll_asignaciones.set)
    scroll_asignaciones.pack(side="right", fill="y")

    frame_botones = tk.Frame(frame_cobradores)
    frame_botones.pack(pady=10)

    btn_asignar = tk.Button(frame_botones, text="Asignar Seleccionado →", bg="#4CAF50", fg="white", font=("Arial", 12), width=22)
    btn_asignar.pack(side="left", padx=5)

    btn_quitar = tk.Button(frame_botones, text="← Quitar Seleccionado", bg="#f44336", fg="white", font=("Arial", 12), width=22)
    btn_quitar.pack(side="left", padx=5)

    btn_cerrar = tk.Button(frame_cobradores, text="Cerrar", command=ventana.destroy, bg="#f44336", fg="white", font=("Arial", 12), width=15)
    btn_cerrar.pack(pady=10)

    cliente_servicio_seleccionado_id = tk.IntVar()
    cliente_servicio_seleccionado_texto = tk.StringVar()
    cobradores_data = []

    def cargar_clientes_con_servicios(busqueda=""):
        for item in tree_clientes.get_children():
            tree_clientes.delete(item)
        if busqueda.isdigit():
            query = """
                SELECT cs.id_cliente_servicio, c.nombre, c.apellido,
                       (SELECT num_telefono FROM telefono WHERE id_cliente = c.id_cliente LIMIT 1) as telefono,
                       CONCAT(c.barrio, ', Zona ', c.zona, ', ', c.calle, ' ', c.num_casa) as direccion,
                       s.tipo, s.precio
                FROM cliente_servicio cs
                JOIN cliente c ON cs.id_cliente = c.id_cliente
                JOIN servicio s ON cs.servicio_id = s.id_servicio
                WHERE cs.id_cliente_servicio = %s
                ORDER BY c.nombre
            """
            params = (int(busqueda),)
            registros = ejecutar_query(query, params, fetch_all=True)
        elif busqueda:
            query = """
                SELECT cs.id_cliente_servicio, c.nombre, c.apellido,
                       (SELECT num_telefono FROM telefono WHERE id_cliente = c.id_cliente LIMIT 1) as telefono,
                       CONCAT(c.barrio, ', Zona ', c.zona, ', ', c.calle, ' ', c.num_casa) as direccion,
                       s.tipo, s.precio
                FROM cliente_servicio cs
                JOIN cliente c ON cs.id_cliente = c.id_cliente
                JOIN servicio s ON cs.servicio_id = s.id_servicio
                WHERE c.nombre LIKE %s OR c.apellido LIKE %s OR s.tipo LIKE %s
                ORDER BY c.nombre
            """
            params = (f"%{busqueda}%", f"%{busqueda}%", f"%{busqueda}%")
            registros = ejecutar_query(query, params, fetch_all=True)
        else:
            query = """
                SELECT cs.id_cliente_servicio, c.nombre, c.apellido,
                       (SELECT num_telefono FROM telefono WHERE id_cliente = c.id_cliente LIMIT 1) as telefono,
                       CONCAT(c.barrio, ', Zona ', c.zona, ', ', c.calle, ' ', c.num_casa) as direccion,
                       s.tipo, s.precio
                FROM cliente_servicio cs
                JOIN cliente c ON cs.id_cliente = c.id_cliente
                JOIN servicio s ON cs.servicio_id = s.id_servicio
                ORDER BY c.nombre
            """
            registros = ejecutar_query(query, fetch_all=True)
        if registros:
            for reg in registros:
                tree_clientes.insert("", "end", values=(reg[0], f"{reg[1]} {reg[2]}", reg[3] or "", reg[4] or "", reg[5], f"Q{reg[6]:.2f}"))
        else:
            tree_clientes.insert("", "end", values=("No hay datos", "", "", "", "", ""))

    def cargar_cobradores():
        nonlocal cobradores_data
        query = "SELECT id_cobrador, nombre, apellido FROM cobrador ORDER BY nombre"
        cobradores_data = ejecutar_query(query, fetch_all=True) or []
        combo_cobradores['values'] = [f"{c[0]} - {c[1]} {c[2]}" for c in cobradores_data]
        if cobradores_data:
            combo_cobradores.current(0)
            cargar_asignaciones()

    def cargar_asignaciones():
        for item in tree_asignaciones.get_children():
            tree_asignaciones.delete(item)
        seleccion = combo_cobradores.current()
        if seleccion >= 0 and cobradores_data:
            id_cobrador = cobradores_data[seleccion][0]
            query = """
                SELECT c.nombre, c.apellido, s.tipo
                FROM asignacion_cobrador ac
                JOIN cliente_servicio cs ON ac.id_cliente_servicio = cs.id_cliente_servicio
                JOIN cliente c ON cs.id_cliente = c.id_cliente
                JOIN servicio s ON cs.servicio_id = s.id_servicio
                WHERE ac.id_cobrador = %s
            """
            asignaciones = ejecutar_query(query, (id_cobrador,), fetch_all=True) or []
            for a in asignaciones:
                tree_asignaciones.insert("", "end", values=(f"{a[0]} {a[1]}", a[2]))

    def on_cliente_seleccionado(event):
        seleccion = tree_clientes.selection()
        if seleccion:
            valores = tree_clientes.item(seleccion[0])["values"]
            if valores[0] != "No hay datos":
                cliente_servicio_seleccionado_id.set(valores[0])
                cliente_servicio_seleccionado_texto.set(f"{valores[1]} - {valores[4]}")
        else:
            cliente_servicio_seleccionado_id.set(0)

    def asignar():
        id_cliente_servicio = cliente_servicio_seleccionado_id.get()
        if not id_cliente_servicio:
            messagebox.showwarning("Sin selección", "Seleccione un cliente con servicio de la lista")
            return

        seleccion_cobrador = combo_cobradores.current()
        if seleccion_cobrador < 0 or not cobradores_data:
            messagebox.showwarning("Sin selección", "Seleccione un cobrador")
            return
        id_cobrador = cobradores_data[seleccion_cobrador][0]

        query_check = "SELECT COUNT(*) FROM asignacion_cobrador WHERE id_cliente_servicio = %s AND id_cobrador = %s"
        existe = ejecutar_query(query_check, (id_cliente_servicio, id_cobrador), fetch_one=True)
        if existe and existe[0] > 0:
            messagebox.showwarning("Ya asignado", "Este cliente-servicio ya está asignado a este cobrador")
            return

        query = "INSERT INTO asignacion_cobrador (id_cliente_servicio, id_cobrador) VALUES (%s, %s)"
        resultado = ejecutar_query(query, (id_cliente_servicio, id_cobrador), commit=True)
        if resultado:
            messagebox.showinfo("Éxito", f"Asignado correctamente")
            cargar_asignaciones()
        else:
            messagebox.showerror("Error", "No se pudo asignar")

    def quitar():
        seleccion = tree_asignaciones.selection()
        if not seleccion:
            messagebox.showwarning("Sin selección", "Seleccione una asignación para quitar")
            return
        valores = tree_asignaciones.item(seleccion[0])["values"]
        cliente_nombre = valores[0]
        servicio_nombre = valores[1]

        seleccion_cobrador = combo_cobradores.current()
        if seleccion_cobrador < 0 or not cobradores_data:
            return
        id_cobrador = cobradores_data[seleccion_cobrador][0]

        query_buscar = """
            SELECT cs.id_cliente_servicio
            FROM cliente_servicio cs
            JOIN cliente c ON cs.id_cliente = c.id_cliente
            JOIN servicio s ON cs.servicio_id = s.id_servicio
            WHERE CONCAT(c.nombre, ' ', c.apellido) = %s AND s.tipo = %s
        """
        resultado = ejecutar_query(query_buscar, (cliente_nombre, servicio_nombre), fetch_one=True)
        if resultado:
            id_cliente_servicio = resultado[0]
            confirmar = messagebox.askyesno("Confirmar", f"¿Quitar la asignación de '{cliente_nombre}' - '{servicio_nombre}'?")
            if confirmar:
                query = "DELETE FROM asignacion_cobrador WHERE id_cliente_servicio = %s AND id_cobrador = %s"
                ejecutar_query(query, (id_cliente_servicio, id_cobrador), commit=True)
                cargar_asignaciones()

    def buscar_clientes():
        texto = entry_buscar.get().strip()
        cargar_clientes_con_servicios(texto)

    def limpiar_busqueda():
        entry_buscar.delete(0, tk.END)
        cargar_clientes_con_servicios()

    tree_clientes.bind("<<TreeviewSelect>>", on_cliente_seleccionado)
    combo_cobradores.bind("<<ComboboxSelected>>", lambda e: cargar_asignaciones())
    btn_buscar.config(command=buscar_clientes)
    btn_refrescar.config(command=limpiar_busqueda)
    btn_asignar.config(command=asignar)
    btn_quitar.config(command=quitar)

    cargar_clientes_con_servicios()
    cargar_cobradores()

def ventana_control_cobros():
    ventana = tk.Toplevel()
    ventana.title("Control de Cobros - Cable Internet")
    ventana.attributes('-fullscreen', True)
    ventana.transient()
    ventana.grab_set()
    ventana.bind("<Escape>", lambda e: ventana.destroy())

    notebook = ttk.Notebook(ventana)
    notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    frame_resumen = tk.Frame(notebook)
    notebook.add(frame_resumen, text="Resumen por Cobrador")

    frame_detalle = tk.Frame(notebook)
    notebook.add(frame_detalle, text="Cobros por Fecha")

    columnas_resumen = ("ID", "Cobrador", "Total Cobrado Hoy", "Total Semana", "Total Mes")
    tree_resumen = ttk.Treeview(frame_resumen, columns=columnas_resumen, show="headings", height=20)
    anchos = {"ID": 50, "Cobrador": 200, "Total Cobrado Hoy": 150, "Total Semana": 150, "Total Mes": 150}
    for col in columnas_resumen:
        tree_resumen.heading(col, text=col)
        tree_resumen.column(col, width=anchos.get(col, 100))
    tree_resumen.pack(side="left", fill="both", expand=True, padx=5, pady=5)

    scroll_resumen = ttk.Scrollbar(frame_resumen, orient="vertical", command=tree_resumen.yview)
    tree_resumen.configure(yscrollcommand=scroll_resumen.set)
    scroll_resumen.pack(side="right", fill="y")

    tk.Label(frame_detalle, text="Seleccione una fecha:", font=("Arial", 12)).pack(pady=10)
    from datetime import datetime
    fecha_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
    entry_fecha = tk.Entry(frame_detalle, textvariable=fecha_var, font=("Arial", 12), width=15)
    entry_fecha.pack()

    columnas_detalle = ("Cobrador", "Cliente", "Monto", "Método de Pago", "Fecha")
    tree_detalle = ttk.Treeview(frame_detalle, columns=columnas_detalle, show="headings", height=15)
    for col in columnas_detalle:
        tree_detalle.heading(col, text=col)
        tree_detalle.column(col, width=150)
    tree_detalle.pack(fill="both", expand=True, padx=5, pady=5)

    scroll_detalle = ttk.Scrollbar(frame_detalle, orient="vertical", command=tree_detalle.yview)
    tree_detalle.configure(yscrollcommand=scroll_detalle.set)
    scroll_detalle.pack(side="right", fill="y")

    def cargar_resumen():
        for item in tree_resumen.get_children():
            tree_resumen.delete(item)
        hoy = datetime.now().strftime("%Y-%m-%d")
        query = """
            SELECT c.id_cobrador, c.nombre, c.apellido,
                   COALESCE(SUM(CASE WHEN DATE(p.fecha) = %s THEN p.monto ELSE 0 END), 0) as total_hoy,
                   COALESCE(SUM(CASE WHEN YEARWEEK(p.fecha) = YEARWEEK(CURDATE()) THEN p.monto ELSE 0 END), 0) as total_semana,
                   COALESCE(SUM(CASE WHEN MONTH(p.fecha) = MONTH(CURDATE()) THEN p.monto ELSE 0 END), 0) as total_mes
            FROM cobrador c
            LEFT JOIN pago p ON c.id_cobrador = p.id_cobrador
            GROUP BY c.id_cobrador
            ORDER BY total_hoy DESC
        """
        registros = ejecutar_query(query, (hoy,), fetch_all=True)
        if registros:
            for reg in registros:
                tree_resumen.insert("", "end", values=(reg[0], f"{reg[1]} {reg[2]}", f"Q{reg[3]:.2f}", f"Q{reg[4]:.2f}", f"Q{reg[5]:.2f}"))
        else:
            tree_resumen.insert("", "end", values=("No hay datos", "", "", "", ""))

    def cargar_detalle():
        for item in tree_detalle.get_children():
            tree_detalle.delete(item)
        fecha = fecha_var.get()
        query = """
            SELECT c.nombre, c.apellido, cl.nombre, p.monto, mp.nombre, p.fecha
            FROM pago p
            JOIN cobrador c ON p.id_cobrador = c.id_cobrador
            JOIN factura f ON p.factura_id_factura = f.id_factura
            JOIN cliente_servico cs ON f.id_cliente_servicio = cs.id_cliente_servicio
            JOIN cliente cl ON cs.id_cliente = cl.id_cliente
            JOIN metodo_pago mp ON p.id_metodo_pago = mp.id_metodo_pago
            WHERE DATE(p.fecha) = %s
            ORDER BY p.fecha DESC
        """
        registros = ejecutar_query(query, (fecha,), fetch_all=True)
        if registros:
            total = 0
            for reg in registros:
                tree_detalle.insert("", "end", values=(f"{reg[0]} {reg[1]}", reg[2], f"Q{reg[3]:.2f}", reg[4], reg[5]))
                total += reg[3]
            tree_detalle.insert("", "end", values=("", "", f"TOTAL: Q{total:.2f}", "", ""))
        else:
            tree_detalle.insert("", "end", values=("No hay cobros registrados", "", "", "", ""))

    def actualizar_detalle():
        cargar_detalle()

    btn_actualizar_fecha = tk.Button(frame_detalle, text="Consultar", command=actualizar_detalle, bg="#2196F3", fg="white")
    btn_actualizar_fecha.pack(pady=5)

    btn_cerrar = tk.Button(ventana, text="Cerrar", command=ventana.destroy, bg="#f44336", fg="white", width=15)
    btn_cerrar.pack(pady=10)

    cargar_resumen()
    cargar_detalle()


def ventana_facturar():
    ventana = tk.Toplevel()
    ventana.title("Registrar Pago - Cable Internet")
    ventana.attributes('-fullscreen', True)
    ventana.transient()
    ventana.grab_set()
    ventana.bind("<Escape>", lambda e: ventana.destroy())

    tk.Label(ventana, text="Registrar Pago de Cliente", font=("Arial", 20, "bold")).pack(pady=20)

    panel_principal = tk.PanedWindow(ventana, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, sashwidth=5)
    panel_principal.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    frame_clientes = tk.LabelFrame(panel_principal, text="Clientes", font=("Arial", 12, "bold"))
    panel_principal.add(frame_clientes, width=600)

    frame_buscar = tk.Frame(frame_clientes)
    frame_buscar.pack(fill="x", padx=10, pady=10)
    tk.Label(frame_buscar, text="Buscar:", font=("Arial", 12)).pack(side="left")
    entry_buscar = tk.Entry(frame_buscar, font=("Arial", 12), width=30)
    entry_buscar.pack(side="left", padx=10)
    btn_buscar = tk.Button(frame_buscar, text="Buscar", bg="#2196F3", fg="white", font=("Arial", 12))
    btn_buscar.pack(side="left")
    btn_refrescar = tk.Button(frame_buscar, text="Refrescar", bg="#9E9E9E", fg="white", font=("Arial", 12))
    btn_refrescar.pack(side="left", padx=5)

    columnas_clientes = ("ID", "Nombre", "Apellido", "DPI", "Teléfono", "Dirección")
    tree_clientes = ttk.Treeview(frame_clientes, columns=columnas_clientes, show="headings", height=18)
    anchos = {"ID": 50, "Nombre": 150, "Apellido": 150, "DPI": 120, "Teléfono": 100, "Dirección": 200}
    for col in columnas_clientes:
        tree_clientes.heading(col, text=col)
        tree_clientes.column(col, width=anchos.get(col, 100))
    tree_clientes.pack(fill="both", expand=True, padx=10, pady=10)

    scroll_clientes = ttk.Scrollbar(frame_clientes, orient="vertical", command=tree_clientes.yview)
    tree_clientes.configure(yscrollcommand=scroll_clientes.set)
    scroll_clientes.pack(side="right", fill="y")

    panel_derecho = tk.Frame(panel_principal)
    panel_principal.add(panel_derecho, width=500)

    frame_detalle = tk.LabelFrame(panel_derecho, text="Detalle del Cliente", font=("Arial", 12, "bold"))
    frame_detalle.pack(fill="both", expand=True, pady=5)

    texto_detalle = tk.Text(frame_detalle, font=("Arial", 11), wrap="word", height=10)
    texto_detalle.pack(fill="both", expand=True, padx=10, pady=10)

    frame_pago = tk.LabelFrame(panel_derecho, text="Registrar Pago", font=("Arial", 12, "bold"))
    frame_pago.pack(fill="x", pady=5)

    tk.Label(frame_pago, text="Monto a pagar (Q):", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=10,
                                                                             sticky="e")
    entry_monto = tk.Entry(frame_pago, font=("Arial", 12), width=20)
    entry_monto.grid(row=0, column=1, padx=10, pady=10, sticky="w")

    tk.Label(frame_pago, text="Método de pago:", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=10, sticky="e")
    combo_metodo = ttk.Combobox(frame_pago, font=("Arial", 12), width=18)
    combo_metodo['values'] = ("EFECTIVO", "TARJETA", "TRANSFERENCIA")
    combo_metodo.current(0)
    combo_metodo.grid(row=1, column=1, padx=10, pady=10, sticky="w")

    tk.Label(frame_pago, text="Descripción (opcional):", font=("Arial", 12)).grid(row=2, column=0, padx=10, pady=10,
                                                                                  sticky="e")
    entry_descripcion = tk.Entry(frame_pago, font=("Arial", 12), width=30)
    entry_descripcion.grid(row=2, column=1, padx=10, pady=10, sticky="w")

    frame_botones = tk.Frame(panel_derecho)
    frame_botones.pack(fill="x", pady=10)

    btn_registrar = tk.Button(frame_botones, text="Registrar Pago", bg="#4CAF50", fg="white", font=("Arial", 12),
                              width=20)
    btn_registrar.pack(side="left", padx=10, pady=10)

    btn_cerrar = tk.Button(frame_botones, text="Cerrar", command=ventana.destroy, bg="#f44336", fg="white",
                           font=("Arial", 12), width=15)
    btn_cerrar.pack(side="right", padx=10, pady=10)

    cliente_seleccionado_id = tk.IntVar()
    cliente_seleccionado_nombre = tk.StringVar()
    metodo_pago_data = []

    def cargar_metodos_pago():
        nonlocal metodo_pago_data
        query = "SELECT id_metodo_pago, nombre FROM metodo_pago"
        metodo_pago_data = ejecutar_query(query, fetch_all=True) or []
        combo_metodo['values'] = [m[1] for m in metodo_pago_data]
        if metodo_pago_data:
            combo_metodo.current(0)

    def cargar_clientes(busqueda=""):
        for item in tree_clientes.get_children():
            tree_clientes.delete(item)
        if busqueda.isdigit():
            query = """
                SELECT c.id_cliente, c.nombre, c.apellido, c.dpi, 
                       (SELECT num_telefono FROM telefono WHERE id_cliente = c.id_cliente LIMIT 1) as telefono,
                       CONCAT(c.barrio, ', Zona ', c.zona, ', ', c.calle, ' ', c.num_casa) as direccion
                FROM cliente c
                WHERE c.id_cliente = %s
            """
            params = (int(busqueda),)
            registros = ejecutar_query(query, params, fetch_all=True)
        elif busqueda:
            query = """
                SELECT c.id_cliente, c.nombre, c.apellido, c.dpi, 
                       (SELECT num_telefono FROM telefono WHERE id_cliente = c.id_cliente LIMIT 1) as telefono,
                       CONCAT(c.barrio, ', Zona ', c.zona, ', ', c.calle, ' ', c.num_casa) as direccion
                FROM cliente c
                WHERE c.nombre LIKE %s OR c.apellido LIKE %s OR c.dpi LIKE %s
            """
            params = (f"%{busqueda}%", f"%{busqueda}%", f"%{busqueda}%")
            registros = ejecutar_query(query, params, fetch_all=True)
        else:
            query = """
                SELECT c.id_cliente, c.nombre, c.apellido, c.dpi, 
                       (SELECT num_telefono FROM telefono WHERE id_cliente = c.id_cliente LIMIT 1) as telefono,
                       CONCAT(c.barrio, ', Zona ', c.zona, ', ', c.calle, ' ', c.num_casa) as direccion
                FROM cliente c
                ORDER BY c.id_cliente DESC
            """
            registros = ejecutar_query(query, fetch_all=True)
        if registros:
            for reg in registros:
                tree_clientes.insert("", "end", values=(reg[0], reg[1], reg[2], reg[3], reg[4] or "", reg[5] or ""))
        else:
            tree_clientes.insert("", "end", values=("No hay datos", "", "", "", "", ""))

    def mostrar_detalle(event):
        seleccion = tree_clientes.selection()
        if seleccion:
            valores = tree_clientes.item(seleccion[0])["values"]
            if valores[0] != "No hay datos":
                id_cliente = valores[0]
                cliente_seleccionado_id.set(id_cliente)
                cliente_seleccionado_nombre.set(f"{valores[1]} {valores[2]}")

                query_servicios = """
                    SELECT s.tipo, s.precio
                    FROM cliente_servico cs
                    JOIN servicio s ON cs.servicio_id = s.id_servicio
                    WHERE cs.id_cliente = %s
                """
                servicios = ejecutar_query(query_servicios, (id_cliente,), fetch_all=True) or []

                total_mensual = 0
                servicios_texto = ""
                for s in servicios:
                    total_mensual += s[1]
                    servicios_texto += f"• {s[0]} - Q{s[1]:.2f}\n"

                if servicios:
                    servicios_info = f"\n=== SERVICIOS CONTRATADOS ===\n{servicios_texto}\nTOTAL MENSUAL: Q{total_mensual:.2f}"
                else:
                    servicios_info = "\n=== SERVICIOS CONTRATADOS ===\nNo tiene servicios contratados"

                detalle = f"""
=== CLIENTE ===
ID: {valores[0]}
Nombre: {valores[1]} {valores[2]}
DPI: {valores[3]}
Teléfono: {valores[4]}
Dirección: {valores[5]}
{servicios_info}
"""
                texto_detalle.delete(1.0, tk.END)
                texto_detalle.insert(1.0, detalle)

                if total_mensual > 0:
                    entry_monto.delete(0, tk.END)
                    entry_monto.insert(0, f"{total_mensual:.2f}")

    def registrar_pago():
        id_cliente = cliente_seleccionado_id.get()
        if not id_cliente:
            messagebox.showwarning("Sin selección", "Seleccione un cliente de la lista")
            return

        try:
            monto = float(entry_monto.get().strip())
            if monto <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Datos inválidos", "Ingrese un monto válido mayor a 0")
            entry_monto.focus()
            return

        metodo = combo_metodo.get()
        id_metodo = None
        for m in metodo_pago_data:
            if m[1] == metodo:
                id_metodo = m[0]
                break

        if id_metodo is None:
            messagebox.showerror("Error", "Método de pago no válido")
            return

        from datetime import datetime
        fecha = datetime.now().strftime("%Y-%m-%d")
        id_cobrador = 1

        query_cs = "SELECT id_cliente_servicio FROM cliente_servico WHERE id_cliente = %s LIMIT 1"
        cs_data = ejecutar_query(query_cs, (id_cliente,), fetch_one=True)

        if not cs_data:
            messagebox.showerror("Error", "El cliente no tiene servicios contratados")
            return

        id_cliente_servicio = cs_data[0]

        query_factura = "INSERT INTO factura (fecha_emicion, total, id_cliente_servicio, tipo_factura) VALUES (%s, %s, %s, %s)"
        id_factura = ejecutar_query(query_factura, (fecha, monto, id_cliente_servicio, "COBRO"), commit=True)

        if not id_factura:
            messagebox.showerror("Error", "No se pudo crear la factura")
            return

        query_pago = "INSERT INTO pago (fecha, monto, id_cobrador, factura_id_factura, id_metodo_pago) VALUES (%s, %s, %s, %s, %s)"
        resultado = ejecutar_query(query_pago, (fecha, monto, id_cobrador, id_factura, id_metodo), commit=True)

        if resultado:
            messagebox.showinfo("Éxito", f"Factura #{id_factura} creada y pago de Q{monto:.2f} registrado")
            entry_monto.delete(0, tk.END)
            entry_descripcion.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "No se pudo registrar el pago")

    def buscar_clientes():
        texto = entry_buscar.get().strip()
        cargar_clientes(texto)

    def limpiar_busqueda():
        entry_buscar.delete(0, tk.END)
        cargar_clientes()

    btn_buscar.config(command=buscar_clientes)
    btn_refrescar.config(command=limpiar_busqueda)
    tree_clientes.bind("<<TreeviewSelect>>", mostrar_detalle)
    entry_buscar.bind("<Return>", lambda e: buscar_clientes())
    btn_registrar.config(command=registrar_pago)

    cargar_metodos_pago()
    cargar_clientes()

def ventana_mis_servicios_asignados():
    ventana = tk.Toplevel()
    ventana.title("Mis Servicios Asignados - Cable Internet")
    ventana.attributes('-fullscreen', True)
    ventana.transient()
    ventana.grab_set()
    ventana.bind("<Escape>", lambda e: ventana.destroy())

    tk.Label(ventana, text="Servicios Asignados para Cobro", font=("Arial", 20, "bold")).pack(pady=20)

    frame_buscar = tk.Frame(ventana)
    frame_buscar.pack(pady=10)
    tk.Label(frame_buscar, text="Buscar:", font=("Arial", 12)).pack(side="left")
    entry_buscar = tk.Entry(frame_buscar, font=("Arial", 12), width=30)
    entry_buscar.pack(side="left", padx=10)
    btn_buscar = tk.Button(frame_buscar, text="Buscar", bg="#2196F3", fg="white", font=("Arial", 12))
    btn_buscar.pack(side="left")
    btn_refrescar = tk.Button(frame_buscar, text="Refrescar", bg="#9E9E9E", fg="white", font=("Arial", 12))
    btn_refrescar.pack(side="left", padx=5)

    frame_lista = tk.Frame(ventana)
    frame_lista.pack(fill="both", expand=True, padx=20, pady=10)

    columnas = ("ID Servicio", "Tipo de Servicio", "Precio Mensual", "Estado")
    tree = ttk.Treeview(frame_lista, columns=columnas, show="headings", height=15)
    anchos = {"ID Servicio": 80, "Tipo de Servicio": 350, "Precio Mensual": 120, "Estado": 100}
    for col in columnas:
        tree.heading(col, text=col)
        tree.column(col, width=anchos.get(col, 100))
    tree.pack(fill="both", expand=True, padx=10, pady=10)

    scroll = ttk.Scrollbar(frame_lista, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scroll.set)
    scroll.pack(side="right", fill="y")

    frame_detalle = tk.LabelFrame(ventana, text="Clientes con este Servicio", font=("Arial", 12, "bold"))
    frame_detalle.pack(fill="both", expand=True, padx=20, pady=10)

    columnas_clientes = ("ID Cliente", "Nombre", "Teléfono", "Dirección", "Estado Servicio")
    tree_clientes = ttk.Treeview(frame_detalle, columns=columnas_clientes, show="headings", height=8)
    anchos_clientes = {"ID Cliente": 80, "Nombre": 200, "Teléfono": 120, "Dirección": 300, "Estado Servicio": 120}
    for col in columnas_clientes:
        tree_clientes.heading(col, text=col)
        tree_clientes.column(col, width=anchos_clientes.get(col, 100))
    tree_clientes.pack(fill="both", expand=True, padx=10, pady=10)

    scroll_clientes = ttk.Scrollbar(frame_detalle, orient="vertical", command=tree_clientes.yview)
    tree_clientes.configure(yscrollcommand=scroll_clientes.set)
    scroll_clientes.pack(side="right", fill="y")

    btn_cerrar = tk.Button(ventana, text="Cerrar", command=ventana.destroy, bg="#f44336", fg="white", font=("Arial", 12), width=20)
    btn_cerrar.pack(pady=0)

    servicios_asignados = []
    clientes_servicio = []

    def cargar_servicios_asignados(busqueda=""):
        nonlocal servicios_asignados
        for item in tree.get_children():
            tree.delete(item)
        if busqueda.isdigit():
            query = """
                SELECT s.id_servicio, s.tipo, s.precio, s.estado
                FROM servicio s
                JOIN asignacion_cobrador ac ON s.id_servicio = ac.servicio_id
                WHERE s.estado = 'ACTIVO' AND s.id_servicio = %s
                ORDER BY s.tipo
            """
            params = (int(busqueda),)
            servicios_asignados = ejecutar_query(query, params, fetch_all=True) or []
        elif busqueda:
            query = """
                SELECT s.id_servicio, s.tipo, s.precio, s.estado
                FROM servicio s
                JOIN asignacion_cobrador ac ON s.id_servicio = ac.servicio_id
                WHERE s.estado = 'ACTIVO' AND s.tipo LIKE %s
                ORDER BY s.tipo
            """
            params = (f"%{busqueda}%",)
            servicios_asignados = ejecutar_query(query, params, fetch_all=True) or []
        else:
            query = """
                SELECT s.id_servicio, s.tipo, s.precio, s.estado
                FROM servicio s
                JOIN asignacion_cobrador ac ON s.id_servicio = ac.servicio_id
                WHERE s.estado = 'ACTIVO'
                ORDER BY s.tipo
            """
            servicios_asignados = ejecutar_query(query, fetch_all=True) or []
        if servicios_asignados:
            for s in servicios_asignados:
                tree.insert("", "end", values=(s[0], s[1], f"Q{s[2]:.2f}", s[3]))
        else:
            tree.insert("", "end", values=("No hay datos", "", "", ""))

    def cargar_clientes_por_servicio(event):
        seleccion = tree.selection()
        if seleccion:
            valores = tree.item(seleccion[0])["values"]
            if valores[0] != "No hay datos":
                id_servicio = valores[0]
                for item in tree_clientes.get_children():
                    tree_clientes.delete(item)
                query = """
                    SELECT c.id_cliente, c.nombre, c.apellido,
                           (SELECT num_telefono FROM telefono WHERE id_cliente = c.id_cliente LIMIT 1) as telefono,
                           CONCAT(c.barrio, ', Zona ', c.zona, ', ', c.calle, ' ', c.num_casa) as direccion,
                           cs.estado
                    FROM cliente_servico cs
                    JOIN cliente c ON cs.id_cliente = c.id_cliente
                    WHERE cs.servicio_id = %s
                    ORDER BY c.nombre
                """
                clientes = ejecutar_query(query, (id_servicio,), fetch_all=True) or []
                if clientes:
                    for cl in clientes:
                        tree_clientes.insert("", "end", values=(cl[0], f"{cl[1]} {cl[2]}", cl[3] or "", cl[4] or "", cl[5]))
                else:
                    tree_clientes.insert("", "end", values=("No hay clientes", "", "", "", ""))

    def buscar_servicios():
        texto = entry_buscar.get().strip()
        cargar_servicios_asignados(texto)

    def limpiar_busqueda():
        entry_buscar.delete(0, tk.END)
        cargar_servicios_asignados()
        for item in tree_clientes.get_children():
            tree_clientes.delete(item)

    btn_buscar.config(command=buscar_servicios)
    btn_refrescar.config(command=limpiar_busqueda)
    tree.bind("<<TreeviewSelect>>", cargar_clientes_por_servicio)
    entry_buscar.bind("<Return>", lambda e: buscar_servicios())

    cargar_servicios_asignados()

def ventana_gestion_materiales():
    ventana = tk.Toplevel()
    ventana.title("Gestión de Materiales - Cable Internet")
    ventana.attributes('-fullscreen', True)
    ventana.transient()
    ventana.grab_set()
    ventana.bind("<Escape>", lambda e: ventana.destroy())

    material_seleccionado_id = tk.IntVar()

    panel_principal = tk.PanedWindow(ventana, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, sashwidth=5)
    panel_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    frame_lista = tk.LabelFrame(panel_principal, text="Materiales Registrados", font=("Arial", 12, "bold"))
    panel_principal.add(frame_lista, width=600)

    frame_buscar = tk.Frame(frame_lista)
    frame_buscar.pack(fill="x", padx=5, pady=5)
    tk.Label(frame_buscar, text="Buscar:", font=("Arial", 10)).pack(side="left")
    entry_buscar = tk.Entry(frame_buscar, font=("Arial", 10), width=30)
    entry_buscar.pack(side="left", padx=5)

    columnas_materiales = ("ID", "Nombre", "Stock Actual", "Precio Compra", "Estado")
    tree_materiales = ttk.Treeview(frame_lista, columns=columnas_materiales, show="headings", height=15)
    anchos = {"ID": 50, "Nombre": 250, "Stock Actual": 100, "Precio Compra": 120, "Estado": 100}
    for col in columnas_materiales:
        tree_materiales.heading(col, text=col)
        tree_materiales.column(col, width=anchos.get(col, 100))
    tree_materiales.pack(side="left", fill="both", expand=True, padx=5, pady=5)

    scroll_materiales = ttk.Scrollbar(frame_lista, orient="vertical", command=tree_materiales.yview)
    tree_materiales.configure(yscrollcommand=scroll_materiales.set)
    scroll_materiales.pack(side="right", fill="y")

    panel_derecho = tk.Frame(panel_principal)
    panel_principal.add(panel_derecho, width=500)

    frame_form = tk.LabelFrame(panel_derecho, text="Datos del Material", font=("Arial", 12, "bold"))
    frame_form.pack(fill="x", pady=5)

    campos = [
        ("Nombre *:", "nombre"),
        ("Stock Actual:", "stock"),
        ("Precio Compra (Q):", "precio"),
        ("Estado:", "estado")
    ]

    entries = {}
    for i, (label, key) in enumerate(campos):
        tk.Label(frame_form, text=label, font=("Arial", 10)).grid(row=i, column=0, padx=5, pady=5, sticky="e")
        if key == "estado":
            entry = ttk.Combobox(frame_form, font=("Arial", 10), width=37)
            entry['values'] = ("DISPONIBLE", "AGOTADO", "DESCONTINUADO")
            entry.current(0)
        else:
            entry = tk.Entry(frame_form, font=("Arial", 10), width=40)
        entry.grid(row=i, column=1, padx=5, pady=5, sticky="w")
        entries[key] = entry

    frame_botones_form = tk.Frame(frame_form)
    frame_botones_form.grid(row=len(campos), column=0, columnspan=2, pady=10)

    btn_guardar = tk.Button(frame_botones_form, text="Guardar Material", bg="#4CAF50", fg="white", width=12)
    btn_guardar.pack(side="left", padx=5)
    btn_actualizar = tk.Button(frame_botones_form, text="Actualizar Material", bg="#2196F3", fg="white", width=14,
                               state="disabled")
    btn_actualizar.pack(side="left", padx=5)
    btn_eliminar = tk.Button(frame_botones_form, text="Eliminar Material", bg="#f44336", fg="white", width=12,
                             state="disabled")
    btn_eliminar.pack(side="left", padx=5)
    btn_nuevo = tk.Button(frame_botones_form, text="Nuevo Material", bg="#FF9800", fg="white", width=12)
    btn_nuevo.pack(side="left", padx=5)

    btn_cerrar = tk.Button(panel_derecho, text="Cerrar", command=ventana.destroy, bg="#f44336", fg="white",
                           width=15)
    btn_cerrar.pack(pady=10)

    def limpiar_formulario():
        entries["nombre"].delete(0, tk.END)
        entries["stock"].delete(0, tk.END)
        entries["precio"].delete(0, tk.END)
        entries["estado"].current(0)
        entries["nombre"].focus()
        btn_actualizar.config(state="disabled")
        btn_eliminar.config(state="disabled")
        material_seleccionado_id.set(0)

    def cargar_materiales(busqueda=""):
        for item in tree_materiales.get_children():
            tree_materiales.delete(item)
        if busqueda.isdigit():
            query = "SELECT id_material, nombre, stock_actual, precio_compra, estado FROM material WHERE id_material = %s"
            params = (int(busqueda),)
            registros = ejecutar_query(query, params, fetch_all=True)
        elif busqueda:
            query = "SELECT id_material, nombre, stock_actual, precio_compra, estado FROM material WHERE nombre LIKE %s"
            params = (f"%{busqueda}%",)
            registros = ejecutar_query(query, params, fetch_all=True)
        else:
            query = "SELECT id_material, nombre, stock_actual, precio_compra, estado FROM material ORDER BY id_material DESC"
            registros = ejecutar_query(query, fetch_all=True)
        if registros:
            for reg in registros:
                tree_materiales.insert("", "end", values=(reg[0], reg[1], reg[2], f"Q{reg[3]:.2f}", reg[4]))
        else:
            tree_materiales.insert("", "end", values=("No hay datos", "", "", "", ""))

    def guardar_material():
        nombre = entries["nombre"].get().strip()
        stock = entries["stock"].get().strip()
        precio = entries["precio"].get().strip()
        estado = entries["estado"].get()

        if not nombre:
            messagebox.showwarning("Datos incompletos", "El nombre del material es obligatorio")
            entries["nombre"].focus()
            return

        try:
            stock_int = int(stock) if stock else 0
        except ValueError:
            messagebox.showwarning("Datos inválidos", "El stock debe ser un número entero")
            entries["stock"].focus()
            return

        try:
            precio_float = float(precio) if precio else 0.0
        except ValueError:
            messagebox.showwarning("Datos inválidos", "El precio debe ser un número")
            entries["precio"].focus()
            return

        query = "INSERT INTO material (nombre, stock_actual, precio_compra, estado) VALUES (%s, %s, %s, %s)"
        resultado = ejecutar_query(query, (nombre, stock_int, precio_float, estado), commit=True)
        if resultado:
            messagebox.showinfo("Éxito", f"Material '{nombre}' registrado")
            limpiar_formulario()
            cargar_materiales()
        else:
            messagebox.showerror("Error", "No se pudo guardar el material")

    def actualizar_material():
        id_material = material_seleccionado_id.get()
        if not id_material:
            messagebox.showwarning("Sin selección", "Seleccione un material de la lista")
            return

        nombre = entries["nombre"].get().strip()
        stock = entries["stock"].get().strip()
        precio = entries["precio"].get().strip()
        estado = entries["estado"].get()

        if not nombre:
            messagebox.showwarning("Datos incompletos", "El nombre del material es obligatorio")
            entries["nombre"].focus()
            return

        try:
            stock_int = int(stock) if stock else 0
        except ValueError:
            messagebox.showwarning("Datos inválidos", "El stock debe ser un número entero")
            entries["stock"].focus()
            return

        try:
            precio_float = float(precio) if precio else 0.0
        except ValueError:
            messagebox.showwarning("Datos inválidos", "El precio debe ser un número")
            entries["precio"].focus()
            return

        query = "UPDATE material SET nombre=%s, stock_actual=%s, precio_compra=%s, estado=%s WHERE id_material=%s"
        resultado = ejecutar_query(query, (nombre, stock_int, precio_float, estado, id_material), commit=True)
        if resultado is not None:
            messagebox.showinfo("Éxito", "Material actualizado")
            cargar_materiales()
        else:
            messagebox.showerror("Error", "No se pudo actualizar")

    def eliminar_material():
        id_material = material_seleccionado_id.get()
        if not id_material:
            messagebox.showwarning("Sin selección", "Seleccione un material de la lista")
            return
        nombre = entries["nombre"].get().strip()
        confirmar = messagebox.askyesno("Confirmar", f"¿Eliminar el material '{nombre}'?")
        if confirmar:
            ejecutar_query("DELETE FROM material WHERE id_material = %s", (id_material,), commit=True)
            messagebox.showinfo("Éxito", "Material eliminado")
            limpiar_formulario()
            cargar_materiales()

    def on_material_seleccionado(event):
        seleccion = tree_materiales.selection()
        if seleccion:
            valores = tree_materiales.item(seleccion[0])["values"]
            if valores[0] != "No hay datos":
                id_material = valores[0]
                material_seleccionado_id.set(id_material)
                query = "SELECT nombre, stock_actual, precio_compra, estado FROM material WHERE id_material = %s"
                datos_material = ejecutar_query(query, (id_material,), fetch_one=True)
                if datos_material:
                    entries["nombre"].delete(0, tk.END)
                    entries["nombre"].insert(0, datos_material[0] or "")
                    entries["stock"].delete(0, tk.END)
                    entries["stock"].insert(0, str(datos_material[1]) if datos_material[1] is not None else "")
                    entries["precio"].delete(0, tk.END)
                    entries["precio"].insert(0, str(datos_material[2]) if datos_material[2] is not None else "")
                    entries["estado"].set(datos_material[3] or "DISPONIBLE")
                btn_actualizar.config(state="normal")
                btn_eliminar.config(state="normal")
        else:
            limpiar_formulario()

    def buscar_materiales():
        texto = entry_buscar.get().strip()
        cargar_materiales(texto)

    def limpiar_busqueda():
        entry_buscar.delete(0, tk.END)
        cargar_materiales()

    def nuevo_material():
        limpiar_formulario()

    btn_guardar.config(command=guardar_material)
    btn_actualizar.config(command=actualizar_material)
    btn_eliminar.config(command=eliminar_material)
    btn_nuevo.config(command=nuevo_material)
    btn_buscar = tk.Button(frame_buscar, text="Buscar", command=buscar_materiales, bg="#2196F3", fg="white")
    btn_buscar.pack(side="left", padx=5)
    btn_refrescar = tk.Button(frame_buscar, text="Refrescar", command=limpiar_busqueda, bg="#9E9E9E", fg="white")
    btn_refrescar.pack(side="left", padx=5)

    tree_materiales.bind("<<TreeviewSelect>>", on_material_seleccionado)
    entry_buscar.bind("<Return>", lambda e: buscar_materiales())

    cargar_materiales()

def ventana_gestion_facturas():
    ventana = tk.Toplevel()
    ventana.title("Gestión de Facturas - Cable Internet")
    ventana.attributes('-fullscreen', True)
    ventana.transient()
    ventana.grab_set()
    ventana.bind("<Escape>", lambda e: ventana.destroy())

    tk.Label(ventana, text="Facturas Emitidas", font=("Arial", 20, "bold")).pack(pady=20)

    frame_buscar = tk.Frame(ventana)
    frame_buscar.pack(pady=10)
    tk.Label(frame_buscar, text="Buscar por Cliente:", font=("Arial", 12)).pack(side="left")
    entry_buscar = tk.Entry(frame_buscar, font=("Arial", 12), width=30)
    entry_buscar.pack(side="left", padx=10)
    btn_buscar = tk.Button(frame_buscar, text="Buscar", bg="#2196F3", fg="white", font=("Arial", 12))
    btn_buscar.pack(side="left")
    btn_refrescar = tk.Button(frame_buscar, text="Refrescar", bg="#9E9E9E", fg="white", font=("Arial", 12))
    btn_refrescar.pack(side="left", padx=5)

    frame_lista = tk.Frame(ventana)
    frame_lista.pack(fill="both", expand=True, padx=20, pady=10)

    columnas = ("ID Factura", "Cliente", "Fecha", "Total", "Tipo", "Servicio")
    tree = ttk.Treeview(frame_lista, columns=columnas, show="headings", height=18)
    anchos = {"ID Factura": 80, "Cliente": 200, "Fecha": 100, "Total": 100, "Tipo": 100, "Servicio": 200}
    for col in columnas:
        tree.heading(col, text=col)
        tree.column(col, width=anchos.get(col, 100))
    tree.pack(fill="both", expand=True, padx=10, pady=10)

    scroll = ttk.Scrollbar(frame_lista, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scroll.set)
    scroll.pack(side="right", fill="y")

    frame_detalle = tk.LabelFrame(ventana, text="Detalle de Factura", font=("Arial", 12, "bold"))
    frame_detalle.pack(fill="both", expand=True, padx=20, pady=10)

    texto_detalle = tk.Text(frame_detalle, font=("Arial", 11), wrap="word", height=8)
    texto_detalle.pack(fill="both", expand=True, padx=10, pady=10)

    btn_cerrar = tk.Button(ventana, text="Cerrar", command=ventana.destroy, bg="#f44336", fg="white", font=("Arial", 12), width=20)
    btn_cerrar.pack(pady=10)

    def cargar_facturas(busqueda=""):
        for item in tree.get_children():
            tree.delete(item)
        if busqueda:
            query = """
                SELECT f.id_factura, c.nombre, c.apellido, f.fecha_emicion, f.total, f.tipo_factura, s.tipo
                FROM factura f
                JOIN cliente_servico cs ON f.id_cliente_servicio = cs.id_cliente_servicio
                JOIN cliente c ON cs.id_cliente = c.id_cliente
                JOIN servicio s ON cs.servicio_id = s.id_servicio
                WHERE c.nombre LIKE %s OR c.apellido LIKE %s
                ORDER BY f.fecha_emicion DESC
            """
            params = (f"%{busqueda}%", f"%{busqueda}%")
            registros = ejecutar_query(query, params, fetch_all=True) or []
        else:
            query = """
                SELECT f.id_factura, c.nombre, c.apellido, f.fecha_emicion, f.total, f.tipo_factura, s.tipo
                FROM factura f
                JOIN cliente_servico cs ON f.id_cliente_servicio = cs.id_cliente_servicio
                JOIN cliente c ON cs.id_cliente = c.id_cliente
                JOIN servicio s ON cs.servicio_id = s.id_servicio
                ORDER BY f.fecha_emicion DESC
            """
            registros = ejecutar_query(query, fetch_all=True) or []
        if registros:
            for reg in registros:
                tree.insert("", "end", values=(reg[0], f"{reg[1]} {reg[2]}", reg[3], f"Q{reg[4]:.2f}", reg[5], reg[6]))
        else:
            tree.insert("", "end", values=("No hay datos", "", "", "", "", ""))

    def mostrar_detalle(event):
        seleccion = tree.selection()
        if seleccion:
            valores = tree.item(seleccion[0])["values"]
            if valores[0] != "No hay datos":
                id_factura = valores[0]
                query = """
                    SELECT f.id_factura, c.nombre, c.apellido, c.dpi,
                           c.barrio, c.zona, c.calle, c.num_casa,
                           s.tipo, s.precio, f.fecha_emicion, f.total, f.tipo_factura
                    FROM factura f
                    JOIN cliente_servico cs ON f.id_cliente_servicio = cs.id_cliente_servicio
                    JOIN cliente c ON cs.id_cliente = c.id_cliente
                    JOIN servicio s ON cs.servicio_id = s.id_servicio
                    WHERE f.id_factura = %s
                """
                datos = ejecutar_query(query, (id_factura,), fetch_one=True)
                if datos:
                    detalle = f"""
=== FACTURA #{datos[0]} ===

FECHA: {datos[10]}
TIPO: {datos[12]}
TOTAL: Q{datos[11]:.2f}

DATOS DEL CLIENTE:
Nombre: {datos[1]} {datos[2]}
DPI: {datos[3]}
Dirección: {datos[4]}, Zona {datos[5]}, {datos[6]} {datos[7]}

SERVICIO:
Tipo: {datos[8]}
Precio: Q{datos[9]:.2f}
"""
                    texto_detalle.delete(1.0, tk.END)
                    texto_detalle.insert(1.0, detalle)

    def buscar_facturas():
        texto = entry_buscar.get().strip()
        cargar_facturas(texto)
        texto_detalle.delete(1.0, tk.END)

    def limpiar_busqueda():
        entry_buscar.delete(0, tk.END)
        cargar_facturas()
        texto_detalle.delete(1.0, tk.END)

    btn_buscar.config(command=buscar_facturas)
    btn_refrescar.config(command=limpiar_busqueda)
    tree.bind("<<TreeviewSelect>>", mostrar_detalle)
    entry_buscar.bind("<Return>", lambda e: buscar_facturas())

    cargar_facturas()

def abrir_panel_principal(nombre, rol):
    panel = tk.Tk()
    panel.title("Cable Internet - Panel de Control")
    panel.attributes('-fullscreen', True)
    panel.bind("<Escape>", lambda e: panel.destroy())

    ancho = panel.winfo_screenwidth()
    alto = panel.winfo_screenheight()

    ruta_base = os.path.dirname(__file__)
    ruta_fondo = os.path.join(ruta_base, "imagenes_telecable", "fondo.png")

    if os.path.exists(ruta_fondo):
        fondo = Image.open(ruta_fondo)
        fondo = fondo.resize((ancho, alto), Image.Resampling.LANCZOS)
        fondo_tk = ImageTk.PhotoImage(fondo)
        lienzo = tk.Canvas(panel, width=ancho, height=alto)
        lienzo.pack(fill="both", expand=True)
        lienzo.create_image(0, 0, image=fondo_tk, anchor="nw")
        panel.fondo_tk = fondo_tk
    else:
        panel.configure(bg="white")
        lienzo = None

    if lienzo:
        lienzo.create_text(ancho // 2, 80, text=f"Bienvenido, {nombre}", font=("Arial", 24, "bold"), fill="white")
        lienzo.create_text(ancho // 2, 130, text=f"Rol: {rol}", font=("Arial", 16), fill="white")
    else:
        tk.Label(panel, text=f"Bienvenido, {nombre}", font=("Arial", 24, "bold")).pack(pady=20)
        tk.Label(panel, text=f"Rol: {rol}", font=("Arial", 16)).pack()

    frame_botones = tk.Frame(panel)
    if lienzo:
        lienzo.create_window(ancho // 2, 370, window=frame_botones)
    else:
        frame_botones.pack(pady=30)

    if rol == "administrador":
        botones = [
            ("➕ Clientes", ventana_gestion_clientes),
            ("🏍️ Cobradores", ventana_gestion_cobradores),
            ("🔗 Asignar Servicios a Cobradores", ventana_asignar_cliente_servicio_cobrador),
            ("📋 Asignar Servicio a Cliente", ventana_asignar_servicio_cliente),
            ("📊 Control de Cobros", ventana_control_cobros),
            ("🛠️ Servicios", ventana_gestion_servicios),
            ("👷 Técnicos", ventana_gestion_tecnicos),
            ("📋 Órdenes de Trabajo", ventana_ordenes_trabajo_admin),
            ("📦 Materiales", ventana_gestion_materiales),
            ("💰 Facturación", ventana_gestion_facturas),
        ]
    elif rol == "tecnico":
        botones = [
            ("📋 Ver Órdenes de Instalación", ventana_ordenes_trabajo_tecnico),
            ("🔧 Ver Instalaciones Asignadas", ventana_instalaciones_tecnico),
            ("✅ Ver Chequeos Asignados", ventana_chequeos_tecnico),
            ("💰 Facturar Instalación/Chequeo", ventana_facturar_tecnico),
        ]
    elif rol == "cobrador":
        botones = [
            ("💰 Facturar", ventana_facturar),
            ("📊 Mi Resumen Diario", ventana_control_cobros),
            ("🔗 Mis Servicios Asignados", ventana_mis_servicios_asignados),
        ]
    else:
        botones = []

    for texto, comando in botones:
        if comando:
            btn = tk.Button(frame_botones, text=texto, font=("Arial", 12), width=28, pady=5, command=comando)
        else:
            btn = tk.Button(frame_botones, text=texto, font=("Arial", 12), width=28, pady=5, state="disabled")
        btn.pack(pady=6)

    def cerrar_sesion():
        panel.destroy()
        ventana_login()

    btn_cerrar_sesion = tk.Button(panel, text="Cerrar Sesión", command=cerrar_sesion, bg="#f44336", fg="white", font=("Arial", 12), width=25, pady=5)
    if lienzo:
        lienzo.create_window(ancho // 2, 680, window=btn_cerrar_sesion)
    else:
        btn_cerrar_sesion.pack(pady=20)

    panel.mainloop()

if __name__ == "__main__":
    crear_admin_default()
    ventana_login()