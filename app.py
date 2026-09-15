from flask import Flask , render_template,request,redirect,url_for,session
from database import get_db_connection
from werkzeug.security import generate_password_hash,check_password_hash
from auth import login_required,role_required,roles_required

app =Flask(__name__)
app.secret_key="Inteligenz Solutions"

def log_activity(user_id, action, details):

    connection = get_db_connection()
    cursor = connection.cursor()

  
    query =""" insert into activity_logs(user_id,action,details) values(%s,%s,%s)"""

    values = (
        user_id,
        action,
        details
    )

    cursor.execute(query, values)

    connection.commit()

    cursor.close()
    connection.close()



@app.route("/",methods=["GET","POST"])
def login():
    if request.method=="POST":
        username=request.form["username"]
        password=request.form["password"]

        connection =get_db_connection()
        cursor =connection.cursor(dictionary=True)

        query="""
            select* from users where username =%s
        """
        cursor.execute(query,(username,))
        user=cursor.fetchone()
        cursor.close()
        connection.close()

        if user and check_password_hash(user["password"],password):
            session["user_id"]=user["id"]
            session["username"]=user["username"]
            session["role"]=user["role"]

            return redirect(url_for("dashboard"))
        return "Invalid username or password"
    
    return render_template("login.html")

@app.route("/dashboard")
@login_required
def dashboard():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    total_query = """
        SELECT COUNT(*) AS total
        FROM incidents
    """

    cursor.execute(total_query)
    total = cursor.fetchone()["total"]

    status_query = """
        SELECT status, COUNT(*) AS count
        FROM incidents
        GROUP BY status
    """

    cursor.execute(status_query)
    status_rows = cursor.fetchall()

    severity_query = """
        SELECT severity, COUNT(*) AS count
        FROM incidents
        GROUP BY severity
    """

    cursor.execute(severity_query)
    severity_rows = cursor.fetchall()

    cursor.close()
    connection.close()

    status_counts = {
        "Open": 0,
        "Investigating": 0,
        "Resolved": 0,
        "Closed": 0
    }

    for row in status_rows:
        status_counts[row["status"]] = row["count"]

    severity_counts = {
        "Low": 0,
        "Medium": 0,
        "High": 0,
        "Critical": 0
    }

    for row in severity_rows:
        severity_counts[row["severity"]] = row["count"]

    return render_template(
        "dashboard.html",
        username=session["username"],
        role=session["role"],
        total=total,
        status_counts=status_counts,
        severity_counts=severity_counts
    )


@app.route("/register",methods=["GET","POST"])
def register():
    if request.method=="POST":
        full_name = request.form["full_name"].strip()
        username = request.form["username"].strip()
        email = request.form["email"].strip()
        password = request.form["password"]

        # Public registration can only create Viewer accounts.
        # Admin can later change the role from Manage Users.
        role = "viewer"

        if not username or not password:
            return "Username and password are required", 400

        hashed_password = generate_password_hash(password)
        connection =get_db_connection()
        cursor = connection.cursor()

        query ="""
            insert into users(username,password,role,full_name,email)
            values(%s,%s,%s,%s,%s)
        """
        values =(
            username,hashed_password,role,full_name,email
        )

        cursor.execute(query,values)
        connection.commit()

        cursor.close()
        connection.close()

        return "Registration successful !"


       

    return render_template("register.html")



@app.route("/admin")
@role_required("admin")
def admin():
    return render_template(
        "admin.html",
        username=session["username"],
        role=session["role"]
    )


@app.route("/create-incident", methods=["GET", "POST"])
@roles_required("admin", "analyst")
def create_incident():

    if request.method == "POST":

        title = request.form["title"].strip()
        description = request.form["description"].strip()
        severity = request.form["severity"]
        source_ip = request.form["source_ip"].strip()

        if not title:
            return "Title cannot be empty", 400

        allowed_severities = [
            "Low",
            "Medium",
            "High",
            "Critical"
        ]

        if severity not in allowed_severities:
            return "Invalid severity", 400

        connection = get_db_connection()

        cursor = connection.cursor()

        query = """insert into incidents
            (title, description, severity, status, source_ip, created_by)
            values (%s, %s, %s, %s, %s, %s) """

        values = (
            title,
            description,
            severity,
            "Open",
            source_ip,
            session["user_id"]
        )

        cursor.execute(query, values)

        connection.commit()

        log_activity(session["user_id"],"Incident Created",f"Incident '{title}' was created")

        cursor.close()
        connection.close()

        return redirect(url_for("incidents"))

    return render_template("create_incident.html")


@app.route("/incidents")
@login_required
def incidents():

    search = request.args.get("search", "").strip()
    severity = request.args.get("severity", "").strip()
    status = request.args.get("status", "").strip()

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT
            incidents.*,
            users.username AS assigned_username,
            users.full_name AS assigned_name
        FROM incidents
        LEFT JOIN users
            ON incidents.assigned_to = users.id
        WHERE 1=1
    """

    values = []

    if search:
        query += """
            AND (
                incidents.title LIKE %s
                OR incidents.description LIKE %s
                OR incidents.source_ip LIKE %s
            )
        """

        search_value = "%" + search + "%"

        values.extend([
            search_value,
            search_value,
            search_value
        ])

    if severity:
        query += """
            AND incidents.severity = %s
        """

        values.append(severity)

    if status:
        query += """
            AND incidents.status = %s
        """

        values.append(status)

    query += """
        ORDER BY incidents.created_at DESC
    """

    cursor.execute(query, tuple(values))

    incidents = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
    "incidents.html",
    incidents=incidents,
    search=search,
    severity=severity,
    status=status,
    role=session["role"]
)

@app.route("/incident/<int:id>")
@login_required
def incident_details(id):

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

   
    query = """
        SELECT
            incidents.*,
            users.username AS assigned_username,
            users.full_name AS assigned_name
        FROM incidents
        LEFT JOIN users
            ON incidents.assigned_to = users.id
        WHERE incidents.id = %s
    """

    cursor.execute(query, (id,))

    incident = cursor.fetchone()

    if not incident:
        cursor.close()
        connection.close()
        return "Incident not found", 404

  
    analyst_query = """
        SELECT id, username, full_name
        FROM users
        WHERE role = %s
        ORDER BY full_name
    """

    cursor.execute(
        analyst_query,
        ("analyst",)
    )

    analysts = cursor.fetchall()

    
    notes_query = """
        SELECT
            incident_notes.id,
            incident_notes.note,
            incident_notes.created_at,
            users.username,
            users.full_name
        FROM incident_notes
        JOIN users
            ON incident_notes.user_id = users.id
        WHERE incident_notes.incident_id = %s
        ORDER BY incident_notes.created_at DESC
    """

    cursor.execute(
        notes_query,
        (id,)
    )

    notes = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "incident_details.html",
        incident=incident,
        analysts=analysts,
        notes=notes,
        role=session["role"]
    )


@app.route("/incident/<int:id>/edit", methods=["GET", "POST"])
@roles_required("admin","analyst")
def edit_incident(id):

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    if request.method == "POST":

        title = request.form["title"].strip()
        description = request.form["description"].strip()
        severity = request.form["severity"]
        source_ip = request.form["source_ip"].strip()

        if not title:
            return "Title cannot be empty", 400

        allowed_severities = [
            "Low",
            "Medium",
            "High",
            "Critical"
        ]

        if severity not in allowed_severities:
            return "Invalid severity", 400

        query = """
            UPDATE incidents
            SET title = %s,
                description = %s,
                severity = %s,
                source_ip = %s
            WHERE id = %s
        """

        values = (
            title,
            description,
            severity,
            source_ip,
            id
        )

        cursor.execute(query, values)

        connection.commit()

        log_activity(
    session["user_id"],
    "Incident Updated",
    f"Incident {id} information was updated"
)

        cursor.close()
        connection.close()

        return redirect(
            url_for("incident_details", id=id)
        )

    query = """
        select *
        from incidents
        where id = %s """

    cursor.execute(query, (id,))

    incident = cursor.fetchone()

    cursor.close()
    connection.close()

    if not incident:
        return "Incident not found", 404

    return render_template(
        "edit_incident.html",
        incident=incident
    )







@app.route("/incident/<int:id>/status", methods=["POST"])
@roles_required("admin", "analyst")
def update_incident_status(id):

    status = request.form["status"]

    allowed_statuses = [
        "Open",
        "Investigating",
        "Resolved",
        "Closed"
    ]

    if status not in allowed_statuses:
        return "Invalid status", 400

    connection = get_db_connection()
    cursor = connection.cursor()

    query = """
        UPDATE incidents
        SET status = %s
        WHERE id = %s
    """

    values = (
        status,
        id
    )

    cursor.execute(query, values)

    connection.commit()

    log_activity(
    session["user_id"],
    "Status Updated",
    f"Incident {id} status changed to {status}"
)

    cursor.close()
    connection.close()

    return redirect(
        url_for("incident_details", id=id)
    )



@app.route("/incident/<int:id>/assign",methods=["POST"])
@roles_required("admin","analyst")
def assign_incident(id):

    assigned_to =request.form["assigned_to"]
    connection =get_db_connection()
    cursor =connection.cursor()

    analyst_query =""" select id from users where id =%s and role =%s"""
    cursor.execute(analyst_query,(assigned_to,"analyst"))
    analyst =cursor.fetchone()

    if not analyst:
        cursor.close()
        connection.close()
        return "Invalid analyst",400

    update_query =""" update incidents set assigned_to =%s where id =%s"""
    cursor.execute( update_query,(assigned_to,id))
    connection.commit()

    log_activity(
    session["user_id"],
    "Analyst Assigned",
    f"Incident {id} assigned to analyst ID {assigned_to}"
)

    cursor.close()
    connection.close()
    return redirect( url_for("incident_details", id=id))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/incident/<int:id>/notes", methods=["POST"])
@roles_required("admin", "analyst")
def add_incident_note(id):

    note = request.form["note"].strip()

    if not note:
        return "Note cannot be empty", 400

    connection = get_db_connection()
    cursor = connection.cursor()

   
    incident_query = """
        SELECT id
        FROM incidents
        WHERE id = %s
    """

    cursor.execute(
        incident_query,
        (id,)
    )

    incident = cursor.fetchone()

    if not incident:
        cursor.close()
        connection.close()
        return "Incident not found", 404

   
    query = """
        INSERT INTO incident_notes
        (incident_id, user_id, note)
        VALUES (%s, %s, %s)
    """

    values = (
        id,
        session["user_id"],
        note
    )

    cursor.execute(query, values)
    connection.commit()

    log_activity(
    session["user_id"],
    "Note Added",
    f"Investigation note added to incident {id}"
)

    cursor.close()
    connection.close()

    return redirect(
        url_for("incident_details", id=id)
    )


@app.route("/activity-logs")
@role_required("admin")
def activity_logs():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT
            activity_logs.id,
            activity_logs.action,
            activity_logs.details,
            activity_logs.created_at,
            users.username,
            users.full_name,
            users.role
        FROM activity_logs
        LEFT JOIN users
            ON activity_logs.user_id = users.id
        ORDER BY activity_logs.created_at DESC
    """

    cursor.execute(query)

    logs = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "activity_logs.html",
        logs=logs
    )

@app.route("/admin/users")
@role_required("admin")
def manage_users():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT
            id,
            username,
            full_name,
            email,
            role
        FROM users
        ORDER BY id
    """

    cursor.execute(query)

    users = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "manage_users.html",
        users=users
    )


@app.route("/admin/users/<int:id>/role", methods=["POST"])
@role_required("admin")
def change_user_role(id):

    role = request.form["role"]

    allowed_roles = [
        "admin",
        "analyst",
        "viewer"
    ]

    if role not in allowed_roles:
        return "Invalid role", 400

    
   
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    user_query = """
        SELECT username
        FROM users
        WHERE id = %s
    """

    cursor.execute(
        user_query,
        (id,)
    )

    user = cursor.fetchone()

    if not user:
        cursor.close()
        connection.close()
        return "User not found", 404
    
    if id == session["user_id"]:
       cursor.close()
       connection.close()
       return "You cannot change your own role", 400

    update_query = """
        UPDATE users
        SET role = %s
        WHERE id = %s
    """

    cursor.execute(
        update_query,
        (role, id)
    )

    connection.commit()

    

    cursor.close()
    connection.close()

    log_activity(
        session["user_id"],
        "User Role Updated",
        f"User '{user['username']}' role changed to {role}"
    )

    return redirect(
        url_for("manage_users")
    )




if __name__=="__main__":
    app.run(debug=True)