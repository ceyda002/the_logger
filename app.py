
from flask import Flask, render_template, redirect, url_for, flash, request, Response
from flask_migrate import Migrate
from extensions import db, bcrypt, login_manager
from flask_login import login_user, login_required, logout_user,current_user
from models import User, Course, Sess, Note
from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime, timedelta
from collections import defaultdict
from config import Config
import os, csv, io , json




# print("Current working directory:", os.getcwd())
def create_app():
    app = Flask(__name__)


    app.config['SECRET_KEY'] = "log"
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db' #means create a file called site.db in the current folder
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static', 'uploads', 'notes')
    app.config['MAX_CONTENT_LENGTH']= 20 * 1024 
    app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'doc','docx','txt'}
    
    
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    #initalizing extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    Migrate(app,db)


    
  











    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))


    def update_course_total_hours(course_id):
        course = Course.query.get(course_id)
        if course:
            session_minutes = sum(s.hours * 60 + s.minutes for s in course.sess)
            course.total_hours= course.manual_hours + session_minutes
            db.session.commit()


    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/login', methods =['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username'].strip()
            password = request.form['password'].strip()
            user = User.query.filter_by(username=username).first()
            if user and bcrypt.check_password_hash(user.password, password):
                login_user(user)
                flash('Logged in!','success')
                return redirect(url_for('dashboard'))
            else:
                flash('Login failed. Check username and password.', 'danger')
        return render_template('login.html')

    @app.route('/register', methods = ['GET', 'POST'])
    def register():
        
        if request.method == 'POST':
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']


            existing_user = User.query.filter((User.username==username)|(User.email==email)).first()
            if existing_user:
                flash("username or email already exists.", "danger")
                return redirect(url_for('register'))

            hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
            new_user = User(username=username, email=email, password=hashed_pw)
            db.session.add(new_user)
            db.session.commit()

            flash("You have registered.", "success")
            return redirect(url_for('login'))
        return render_template('register.html')


    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('Logged out.', 'success')
        return redirect(url_for('login'))


    @app.route('/dashboard') #non -logged-in users 
    @login_required
    def dashboard():
        courses = Course.query.filter_by(user_id=current_user.id).all()
        sessions = Sess.query.join(Course).filter(Course.user_id == current_user.id).order_by(Sess.date.desc()).all()
        overall_minutes = sum(s.hours * 60 + s.minutes for course in courses for s in course.sess)
        overall_hours = overall_minutes // 60
        overall_remaining_minutes = overall_minutes % 60

        course_names = [course.coursename for course in courses]
        course_hours = [sum(s.hours  + s.minutes / 60 for s in course.sess) + course.manual_hours for course in courses]
        daily_hours = defaultdict(float)
        for sess in sessions:
            day = sess.date
            if isinstance(day, datetime):
                day = day.date()
            daily_hours[day] += sess.hours + sess.minutes / 60

        today = date.today()
        start_day = today - timedelta(days=29)
        streak_labels = []
        streak_values = []
        for i in range(60):
            day = start_day + timedelta(days=i)
            streak_labels.append(day.strftime('%Y-%m-%d'))
            streak_values.append(round(daily_hours.get(day, 0), 2))

        # Pass data to template
        return render_template('dashboard.html', courses=courses, sessions=sessions, overall_hours=overall_hours, overall_remaining_minutes=overall_remaining_minutes, course_names=course_names, course_hours=course_hours, streak_labels=streak_labels, streak_values=streak_values)



    # CRUD functionalit for courses
    @app.route('/courses/add', methods=['GET', 'POST'])
    @login_required
    def add_course():
        if request.method == 'POST':
            coursename = request.form['coursename'].strip()
            description = request.form['description'].strip()
            status = request.form.get('status', 'planned')
            total_hours = request.form.get("total_hours") or 0
            manual_hours = request.form.get("manual_hours") or 0
            tags_input = request.form.get("tags") or ""
            tags_cleaned = ",".join([t.strip() for t in tags_input.split(",") if t.strip()])
            new_course = Course(coursename=coursename, description=description, status=status, user_id=current_user.id, total_hours=total_hours, manual_hours=manual_hours, tags= tags_cleaned, )
            db.session.add(new_course)
            db.session.commit()
            flash('Course added.', 'success')
            return redirect(url_for('dashboard'))
        return render_template('add_courses.html')


    @app.route('/courses')
    @login_required
    def list_courses():
        query = request.args.get('q', '').lower()
        base_query = Course.query.filter_by(user_id=current_user.id)

        if query:
            base_query = base_query.filter(
                (Course.coursename.ilike(f"%{query}%")) |
                (Course.description.ilike(f"%{query}")) |
                (Course.tags.ilike(f"%{query}%"))
            )
        courses = base_query.all()
        return render_template("courses.html", courses=courses, query=query)

        


    @app.route('/courses/edit/<int:course_id>', methods=['GET','POST'])
    @login_required
    def edit_course(course_id):
        course = Course.query.get_or_404(course_id)
        if course.user_id != current_user.id:
            flash("You can't edit this course.", "danger")
            return redirect(url_for('list_courses'))

        if request.method == 'POST':
            course.coursename = request.form['coursename'].strip()
            course.description = request.form['description'].strip()
            course.status = request.form.get('status', 'planned')
            course.total_hours = int(request.form.get('total_hours', course.total_hours).strip() or 0)
            course.manual_hours = int(request.form['manual_hours'].strip() or 0)
            tags_input = request.form.get("tags") or ""
            course.tags = ",".join([t.strip() for t in tags_input.split(",") if t.strip()])
            db.session.commit()
            update_course_total_hours(course.id)
            flash('Course updated.', 'success')
            return redirect(url_for('list_courses'))
        return render_template('edit_course.html', course=course)

    @app.route('/courses/delete/<int:course_id>')
    @login_required
    def delete_course(course_id):
        course = Course.query.get_or_404(course_id)
        if course.user_id != current_user.id:
            flash("You can't delete this course.", "danger")
            return redirect(url_for('list_courses'))
        db.session.delete(course)
        db.session.commit()
        flash('Course deleted.', 'success')
        return redirect(url_for('list_courses'))

    @app.route('/courses/set_status/<int:course_id>/<status>')
    @login_required
    def set_status(course_id, status):
        if status not in ('planned', 'in_progress','completed'):
            flash('Invalid status.', 'danger')
            return redirect(url_for('dashboard'))
        course = Course.query.get_or_404(course_id)
        if course.user_id != current_user.id:
            flash("Forbidden","danger")
            return redirect(url_for('dashboard'))
        course.status = status
        db.session.commit()
        flash('Status updated.', 'success')
        return redirect(url_for('dashboard'))


    ##session routes
    @app.route('/sessions/add<int:course_id>', methods=['GET', 'POST'])
    @login_required
    def add_session(course_id):
        course = Course.query.get_or_404(course_id)
        if course.user_id != current_user.id:
            flash('Unauthorized', 'danger')
            return redirect(url_for('dashboard'))
        

        if request.method == 'POST':
            
            date_str = request.form['date']
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            

            if not course_id:
                flash('Please select a course.', 'danger')
                
                return redirect(url_for('add_session'))
            

            new_session = Sess( course_id=course_id, date=date_obj,hours = int(request.form['hours']), minutes=int(request.form['minutes']), notes=request.form['notes'].strip())
            db.session.add(new_session)
            db.session.commit()

            update_course_total_hours(course.id)
            flash("Session logged.", "success")
            return redirect(url_for('list_courses'))
        
        return render_template('add_session.html', course=course)

    @app.route('/session/edit/<int:session_id>', methods= ['GET', 'POST'])
    @login_required
    def edit_session(session_id):
        sess = Sess.query.get_or_404(session_id)

        if sess.course.user_id != current_user.id:
            flash('unauthorized', 'danger')
            return redirect(url_for('dashboard'))
        
        if request.method == 'POST':
            sess.course_id = request.form.get('course_id', sess.course_id)
            date_str = request.form.get('date', None)
            if date_str:
                sess.date = datetime.strptime(date_str, '%Y-%m-%d').date()
            sess.hours = int(request.form.get('hours', sess.hours))
            sess.minutes = int(request.form.get('minutes', sess.minutes ))
            sess.notes = request.form.get('notes', sess.notes)

            db.session.commit()
            update_course_total_hours(sess.course_id)
            flash('session updated.' , 'success')
            return redirect(url_for('list_sessions', course_id=sess.course_id))
        
        courses = Course.query.filter_by(user_id=current_user.id).all()
        return render_template('edit_session.html', sess= sess, courses=courses)

    @app.route('/sessions/delete/<int:session_id>', methods=['POST'])
    @login_required
    def delete_session(session_id):
        sess= Sess.query.get_or_404(session_id)
        #verify ownership
        if sess.course.user_id != current_user.id:
            flash('unauthorized', 'danger')
            return redirect(url_for('dashboard'))
        
        course_id = sess.course_id
        
        db.session.delete(sess)
        db.session.commit()
        update_course_total_hours(course_id)
        flash('Session deleted', 'success')
        return redirect(url_for('list_sessions', course_id=course_id))


    @app.route('/sessions/<int:course_id>')
    @login_required
    def list_sessions(course_id):
        course = Course.query.get_or_404(course_id)
        sessions = Sess.query.filter_by(course_id =course_id).order_by(Sess.date.desc()).all()
        return render_template('list_sessions.html', sessions=sessions, course=course, course_id=course_id)

    @app.route('/sessions/all')
    @login_required
    def all_sessions():
        sessions = Sess.query.join(Course).filter(Course.user_id == current_user.id).order_by(Sess.date.desc()).all()
        return render_template('all_sessions.html', sessions=sessions)

    @app.route('/stopwatch')
    @login_required
    def stopwatch():
        return render_template('stopwatch.html')

    @app.route('/export/csv')
    @login_required
    def export_csv():
        sessions = Sess.query.join(Course).filter(Course.user_id == current_user.id).order_by(Sess.date.desc()).all()

        #create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)

        # header
        writer.writerow(['Course Name', 'Date', 'Hours', 'Minutes', 'Notes'])

        #write data rows
        for sess in sessions:
            writer.writerow([sess.course.coursename, sess.date, sess.hours, sess.minutes, sess.notes])

            #prepare response
        output.seek(0)
        return Response(output, mimetype='text/csv', headers={"Content-Disposition":"attachment;filename=sessions.csv"}
        )

    @app.route('/export/json')
    @login_required
    def export_json():
        
        sessions = Sess.query.join(Course).filter(Course.user_id == current_user.id).all()

        data = []
        for sess in sessions:
            data.append({
                'course': sess.course.coursename,
                'date': str(sess.date),
                'hours': sess.hours,
                'minutes': sess.minutes,
                'notes': sess.notes
            })

            # return JSON response
            return Response(json.dumps(data, indent=4), mimetype="application/json", headers={"Content-Disposition":"attachment;filename=sessions.json"})



    with app.app_context():
        # print("Creating database..")
        db.create_all()
        # print("Database created at:", os.path.join(os.getcwd(), "site.db"))

    return app

if __name__ =="__main__":
    app = create_app()
    
    app.run(debug=True)
 
