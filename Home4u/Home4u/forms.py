from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, SelectField, FloatField
from wtforms.validators import  InputRequired, Length, Email, EqualTo, ValidationError, NumberRange
from Home4u.models import User, House, HouseSelector, SearchInfo , Review, stayed, Communication, Request
from wtforms.fields.html5 import DateField


class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[InputRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[InputRequired(), Email()])
    password = PasswordField('Κωδικός', validators=[InputRequired()])
    confirm_password = PasswordField('Επαλήθευση Κωδικού',
                                     validators=[InputRequired(), EqualTo('password')])
    phone = IntegerField('Τηλέφωνο',
                          validators=[NumberRange(min=1000000000, max=9999999999, message='Το τηλέφωνο πρέπει να είναι ακριβώς 10 ψηφία')])
    birth_date = DateField('Ημερομηνία Γέννησης')
    firstname = StringField('Όνομα')
    surname = StringField('Επίθετο')
    sex =  SelectField(u'Φύλο', choices=[("Άνδρας", 'Άνδρας'), ("Γυναίκα", 'Γυναίκα'), ("Άλλο", 'Άλλο')])
    terms = BooleanField('Έχω διαβάσει και αποδέχομαι τους όρους χρήσης')
    submit = SubmitField('Εγγραφή')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Το username υπάρχει ήδη')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Το email αυτό δεν είναι διαθέσιμο')

    def validate_phone(self, phone):
        user = User.query.filter_by(phone=phone.data).first()
        if user:
            raise ValidationError('Το τηλέφωνο υπάρχει ήδη')

class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[InputRequired(), Email()])
    password = PasswordField('Κωδικός', validators=[InputRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Σύνδεση')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[InputRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[InputRequired(), Email()])
    picture = FileField('Ενημέρωση Εικόνας Προφίλ', validators=[FileAllowed(['jpg', 'png'])])
    phone = IntegerField('Τηλέφωνο',
                          validators=[NumberRange(min=1000000000, max=9999999999, message='Το τηλέφωνο πρέπει να είναι ακριβώς 10 ψηφία')])
    birth_date = DateField('Ημερομηνία Γέννησης')
    firstname = StringField('Όνομα')
    surname = StringField('Επίθετο')
    balance = FloatField('Ταμείο')
    sex =  SelectField(u'Φύλο', choices=[("Άνδρας", 'Άνδρας'), ("Γυναίκα", 'Γυναίκα'), ("Άλλο", 'Άλλο')])
    submit = SubmitField('Ενημέρωση')


    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Το username υπάρχει ήδη.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Το email αυτό δεν είναι διαθέσιμο.')

    def validate_phone(self, phone):
        if phone.data != current_user.phone:
            user = User.query.filter_by(phone=phone.data).first()
            if user:
                raise ValidationError('Το τηλέφωνο υπάρχει ήδη.')

class ReviewForm(FlaskForm):
    reviewer = IntegerField('Reviewer')
    recipient = IntegerField('Id')
    stars = SelectField(u'Βαθμολογία ', choices=[("1", '1'), ("2", '2'), ("3", '3'),("4", '4'), ("5", '5')])
    comments = StringField('Σχόλια')
    submit = SubmitField('Προσθήκη Αξιολόγησης')
    submit2 = SubmitField('Επιλογή Καταλύματος')
    submit3 = SubmitField('Επιλογή Χρήστη')



class AddHouseForm(FlaskForm):
    house_name = StringField('Όνομα Σπιτιού', validators=[InputRequired(), Length(min=2, max=50)])
    city = StringField('Πόλη', validators=[InputRequired(), Length(min=2, max=20)])
    postal_code = IntegerField('Ταχυδρομικός Κώδικας',
                                validators=[InputRequired(), NumberRange(min=5, max=5, message='Ο ΤΚ πρέπει να είναι 5 ψήφιο νούμερο')])
    address = StringField('Διεύθυνση', validators=[InputRequired(), Length(min=1, max=50)])
    square_meters = IntegerField('Τετραγωνικά Μέτρα', validators=[InputRequired()])
    price = IntegerField('Τιμή', validators=[InputRequired()])
    house_type = StringField('Είδος Καταλύματος', validators=[InputRequired()])
    visitors = IntegerField('Επισκέπτες', validators=[InputRequired()])
    available_from = DateField('Διαθέσιμο Από', validators=[InputRequired()])
    availability = BooleanField('Διαθέσιμο')
    submit = SubmitField('Αποθήκευση')



class UpdateHouseForm(FlaskForm):
    house_name = StringField('Όνομα Σπιτιού', validators=[InputRequired(), Length(min=2, max=50)])
    city = StringField('Πόλη', validators=[InputRequired(), Length(min=2, max=20)])
    postal_code = IntegerField('Ταχυδρομικός Κώδικας',
                                validators=[InputRequired(), NumberRange(min=10000, max=99999, message='Ο ΤΚ πρέπει να είναι 5 ψήφιο νούμερο')])
    address = StringField('Διεύθυνση', validators=[InputRequired(), Length(min=1, max=50)])
    square_meters = IntegerField('Τετραγωνικά Μέτρα', validators=[InputRequired()])
    price = IntegerField('Τιμή', validators=[InputRequired()])
    house_type = StringField('Είδος Καταλύματος', validators=[InputRequired()])
    visitors = IntegerField('Επισκέπτες', validators=[InputRequired()])
    available_from = DateField('Διαθέσιμο Από',
                           format='%Y-%m-%d')
    availability = BooleanField('Διαθέσιμο')
    picture = FileField('Ενημέρωση Εικόνας Προφίλ', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Αποθήκευση')
    submit2 = SubmitField('Προχωρήστε στην πλρηρωμή')



class SearchForm(FlaskForm):
    location = StringField('Περιοχή')
    arrival_date = DateField('Ημερομηνία Άφιξης', format='%Y-%m-%d')
    guests = IntegerField('Αριθμός Επισκεπτών')
    submit = SubmitField('Αναζήτηση')
    house_id = IntegerField('Id Σπιτιού')
    submit2 = SubmitField('Κάντε Κράτηση')

class ResultsForm(FlaskForm):
    submit = SubmitField('Κάντε Κράτηση')


class Communication2Form(FlaskForm):

    receiver = StringField('Παραλήπτης')
    message =  StringField('Γραπτο μηνύμα')
    submit = SubmitField('Αποστολή')

class CommunicationForm(Communication2Form):
    select_type = SelectField(u'Επιλογη μήνυματος', choices=[("Δεν εχω ρεύμα", 'Δεν εχω ρεύμα'), ("Δεν εχω νερό", 'Δεν εχω νερό'), ("Δεν εχω internet", 'Δεν εχω internet'),("Δεν εχω ζεστό νερό", 'Δεν εχω ζεστό νερό'), ("Δεν έχω θέρμανση", 'Δεν έχω θέρμανση')])

class PaymentMethodForm(FlaskForm):
    payment_type = SelectField(u'Πληρώστε με:', choices=[('cash', 'Μετρητά'), ('credit_card', 'Πιστωτική'), ('balance', 'Ταμείο')])
    submit = SubmitField('Επιλογή')
    submit2 = SubmitField('Επιβεβαίωση Πληρωμής')

class PaymentCreditForm(FlaskForm):
    card_name = StringField('Όνομα στη κάρτα')
    card_number = IntegerField('Αριθμός της κάρτας')
    cvv = IntegerField('CVV')
    # expire_date_month = IntegerField('Ημερομηνία Λήξεως Μήνα')
    # expire_date_year = IntegerField('Ημερομηνία Λήξεως')
    submit = SubmitField('Επιβεβαίωση Πληρωμής')

class SubmitForm(FlaskForm):
    submit = SubmitField('Επιβεβαίωση Πληρωμής')


class RequestForm(FlaskForm):
    req_id = IntegerField('Id Αιτήματος')
    submit = SubmitField('Επιβεβαίωση Αιτήματος')
    submit2 = SubmitField('Απόρριψη Αιτήματος')
    submit3 = SubmitField('Επιλογή')

class HouseInfoForm(FlaskForm):
    house_name = StringField('Όνομα Σπιτιού')
    city = StringField('Πόλη')
    postal_code = IntegerField('Ταχυδρομικός Κώδικας')
    address = StringField('Διεύθυνση')
    square_meters = IntegerField('Τετραγωνικά Μέτρα')
    price = IntegerField('Τιμή')
    house_type = StringField('Είδος Καταλύματος')
    visitors = IntegerField('Επισκέπτες')

    picture = FileField('Ενημέρωση Εικόνας Προφίλ')
    submit = SubmitField('Προχωρήστε στην πληρωμή')
    submit2 = SubmitField('Αναφορά Καταχώρησης')
    submit3 = SubmitField('Eπιστροφή στην σελίδα επιβεβαίωσης αναφοράς')

class ReportForm(FlaskForm):
    comments = StringField('Σχόλια', validators=[InputRequired(), Length(min=2, max=50)])
    submit = SubmitField('Ναι')
    submit2 = SubmitField('Όχι')

class AdminForm(FlaskForm):
    submit = SubmitField('Επιβεβαίωση')


class ButtonForm(FlaskForm):
    submit = SubmitField('Αποδοχή')
    submit2 = SubmitField('Απόρριψη')

class ProfileForm(FlaskForm):
    username = StringField('Username')
    email = StringField('Email')
    picture = FileField('Ενημέρωση Εικόνας Προφίλ')
    phone = IntegerField('Τηλέφωνο')
    birth_date = DateField('Ημερομηνία Γέννησης')
    firstname = StringField('Όνομα')
    surname = StringField('Επίθετο')
    balance = FloatField('Ταμείο')
    sex = StringField('Φύλο')
    submit = SubmitField('Επεξεργασία Προφίλ')
