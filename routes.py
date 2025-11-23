from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import UnmappedInstanceError
from sqlalchemy import desc

from models import User, Task


def register_routes(app, db, bcrypt):

    @app.route('/')
    def homePage():
        return render_template("homePage.html")
    
    @app.route("/displayTasks/<username>", methods = ["GET"])
    @login_required
    def displayTasks(username):
        if request.method == "GET":
            user = User.query.filter_by(username=username).first()
            print(user)
            if not user:
                return "User not found", 404

            # LIST OF CLASSES TASKS
            tasks = Task.query.filter_by(userId=user.uid).order_by(desc(Task.priority)).all()
            remainingTasks = [task for task in tasks if task.status == 0]
            workingOnTasks = [task for task in tasks if task.status == 1]
            completedTasks = [task for task in tasks if task.status == 2]
            return render_template("displayTasks.html", user=user, remainingTasks=remainingTasks, workingOnTasks=workingOnTasks, completedTasks=completedTasks)
        
    @app.route("/deleteTask/<int:tid>", methods=["POST", "GET"])
    def deleteTask(tid):
        if request.method == "POST":
            task = Task.query.filter_by(tid=tid).first()
            db.session.delete(task)
            db.session.commit()

            flash(f"{task.task} DELETED FROM TASKS")
            return redirect(url_for("displayTasks", username=current_user.username))
        else:
            return redirect(url_for("displayTasks", username=current_user.username))

    @app.route("/markWorkingOn/<int:tid>", methods=["POST", "GET"])
    def markWorkingOn(tid):
        if request.method == "POST":
            task = Task.query.filter_by(tid=tid).first()
            task.status = 1

            db.session.commit()

            flash(f"WORKING ON {task.task}")
            return redirect(url_for("displayTasks", username=current_user.username))
        elif request.method == "GET":
            return redirect(url_for("displayTasks", username=current_user.username))


    @app.route("/markIncomplete/<int:tid>", methods=["POST", "GET"])
    def markIncomplete(tid):
        if request.method == "POST":
            task = Task.query.filter_by(tid=tid).first()
            task.status = 0

            db.session.commit()

            flash(f"{task.task} MARKED INCOMPLETE")
            return redirect(url_for("displayTasks", username=current_user.username))
        elif request.method == "GET":
            return redirect(url_for("displayTasks", username=current_user.username))

    @app.route("/clearCompletedTasks/<username>", methods=["POST", "GET"])
    def clearCompletedTasks(username):
        if request.method == "POST":
            user = User.query.filter_by(username).first()
            uid = user.uid

            task = Task.query.filter_by(status=2, userId=uid).delete()
            db.session.commit()

            flash(f"DELETED ALL COMPLETED TASKS FOR {current_user.username}")
            return redirect(url_for("displayTasks", username=current_user.username))
        elif request.method == "GET":
            return redirect(url_for("displayTasks", username=current_user.username))
        
    @app.route("/clearWorkingOnTasks/<username>", methods=["POST", "GET"])
    def clearWorkingOnTasks(username):
        if request.method == "POST":
            user = User.query.filter_by(username).first()
            uid = user.uid

            task = Task.query.filter_by(status=1, userId = uid).delete()
            db.session.commit()

            flash(f"DELETED ALL WORKING ON TASKS FOR {username}")
            return redirect(url_for("displayTasks", username=current_user.username))
        elif request.method == "GET":
            return redirect(url_for("displayTasks", username=current_user.username))

    @app.route("/clearAllTasks/<username>", methods=["POST", "GET"])
    def clearAllTasks(username):
        if request.method == "POST":
            user = User.query.filter(User.username == username).first()
            uid = user.uid

            Task.query.filter(Task.userId == uid).delete()
            db.session.commit()

            flash(f"DELETED ALL TASKS FOR {username}")
            return redirect(url_for("displayTasks", username=current_user.username))
        elif request.method == "GET":
            return redirect(url_for("displayTasks", username=current_user.username))
    
    @app.route("/markComplete/<int:tid>", methods=["POST", "GET"])
    def markComplete(tid):
        if request.method == "POST":
            task = Task.query.filter_by(tid=tid).first()

            task.status = 2

            db.session.commit()
            flash(f"{task.task} COMPLETED")
            return redirect(url_for("displayTasks", username=current_user.username))
        elif request.method == "GET":
            return redirect(url_for("displayTasks", username=current_user.username))
        
    @app.route("/editTask/<int:tid>", methods=["POST", "GET"])
    def editTask(tid):
        oldTask = Task.query.get(tid)
        oldTaskName = oldTask.task
        oldPriority = oldTask.priority
        oldDescription = oldTask.description

        if request.method == "POST":
            newTaskName = request.form.get('task').title()
            newPriority = request.form.get('priority') or 0
            newDescription = request.form.get('description')

            oldTask.task = newTaskName
            oldTask.priority = newPriority
            oldTask.description = newDescription

            db.session.commit()

            flash(f"{oldTaskName} UPDATED to {newTaskName}")
            return redirect(url_for("displayTasks", username=current_user.username))
        else:
            return render_template("edit.html", oldTask=oldTask)

    @app.route("/signup", methods=["POST", "GET"])
    def signup():
        if request.method == "GET":
            return render_template("signup.html")
        elif request.method == "POST":
            username = request.form.get('username')
            password = request.form.get('password')

            hashed_pwd = bcrypt.generate_password_hash(password)

            user = User(username=username, password=hashed_pwd)

            try:
                db.session.add(user)
                db.session.commit()
                if bcrypt.check_password_hash(user.password, password):
                    login_user(user)
                else:
                    flash("LOGIN FAILED AFTER SIGN UP")
            except IntegrityError:
                flash("USER HAS ALREADY SIGNED UP")
                return redirect(url_for("homePage"))

            return redirect(url_for("displayTasks", username=user.username))
    
    @app.route("/login", methods=["POST", "GET"])
    def login():
        if request.method == "GET":
            return render_template("login.html")
        elif request.method == "POST":
            try:
                username = request.form.get("username")
                password = request.form.get("password")

                user = User.query.filter(User.username == username).first()

                if bcrypt.check_password_hash(user.password, password):
                    login_user(user)  
                    return redirect(url_for("displayTasks", username=user.username))
                else:
                    flash("LOGIN FAILED - Incorrect Password")
                    return redirect(url_for("homePage"))
                
            except AttributeError:
                flash(f"{username} is not signed up")
                return redirect(url_for("homePage"))
            
    @app.route("/addTask/<username>", methods=["POST"])
    def addTask(username):
        if request.method == "POST":
            userId = current_user.uid
            task = request.form.get('task').title()
            status = request.form.get('status')
            priority = request.form.get('priority') or 0
            description = request.form.get('description')

            newTask = Task(userId=userId, task=task, status=status, priority=priority, description=description)

            db.session.add(newTask)
            db.session.commit()

        return redirect(url_for('displayTasks', username=username))    

    @app.route("/elaborateTask/<int:tid>", methods=["GET", "POST"])
    def elaborateTask(tid):
        oldTask = Task.query.get(tid)
        oldTaskName = oldTask.task
        oldPriority = oldTask.priority
        oldDescription = oldTask.description

        if request.method == "GET":
            task = Task.query.filter(Task.tid == tid).first()
            return render_template("elaborateTask.html", task=task)
        elif request.method == "POST":
            newTaskName = request.form.get('task').title()
            newPriority = request.form.get('priority') or 0
            newDescription = request.form.get('description')

            oldTask.task = newTaskName
            oldTask.priority = newPriority
            oldTask.description = newDescription

            db.session.commit()

            if oldTaskName != newTaskName:
                flash(f"{oldTaskName} updated to {newTaskName}")
            if oldPriority != newPriority:
                flash(f"Priority updated from {oldPriority} to {newPriority}")
            if oldDescription != newDescription:
                flash("Description is updated")
            return redirect(url_for("displayTasks", username=current_user.username))

    @app.route("/logout/")
    def logout():
        logout_user()
        return redirect(url_for("homePage"))
    
    @app.route("/deleteUser/<int:uid>", methods=["POST"])
    def deleteUser(uid):
        user = User.query.get(uid)
        if not user:
            flash("User not found")
            return redirect(url_for("secret"))

        tasks = Task.query.filter(Task.userId == uid).all()

        for task in tasks:
            db.session.delete(task)

        db.session.delete(user)
        
        db.session.commit()

        flash(f"{user.username} DELETED")
        return redirect(url_for("secret"))



    @app.route("/showUsers")
    @login_required
    def secret():
        if current_user.username == "Aryan":
            users = User.query.all()
            return render_template("secret.html", users=users)
        else:
            flash("CANNOT DISPLAY USERS FOR YOU")
            return redirect(url_for("homePage"))
    
    @app.route("/deleteEnteredUser", methods=["POST"])
    @login_required
    def deleteEnteredUser():
        if request.method == "POST":
            username = request.form.get('username')
            user = User.query.filter(User.username == username).first()

            try:
                db.session.delete(user)
                db.session.commit()

                flash(f"{user.username} DELETED")

            except UnmappedInstanceError:
                flash(f"{username} DOES NOT EXIST")

        return redirect(url_for("secret"))
