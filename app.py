import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from config import DevelopmentConfig
import forms
from models import *
from flask_wtf import CSRFProtect
from forms import LoginForm, RegistrationForm

# Inicializar la aplicación Flask
app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
app.secret_key = "clavesecretapizzeria"
csrf = CSRFProtect(app)

# Configuración de Flask-Login
login_manager = LoginManager()
login_manager.login_message = "Debes iniciar sesión para acceder a esta página."

login_manager.init_app(app)
login_manager.login_view = 'login'

# Cargar usuario en sesión
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Ruta principal - redirige según estado de autenticación
@app.route('/')
def index():
  
        return redirect(url_for('login'))

# Ruta para iniciar sesión
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('sistema'))
        else:
            flash('Usuario o contraseña incorrectos', 'danger')
    
    return render_template('login.html', form=form)

# Ruta para cerrar sesión
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión correctamente.', 'info')
    return redirect(url_for('login'))

# Ruta para registrarse
@app.route('/register', methods=['GET', 'POST'])
def register():
    
        
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('El nombre de usuario ya está en uso', 'danger')
        else:
            user = User(username=form.username.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Registro exitoso. Ahora puedes iniciar sesión.', 'success')
            return redirect(url_for('login'))
    
    return render_template('registro.html', form=form)

# Definir precios
PRECIOS_PIZZA = {"Chica $40": 40, "Mediana $80": 80, "Grande $120": 120}
PRECIOS_INGREDIENTES = {"Jamon $10": 10, "Piña $10": 10, "Champiñones $10": 10}

# Ruta del sistema (protegida)
@app.route("/sistema", methods=["GET", "POST"])
@login_required
def sistema():
    busqueda_form = forms.BusquedaForm(request.form)
    pedido_form = forms.PedidoForm(request.form)
    fecha_actual = datetime.now().strftime('%Y-%m-%d')
    pedido_form.fecha_compra.data = fecha_actual

    pedidos = []
    if os.path.exists("pedidos_temp.txt"):
        with open("pedidos_temp.txt", "r") as archivo:
            for linea in archivo:
                datos = linea.strip().split(", ")
                pedido = {
                    "id": int(datos[0]),
                    "nombre": datos[1],
                    "direccion": datos[2],
                    "telefono": datos[3],
                    "fecha_compra": datos[4],
                    "tamanio": datos[5],
                    "ingredientes": datos[6],
                    "num_pizzas": int(datos[7]),
                    "subtotal": float(datos[8])
                }
                pedidos.append(pedido)

    ventas_del_dia = Cliente.query.filter(db.func.date(Cliente.fecha_compra) == fecha_actual).all()
    total_ventas_del_dia = sum(venta.total for venta in ventas_del_dia)

    resultados_busqueda, total_busqueda = [], 0

    if request.method == "POST":
        if "Agregar" in request.form and pedido_form.validate():
            nuevo_id = max([p["id"] for p in pedidos], default=0) + 1
            precio_base = PRECIOS_PIZZA[pedido_form.tamanioPizza.data]
            precio_ingrediente = PRECIOS_INGREDIENTES[pedido_form.ingredientes.data]
            subtotal = (precio_base + precio_ingrediente) * pedido_form.numPizzas.data

            with open("pedidos_temp.txt", "a") as archivo:
                archivo.write(f"{nuevo_id}, {pedido_form.nombre.data}, {pedido_form.direccion.data}, "
                              f"{pedido_form.telefono.data}, {pedido_form.fecha_compra.data}, "
                              f"{pedido_form.tamanioPizza.data}, {pedido_form.ingredientes.data}, "
                              f"{pedido_form.numPizzas.data}, {subtotal}\n")

            flash("Pizza agregada correctamente.", "success")
            return redirect(url_for('sistema'))  # Cambio aquí de 'index' a 'sistema'

        elif "Quitar" in request.form:
            id_quitar = request.form.get("id_quitar")
            pedidos = [p for p in pedidos if str(p["id"]) != id_quitar]

            with open("pedidos_temp.txt", "w") as archivo:
                for p in pedidos:
                    archivo.write(f"{p['id']}, {p['nombre']}, {p['direccion']}, {p['telefono']}, "
                                  f"{p['fecha_compra']}, {p['tamanio']}, {p['ingredientes']}, {p['num_pizzas']}, {p['subtotal']}\n")

            flash("Producto eliminado del pedido", "info")
            return redirect(url_for('sistema'))  # Cambio aquí de 'index' a 'sistema'

        elif "Terminar" in request.form and pedidos:
            total = sum(p["subtotal"] for p in pedidos)
            nuevo_cliente = Cliente(
                nombre=pedidos[0]["nombre"], direccion=pedidos[0]["direccion"],
                telefono=pedidos[0]["telefono"], fecha_compra=datetime.strptime(pedidos[0]["fecha_compra"], '%Y-%m-%d'),
                total=total
            )
            db.session.add(nuevo_cliente)
            db.session.commit()
            os.remove("pedidos_temp.txt")
            flash(f"Pedido completado. Total a pagar: ${total}", "success")
            return redirect(url_for('sistema'))  # Cambio aquí de 'index' a 'sistema'

        elif "buscar" in request.form and busqueda_form.validate():
            fecha_obj = datetime.strptime(busqueda_form.fecha.data, '%Y-%m-%d')
            resultados_busqueda = Cliente.query.filter(db.func.date(Cliente.fecha_compra) == fecha_obj.date()).all()
            total_busqueda = sum(venta.total for venta in resultados_busqueda)

    return render_template("index.html", pedido_form=pedido_form, busqueda_form=busqueda_form,
                           pedidos=pedidos, resultados_busqueda=resultados_busqueda,
                           total_busqueda=total_busqueda, fecha_actual=fecha_actual,
                           ventas_del_dia=ventas_del_dia, total_ventas_del_dia=total_ventas_del_dia)

# Ejecutar la aplicación
if __name__ == "__main__":
    db.init_app(app)
    csrf.init_app(app)
    with app.app_context():
        db.create_all()
    app.run(debug=True)