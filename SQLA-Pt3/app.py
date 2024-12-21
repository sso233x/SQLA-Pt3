"""Blogly application."""
from flask import Flask, render_template, request, redirect, flash
from models import db, connect_db, User, Post, Tag, PostTag

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)
with app.app_context():
    db.create_all()

# USER ROUTES
@app.route('/')
def home_page():
    """Redirect to list of users"""
    return redirect('/users')

@app.route('/users') 
def show_users():
    users = User.query.all()
    return render_template("base.html", users=users)

@app.route('/users/new', methods=['GET', 'POST'])
def new_users():
    if request.method == "POST":
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        image_url = request.form.get("image_url")

        new_user = User(first_name=first_name, last_name=last_name, image_url=image_url)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/users')

    return render_template("form.html")

@app.route('/users/<int:user_id>')
def show_info(user_id):
    """Show info on a single user"""
    user = User.query.get_or_404(user_id)
    return render_template("detail.html", user=user)

@app.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
def user_edit(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == "POST":
        user.first_name = request.form["first_name"]
        user.last_name = request.form["last_name"]
        user.image_url = request.form.get("image_url")

        db.session.commit()
        return redirect('/users')

    return render_template("edit.html", user=user)

@app.route('/users/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect('/users')

# POST ROUTES
@app.route("/users/<int:user_id>/posts/new", methods=["GET", "POST"])
def add_post(user_id):
    """Show form to add a post or handle form submission."""
    user = User.query.get_or_404(user_id)
    tags = Tag.query.all()
    
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        selected_tags = request.form.getlist("tags")

        post = Post(title=title, content=content, user_id=user_id)
        db.session.add(post)
        db.session.commit()

        for tag_id in selected_tags:
            tag = Tag.query.get(tag_id)
            post.tags.append(tag)
        db.session.commit()
        return redirect(f"/users/{user_id}")
    
    return render_template("post-form.html", user=user, tags=tags)

@app.route("/posts/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    """Show details about a single post."""
    post = Post.query.get_or_404(post_id)
    user = User.query.get_or_404(post.user_id)

    if request.method == "POST":
        tag_id_to_remove = request.form.get("tag_id")
        tag_to_remove = Tag.query.get(tag_id_to_remove)
        if tag_to_remove in post.tags:
            post.tags.remove(tag_to_remove)
            db.session.commit()

        return redirect(f"/posts/{post_id}")
    return render_template("post-detail.html", post=post, user=user)

@app.route("/posts/<int:post_id>/edit", methods=["GET", "POST"])
def edit_post(post_id):
    """Show form to edit a post or handle form submission."""
    post = Post.query.get_or_404(post_id)
    tags = Tag.query.all()
    if request.method == "POST":
        post.title = request.form["title"]
        post.content = request.form["content"]
        selected_tags = request.form.getlist("tags")

        post.tags = []

        for tag_id in selected_tags:
            tag = Tag.query.get(tag_id)
            if tag:
                post.tags.append(tag)
        db.session.commit()

        return redirect(f"/posts/{post_id}")
    
    return render_template("post-edit.html", post=post, tags=tags)

@app.route("/posts/<int:post_id>/delete", methods=["POST"])
def delete_post(post_id):
    """Delete a post."""
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(f"/users/{post.user_id}")

# TAG ROUTES
@app.route("/tags")
def list_tags():
    """List all tags."""
    tags = Tag.query.all()
    return render_template('tags-list.html', tags=tags)

@app.route("/tags/<int:tag_id>")
def detail_tags(tag_id):
    """Show posts with specific tag"""
    tag = Tag.query.get_or_404(tag_id)
    return render_template('tag-detail.html', tag=tag)

@app.route("/tags/new", methods=["GET", "POST"])
def tag_form():
    if request.method == "POST":
        name = request.form["name"]

        new_tag = Tag(name=name)
        db.session.add(new_tag)
        db.session.commit()
        return redirect('/tags')

    return render_template("tag-form.html")

@app.route("/tags/<int:tag_id>/edit", methods=["GET", "POST"])
def edit_tag(tag_id):
    """Show form to edit a tag and handle form submission."""
    tag = Tag.query.get_or_404(tag_id)
    
    if request.method == "POST":
        tag.name = request.form["name"]
        db.session.commit()
        return redirect(f"/tags")
    
    return render_template("tag-edit.html", tag=tag)

@app.route("/tags/<int:tag_id>/delete", methods=["POST"])
def delete_tag(tag_id):
    """Delete a tag."""
    tag = Tag.query.get_or_404(tag_id)

    for post in tag.posts:
        post.tags.remove(tag)

    db.session.commit()
    
    db.session.delete(tag)
    db.session.commit()

    flash("Tag deleted successfully!", "success")
    return redirect(f"/tags")
