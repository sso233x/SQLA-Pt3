from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def connect_db(app):
    db.app = app
    db.init_app(app)

#Create User model
class User(db.Model):
    """User."""
    
    __tablename__ = "users"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    first_name = db.Column(db.String(30),
                           nullable=False,)
    last_name = db.Column(db.String(30),
                          nullable=False,)
    image_url = db.Column(db.String(200),
                          nullable=True)

    def __repr__(self):
        return f"<User {self.first_name} {self.last_name}>"

class Post(db.Model):

    __tablename__ = "posts"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    title = db.Column(db.String(100),
                      nullable=False,)
    content = db.Column(db.String(1000),
                        nullable=False,)
    created_at = db.Column(db.DateTime,
                           nullable=False,
                           server_default=db.text('CURRENT_TIMESTAMP'))
    user_id = db.Column(db.Integer, 
                        db.ForeignKey('users.id'))

    user = db.relationship('User', backref='posts')
    tags = db.relationship('Tag', secondary='post_tags', back_populates='posts', cascade='all, delete')

    def __repr__(self):
        return f"<Post {self.title}>"

class Tag(db.Model):

    __tablename__ = "tags"

    id = db.Column(db.Integer, 
                   primary_key=True,
                   autoincrement=True)
    name = db.Column(db.String(100),
                     nullable=False,
                     unique=True)

    posts = db.relationship('Post', secondary='post_tags', back_populates='tags')

    def __repr__(self):
        return f"<Tag {self.name}>"

class PostTag(db.Model):

    __tablename__ = "post_tags"

    post_id = db.Column(db.Integer,
                        db.ForeignKey('posts.id'),
                        primary_key=True,
                        nullable=True)
    tag_id = db.Column(db.Integer,
                        db.ForeignKey('tags.id'),
                        primary_key=True,
                        nullable=True)

    post = db.relationship('Post', backref='post_tags')
    tag = db.relationship('Tag', backref='post_tags')

        