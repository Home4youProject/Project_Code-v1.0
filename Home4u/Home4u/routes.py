import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request
from Home4u import app, db, bcrypt
from Home4u.forms import RegistrationForm,AdminForm ,ProfileForm, ButtonForm, SubmitForm,HouseInfoForm,ReportForm, PaymentCreditForm, LoginForm, PaymentMethodForm, UpdateAccountForm, ReviewForm, AddHouseForm, UpdateHouseForm, SearchForm, ResultsForm, CommunicationForm, Communication2Form, RequestForm
from Home4u.models import User, House, HouseSelector, SearchInfo, Review, stayed, Communication, Request, Report
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime



@app.route("/")
@app.route("/home",methods=['GET', 'POST'])
def home():
    logo_image = url_for('static', filename='logo.png')
    return render_template('home.html', image_file=logo_image)

@app.route("/search", methods=['GET', 'POST'])
@login_required
def search():
    form = SearchForm()
    if form.validate_on_submit():
        search = SearchInfo(location=form.location.data, arrival_date=form.arrival_date.data, guests=form.guests.data)
        db.session.add(search)
        db.session.commit()
        searched = SearchInfo.query.order_by(SearchInfo.id.desc()).first()
        searched_houses = House.query.filter_by(city=searched.location).filter_by(availability=True).filter(House.user_id!=current_user.id).filter(House.visitors>=searched.guests).filter(House.available_from<=searched.arrival_date).all()
        if searched_houses == []:
            flash('Δεν βρέθηκαν κατάλληλα καταλύματα', 'danger')
            return redirect(url_for('search'))
        return redirect(url_for('search_results'))
    return render_template('search.html', title='Search', form=form)

@app.route("/search_results", methods=['GET', 'POST'])
@login_required
def search_results():

    searched = SearchInfo.query.order_by(SearchInfo.id.desc()).first()
    searched_houses = House.query.filter_by(city=searched.location).filter_by(availability=True).filter(House.user_id!=current_user.id).filter(House.visitors>=searched.guests).filter(House.available_from<=searched.arrival_date).all()
    return render_template('search_results.html', searched_houses=searched_houses, title='Search Results')

@app.route("/user_review_list", methods=['GET', 'POST'])
@login_required
def user_review_list():
    form = ReviewForm()
    req = Request.query.filter_by(req_sender=current_user.username).filter_by(req_type='accepted').all()
    homes = House.query.all()
    return render_template('user_review_list.html', homes=homes,req=req, title='Houses List', form=form)

@app.route("/user_review/<int:home_id>" , methods=['GET', 'POST'])
@login_required
def user_review(home_id):
    form = ReviewForm()
    house_review = House.query.get_or_404(home_id)
    if form.validate_on_submit():
        review = Review(reviewer=current_user.id, recipient=house_review.id, stars=form.stars.data, comments=form.comments.data , type='review_for_house')
        db.session.add(review)
        house_review.reviews += int(form.stars.data)
        house_review.review_num += 1
        db.session.commit()
        flash('Your review has been succesfully saved!', 'success')
        return redirect(url_for('user_review_list'))
    return render_template('user_review.html',house_review=house_review , title='Add a Review', form=form)

@app.route("/owner_review_list")
@login_required
def owner_review_list():
    form = ReviewForm()
    req = Request.query.filter_by(req_receiver=current_user.id).filter_by(req_type='accepted').all()
    users = User.query.all()
    #acc_req = Request.query.filter_by(req_sender=)
    #users = User.query.filter_by(id=current_user.id).all()
    # if form.validate_on_submit():
    #     return redirect(url_for('owner_review'))
    return render_template('owner_review_list.html',users=users,req=req, title='Users List', form=form)


@app.route("/owner_review/<int:user_id>", methods=['GET', 'POST'])
@login_required
def owner_review(user_id):
    form = ReviewForm()
    owner_review = User.query.get_or_404(user_id)

    if form.validate_on_submit():
        review = Review(reviewer=current_user.id, recipient=owner_review.id, stars=form.stars.data, comments=form.comments.data, type='review_for_user')
        db.session.add(review)
        owner_review.reviews += int(form.stars.data)
        owner_review.review_num += 1
        db.session.commit()
        flash('Your review has been succesfully saved!', 'success')
        return redirect(url_for('home'))
    return render_template('owner_review.html',owner_review=owner_review, title='Add a Review', form=form)

@app.route("/register_house", methods=['GET', 'POST'])
@login_required
def register_house():
    form = UpdateHouseForm()
    if form.validate_on_submit():
        house = House(house_name=form.house_name.data, city=form.city.data, postal_code=form.postal_code.data, address=form.address.data, square_meters=form.square_meters.data, price=form.price.data, house_type=form.house_type.data, visitors=form.visitors.data, user_id=current_user.id, available_from=form.available_from.data, availability=form.availability.data)
        db.session.add(house)
        current_user.identity="owner"
        db.session.commit()
        flash('Your house has been succesfully saved!', 'success')
        return redirect(url_for('login'))
    return render_template('register_house.html', title='Add House', form=form)

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, phone=form.phone.data, firstname=form.firstname.data, surname=form.surname.data, sex=form.sex.data, birth_date=form.birth_date.data)
        db.session.add(user)
        db.session.commit()
        flash('Το προφίλ σας δημιουργήθηκε. Για να ενημερώσετε το ταμείο σας κάνετε είσοδο και πηγαίνετε στο προφίλ σας', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

def save_picture2(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/house_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.phone = form.phone.data
        current_user.birth_date = form.birth_date.data
        current_user.firstname = form.firstname.data
        current_user.surname = form.surname.data
        current_user.balance = form.balance.data
        current_user.sex = form.sex.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.phone.data = current_user.phone
        form.birth_date.data = current_user.birth_date
        form.firstname.data = current_user.firstname
        form.surname.data = current_user.surname
        form.balance.data = current_user.balance
        form.sex.data = current_user.sex
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)

@app.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    if form.validate_on_submit():
        return redirect(url_for('account'))
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('profile.html', title='Profile',
                           image_file=image_file, form=form)

@app.route("/check_profile/<int:user_id>", methods=['GET', 'POST'])
@login_required
def check_profile(user_id):
    form = ProfileForm()
    user = User.query.filter_by(id=user_id).first()
    image_file = url_for('static', filename='profile_pics/' + user.image_file)
    return render_template('check_profile.html', title='User Profile',
                           image_file=image_file,user=user, form=form)

@app.route("/edit_house/<int:house_id>", methods=['GET', 'POST'])
@login_required
def edit_house(house_id):
    form = UpdateHouseForm()

    house = House.query.get_or_404(house_id)
    if form.validate_on_submit():

        if form.picture.data:
            picture_file = save_picture2(form.picture.data)
            house.image_file = picture_file
        house.house_name = form.house_name.data
        house.city = form.city.data
        house.postal_code = form.postal_code.data
        house.address = form.address.data
        house.square_meters = form.square_meters.data
        house.price = form.price.data
        house.house_type = form.house_type.data
        house.visitors = form.visitors.data
        house.available_from = form.available_from.data
        house.availability = form.availability.data
        db.session.commit()
        flash('Το κατάλυμα σας ενημερώθηκε επιτυχώς', 'success')
        return redirect(url_for('edit_house', house_id=house.id))
    elif request.method == 'GET':

        form.house_name.data = house.house_name
        form.city.data = house.city
        form.postal_code.data = house.postal_code
        form.address.data = house.address
        form.square_meters.data = house.square_meters
        form.price.data = house.price
        form.available_from.data = house.available_from
        form.availability.data = house.availability
        form.house_type.data = house.house_type
        form.visitors.data = house.visitors
    image_file = url_for('static', filename='house_pics/' + house.image_file)
    return render_template('edit_house.html', title='Edit House',
                           image_file=image_file, form=form, house=house)


@app.route("/house_list", methods=['GET', 'POST'])
@login_required
def house_list():
    houses = House.query.filter_by(user_id=current_user.id).all()
    return render_template('house_list.html', houses=houses , title='Houses')

@app.route("/payment_method/<int:house_id>", methods=['GET', 'POST'])
@login_required
def payment_method(house_id):
    form = PaymentMethodForm()
    searched_house = SearchInfo.query.get_or_404(house_id)
    if form.validate_on_submit():
        if form.payment_type.data == 'cash':
            return redirect(url_for('payment_cash', house_id=searched_house.id))
        elif form.payment_type.data == 'credit_card':
            return redirect(url_for('payment_creditcard', house_id=searched_house.id))
        else:
            return redirect(url_for('payment_balance', house_id=searched_house.id))

    return render_template("payment_method.html", title='Πληρωμή', form=form)

@app.route("/payment_cash/<int:house_id>", methods=['GET', 'POST'])
@login_required
def payment_cash(house_id):
    form = SubmitForm()
    house1 = House.query.get_or_404(house_id)

    if form.validate_on_submit():

        request = Request(req_sender=current_user.username, req_receiver=house1.user_id, req_house=house1.id)
        db.session.add(request)
        db.session.commit()

        flash('Ο ιδιοκτήτης έλαβε το αίτημά σας', 'success')
        return redirect(url_for('home'))

    return render_template('payment_cash.html', title='Μετρητά', house1=house1,  form=form)

@app.route("/payment_creditcard/<int:house_id>", methods=['GET', 'POST'])
@login_required
def payment_creditcard(house_id):
    form = PaymentCreditForm()
    house1 = House.query.get_or_404(house_id)

    if form.validate_on_submit():
        request = Request(req_sender=current_user.username, req_receiver=house1.user_id, req_house=house1.id)
        db.session.add(request)
        db.session.commit()
        print(request.id)
        flash('Ο ιδιοκτήτης έλαβε το αίτημά σας', 'success')
        return redirect(url_for('home'))

    return render_template('payment_creditcard.html', title='Πιστωτική Κάρτα', house1=house1,  form=form)

@app.route("/payment_balance/<int:house_id>", methods=['GET', 'POST'])
@login_required
def payment_balance(house_id):
    form = SubmitForm()
    house1 = House.query.get_or_404(house_id)
    if form.validate_on_submit():
        if current_user.balance>=house1.price:
            current_user.balance = current_user.balance-house1.price
            request = Request(req_sender=current_user.username, req_receiver=house1.user_id, req_house=house1.id)
            db.session.add(request)
            db.session.commit()
            print(request.id)
            flash('Ο ιδιοκτήτης έλαβε το αίτημά σας', 'success')
            return redirect(url_for('home'))
        else:
            flash('Το ταμείο σας δεν έχει αρκετό υπόλοιπο. Πηγένετε στο προφίλ σας για να το ενημερώσετε', 'danger')

    return render_template('payment_balance.html', title='Ταμείο', house1=house1,  form=form)



@app.route("/communication")
@login_required
def communication():
    return render_template('communication.html', title='Communication')

@app.route("/write_message", methods=['GET', 'POST'])
@login_required
def write_message():
    form = Communication2Form()
    users = User.query.filter_by(username=form.receiver.data).first()
    if form.validate_on_submit() :
        if users:
            if form.receiver.data==users.username:
                com2 = Communication(sender=current_user.id, message=form.message.data, receiver= form.receiver.data)
                db.session.add(com2)
                db.session.commit()
                flash('Το μήνυμα εστάλει στο χρήστη !', 'success')
                return redirect(url_for('home'))
        else:
            flash('Ο παραλήπτης δεν βρέθηκε', 'danger')
            return redirect(url_for('write_message'))
    return render_template('write_message.html', users=users ,title='write message', form=form)

@app.route("/auto_message", methods=['GET', 'POST'])
@login_required
def auto_message():
    form = CommunicationForm()
    users = User.query.filter_by(username=form.receiver.data).first()
    if form.validate_on_submit():

        if users:
            if form.receiver.data==users.username:
                com = Communication(sender=current_user.id , auto_type=form.select_type.data, receiver= form.receiver.data)
                db.session.add(com)
                db.session.commit()
                flash('Το μήνυμα εστάλει στο χρήστη !', 'success')
                return redirect(url_for('home'))
        else:
            flash('Ο παραλήπτης δεν βρέθηκε', 'danger')
            return redirect(url_for('auto_message'))
    return render_template('auto_message.html', users=users , title='auto_message', form=form)


@app.route("/request_list", methods=['GET', 'POST'])
@login_required
def request_list():
    form = RequestForm()
    requests = Request.query.filter_by(req_receiver=current_user.id).filter_by(req_type='pending').order_by(Request.id.desc()).all()
    houses = House.query.all()
    messages = Communication.query.filter_by(receiver=current_user.username).all()
    users = User.query.all()
    return render_template('request_list.html', requests=requests , houses=houses, messages=messages, users=users, title='Request List', form=form)


@app.route("/accept_request/<int:request_id>", methods=['GET', 'POST'])
@login_required
def accept_request(request_id):
    form = RequestForm()
    db.session.commit()
    house_to_rent = HouseSelector.query.order_by(HouseSelector.id.desc()).first()
    house1 = House.query.filter_by(id=house_to_rent.house_id).first()
    sel_request = Request.query.get_or_404(request_id)
    user = User.query.filter_by(username=sel_request.req_sender).first()
    if form.submit.data:
        if form.validate_on_submit():
            sel_request.req_type='accepted'
            house1.availability = False
            message = Communication(sender=current_user.id, receiver=user.username, message='Η κράτηση σας για το κατάλυμα ' +house1.house_name+ ' ολοκληρώθηκε')
            db.session.add(message)
            db.session.commit()
            flash('Το αίτημα έγινε αποδεχτό', 'success')
            return redirect(url_for('request_list'))
    else:
        if form.validate_on_submit():
            sel_request.req_type='rejected'
            user.balance += house1.price
            message = Communication(sender=current_user.id, receiver=user.username, message='Η κράτηση σας για το κατάλυμα ' +house1.house_name+ ' απορρίφθηκε')
            db.session.add(message)
            db.session.commit()
            flash('Το αίτημα απορρίφθηκε', 'danger')
            return redirect(url_for('request_list'))
    return render_template('accept_request.html' ,user=user, title='Request List', form=form)

@app.route("/house_info/<int:house_id>", methods=['GET', 'POST'])
@login_required
def house_info(house_id):
    form = HouseInfoForm()
    select = HouseSelector(house_id=house_id)
    db.session.add(select)
    db.session.commit()
    house = House.query.get_or_404(house_id)
    user = User.query.filter_by(id=house.user_id).first()
    if form.submit.data:
        if form.validate_on_submit():
            return redirect(url_for('payment_method', house_id=house_id))
    else:
        if form.validate_on_submit():
            return redirect(url_for('report', house_id=house_id))

    image_file = url_for('static', filename='house_pics/' + house.image_file)
    return render_template('house_info.html', title='House Info',
                           image_file=image_file, form=form,user=user, house=house)

@app.route("/house_info_admin/<int:house_id>", methods=['GET', 'POST'])
@login_required
def house_info_admin(house_id):
    form = HouseInfoForm()
    select = HouseSelector(house_id=house_id)
    db.session.add(select)
    db.session.commit()
    house = House.query.get_or_404(house_id)
    user = User.query.filter_by(id=house.user_id).first()
    if form.submit3.data:
        return redirect(url_for('confirm_report', report_id=current_user.report))
    image_file = url_for('static', filename='house_pics/' + house.image_file)
    return render_template('house_info_admin.html', title='House Info',
                           image_file=image_file, form=form,user=user , house=house)

@app.route("/report/<int:house_id>", methods=['GET', 'POST'])
@login_required
def report(house_id):
    form = ReportForm()
    report = House.query.get_or_404(house_id)
    if form.submit.data:
        if form.validate_on_submit():
            rep = Report(comments=form.comments.data, house_id=house_id)
            db.session.add(rep)
            db.session.commit()
            flash('Η αναφορά καταχωρήθηκε επιτυχώς', 'success')
            return redirect(url_for('house_info', house_id=house_id))
    else:
        if form.validate_on_submit():
            flash('Δεν έγινε αναφορά', 'danger')
            return redirect(url_for('house_info', house_id=house_id))
    return render_template('report.html', title='Report', report=report, form=form)



@app.route("/make_me_admin", methods=['GET', 'POST'])
@login_required
def make_me_admin():
    form = AdminForm()
    if form.validate_on_submit():
        current_user.admin=True
        db.session.commit()
        flash('Μόλις αποκτήσατε δικαιώματα διαχειριστή', 'success')
        return redirect(url_for('home'))
    return render_template('make_me_admin.html', title='Γίνε διαχειριστής', form=form)

@app.route("/report_list", methods=['GET', 'POST'])
@login_required
def report_list():
    report_list = Report.query.all()
    houses = House.query.all()

    return render_template('report_list.html',report_list=report_list, houses=houses , title='Report List')

@app.route("/confirm_report/<int:report_id>", methods=['GET', 'POST'])
@login_required
def confirm_report(report_id):
    form = ButtonForm()
    current_user.report=report_id
    db.session.commit()
    report = Report.query.get_or_404(report_id)
    delete_house = House.query.filter_by(id=report.house_id).first()
    user = User.query.filter_by(id=delete_house.user_id).first()
    if form.submit.data:
        if form.validate_on_submit():
            db.session.delete(report)
            db.session.delete(delete_house)
            message = Communication(sender=0, receiver=user.username, message='Το κατάλυμα ' +delete_house.house_name+ ' διαγράφηκε')
            db.session.add(message)
            db.session.commit()
            flash('Η δημοσίευση διαγράφτηκε επιτυχώς', 'success')
            return redirect(url_for('report_list'))
    else:
        if form.validate_on_submit():
            db.session.delete(report)
            db.session.commit()
            flash('Η δημοσίευση δεν παραβίαζε κάποιο κανόνα')
            return redirect(url_for('report_list'))

    return render_template('confirm_report.html',report=report,delete_house=delete_house,  title='confirm report', form=form)


@app.route("/faqs",methods=['GET', 'POST'])
def faqs():

    return render_template('faqs.html',  title='FAQS')


@app.route("/ratings/<int:user_id>",methods=['GET', 'POST'])
@login_required
def ratings(user_id):
    user = User.query.get_or_404(user_id)
    reviews = Review.query.filter_by(recipient=user.id).filter_by(type='review_for_user').all()
    users = User.query.all()


    return render_template('ratings.html',user=user, reviews=reviews,users=users,  title='Reviews')

@app.route("/house_ratings/<int:house_id>",methods=['GET', 'POST'])
@login_required
def house_ratings(house_id):
    house = House.query.get_or_404(house_id)
    reviews = Review.query.filter_by(recipient=house.id).filter_by(type='review_for_house').all()
    users = User.query.all()


    return render_template('house_ratings.html',house=house, reviews=reviews,users=users,  title='Reviews')

@app.route("/terms_and_conditions",methods=['GET', 'POST'])
def terms_and_conditions():
    return render_template('terms_and_conditions.html', title='Terms and Conditions')

@app.route("/all_users", methods=['GET'])
def all_users():
    users = User.query.all()
    count = User.query.count()
    return render_template('all_users.html', users=users, title='All Users', count=count)

@app.route("/all_houses", methods=['GET'])
def all_houses():
    houses = House.query.all()
    count = House.query.count()
    return render_template('all_houses.html', houses=houses, title='All houses', count=count)
