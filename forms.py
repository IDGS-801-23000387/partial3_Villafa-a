from wtforms import Form
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Length
from wtforms import StringField,PasswordField,EmailField,BooleanField,SubmitField, IntegerField, RadioField, HiddenField
from wtforms import validators

class PedidoForm(Form):
    nombre = StringField('Nombre', [
        validators.DataRequired(message='El nombre es requerido'),
        validators.Length(min=4, max=20, message='Requiere min=4 max=20')
    ])
    direccion = StringField('Dirección', [
        validators.DataRequired(message='La dirección es requerida')
    ])
    telefono = IntegerField("Teléfono", [
        validators.DataRequired(message="El campo es requerido"),
        validators.NumberRange(min=1, max=9999999999, message="Número de teléfono no válido")
    ])
    numPizzas = IntegerField("Número de Pizzas", [
        validators.DataRequired(message="El campo es requerido"),
        validators.NumberRange(min=1, max=31, message="El número de pizzas debe ser válido")
    ])
    tamanioPizza = RadioField("Tamaño Pizza", choices=[
        ("Chica $40", "Chica $40"),
        ("Mediana $80", "Mediana $80"),
        ("Grande $120", "Grande $120")
    ], validators=[validators.DataRequired(message="El campo es requerido")])
    fecha_compra = HiddenField() 
    ingredientes = RadioField("Ingredientes", choices=[
        ("Jamon $10", "Jamon $10"),
        ("Piña $10", "Piña $10"),
        ("Champiñones $10", "Champiñones $10")
    ], validators=[validators.DataRequired(message="El campo es requerido")])
    
class BusquedaForm(Form):
    tipo_busqueda = RadioField("Tipo de Búsqueda", choices=[
        ("dia", "Por Día"),
        ("mes", "Por Mes")
    ],  validators=[validators.DataRequired(message="El campo es requerido")])
    fecha = StringField("Fecha (YYYY-MM-DD o YYYY-MM)", validators=[validators.DataRequired(message="El campo es requerido")])
    buscar = SubmitField("Buscar")
    
class LoginForm(FlaskForm):
    username = StringField('Nombre de usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Iniciar sesión')

class RegistrationForm(FlaskForm):
    name= StringField('Nombre ', validators=[DataRequired(), Length(min=4, max=50)])
    username = StringField('Nombre de usuario', validators=[DataRequired(), Length(min=4, max=50)])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6, max=50)])
    submit = SubmitField('Registrarse')
