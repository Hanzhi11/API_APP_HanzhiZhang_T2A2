from init import db

# Define a tokenblocklist table in the database with three columns (i.e. id, jti and created_at) which is used to store the revoked tokens. Each colum has its own constraints.
# In this table, id is the primary key.
class TokenBlocklist(db.Model):
    __tablename__ = 'blocked_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False)