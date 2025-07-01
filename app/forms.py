from flask_wtf import FlaskForm
from wtforms import TextAreaField, IntegerField, SubmitField, SelectField
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, NumberRange


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class ReviewForm(FlaskForm):
    rating = SelectField(
        'Rating',
        choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')],
        validators=[DataRequired()]
    )
    comment = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField('Submit Review')

class CheckoutForm(FlaskForm):
    shipping_address = TextAreaField('Shipping Address', validators=[DataRequired(), Length(min=10, max=500)])
    # Add a SelectField for payment method
    payment_method = SelectField(
        'Payment Method',
        choices=[
            ('cash_on_delivery', 'Cash on Delivery'),
            ('easypaisa_transfer', 'EasyPaisa Transfer')
        ],
        validators=[DataRequired()]
    )
    submit = SubmitField('Place Order')