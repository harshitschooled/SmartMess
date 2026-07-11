from flask_wtf import FlaskForm
from wtforms import DateField, SelectField, TextAreaField, SubmitField, DecimalField
from wtforms.validators import DataRequired, Length, NumberRange, ValidationError

class MenuForm(FlaskForm):
    date = DateField('Menu Date', validators=[DataRequired(message="Please select a date.")])
    meal_type = SelectField('Meal Type', choices=[
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner')
    ], validators=[DataRequired()])
    items = TextAreaField('Menu Items', validators=[
        DataRequired(message="Please specify the food items."),
        Length(min=3, message="Menu items must be at least 3 characters long.")
    ])
    submit = SubmitField('Save Menu')


class FoodWasteForm(FlaskForm):
    date = DateField('Record Date', validators=[DataRequired(message="Please select a date.")])
    meal_type = SelectField('Meal Type', choices=[
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner')
    ], validators=[DataRequired()])
    food_prepared = DecimalField('Food Prepared (kg)', places=2, validators=[
        DataRequired(message="Please specify the food prepared."),
        NumberRange(min=0.0, message="Prepared food amount cannot be negative.")
    ])
    food_consumed = DecimalField('Food Consumed (kg)', places=2, validators=[
        DataRequired(message="Please specify the food consumed."),
        NumberRange(min=0.0, message="Consumed food amount cannot be negative.")
    ])
    submit = SubmitField('Save Waste Record')

    def validate_food_consumed(self, field):
        if self.food_prepared.data is not None and field.data is not None:
            if field.data > self.food_prepared.data:
                raise ValidationError("Consumed food cannot exceed prepared food.")

