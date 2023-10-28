AUTH_USER = "SELECT * FROM users WHERE login = %s AND password_hash	= SHA2(%s, 256);"
LOAD_USER = "SELECT * FROM users WHERE id = %s;"
LOAD_ROLES = "SELECT * FROM roles;"
ADD_USER = "INSERT INTO users (login, password_hash, last_name, first_name, middle_name, role_id) VALUES (%(login)s, SHA2(%(password)s, 256), %(last_name)s, %(first_name)s, %(middle_name)s, %(role_id)s);"
VIEW_USER = "SELECT * FROM users WHERE id = %s"
GET_USERS = "SELECT users.*, roles.name as role_name FROM users LEFT JOIN roles on users.role_id=roles.id;"
EDIT_USER = """
        UPDATE users SET login = %(login)s, last_name = %(last_name)s, 
        first_name = %(first_name)s, middle_name = %(middle_name)s,
        role_id = %(role_id)s WHERE id = %(id)s;
        """
DELETE_USER="DELETE FROM users WHERE id = %s"
UPDATE_PASSWORD="UPDATE users SET password_hash = SHA2(%s, 256) WHERE id = %s;"