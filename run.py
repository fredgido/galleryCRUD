import datetime
import os
import flask
from flask import Flask, request, abort
from flask import render_template, send_from_directory, redirect
from sqlalchemy import func
from flask_sqlalchemy import SQLAlchemy
import graphene
from flask import Flask, abort
from flask_graphql import GraphQLView
from flask_sqlalchemy import SQLAlchemy
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from graphene import relay
import validators
import requests
import json
from concurrent.futures import *

app = Flask(__name__)

POSTS_PER_PAGE = int(os.getenv('POSTS_PER_PAGE', 20))
THUMB_SIZE = int(os.getenv('THUMB_SIZE', 150))
THUMB_SIZE = (THUMB_SIZE, THUMB_SIZE)
PORT = int(os.getenv('FLASK_PORT', 5000))
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_SIZE', 16 * 1024 * 1024))
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI',
                                                  'postgresql://postgres:postgres@localhost/postgres')
# 'postgresql://postgres:postgres@db:5432/postgres''postgresql://postgres:postgres@localhost/postgres''sqlite:///db.db'
# app.secret_key = 'super secret key'
# app.config['SESSION_TYPE'] = 'filesystem'



db = SQLAlchemy(app)


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    json = db.Column(db.JSON)


    # user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return repr(id)


db.create_all()


@app.route("/test", methods=['GET'])
def flex():
    return render_template("indexgraphql.html")


@app.route("/", methods=['GET'])
def index():
    page_number = request.args.get("page")
    page_number = 1 if page_number is None else int(page_number)
    posts_list = Post.query.order_by(Post.id.desc()).paginate(page_number, per_page=POSTS_PER_PAGE)
    return render_template("index.html", posts=posts_list.items,
                           size=posts_list.total, posts_per_page=POSTS_PER_PAGE)


@app.route("/post", methods=['GET'])
def postget():
    post_id = abort(404) if request.args.get("id") is None else int(request.args.get("id"))
    post = Post.query.filter_by(id=post_id).first()
    if post is None:
        abort(404)
    return render_template("post.html", file=post.file, post=post,
                           postdump=json.dumps({"id": post.id, "file": post.file, "text": str(post.json)}, indent=4))


# @app.route("/post", methods=['POST', 'PUT', 'PATCH'])
# def postpoint():
#     if request.files.get("file") is None:
#         return "no file", 400
#
#     new_post_obj = Post(id=post_id, file=filename, text=text)
#     db.session.add(new_post_obj)
#     db.session.commit()
#
#     return redirect("../post?id=" + str(post_id), code=302)


@app.route("/create", methods=['GET'])
def create():
    return render_template("create.html")


@app.route("/about", methods=['GET'])
def about():
    return render_template("about.html")

#
# @app.route("/import", methods=['GET'])
# def importposts():
#     if request.args.get("do") is None:
#         return render_template("import.html")
#
#     posts = []
#     s = requests.Session()
#     for i in range(1, 6):
#         reply = s.get("https://safebooru.donmai.us/posts.json?tags=ordfavgroup%3A5730&page=" + str(i))
#         if len(json.loads(reply.text)) < 1:
#             break
#         posts.extend(json.loads(reply.text))
#     posts.reverse()
#
#     def download(url, s, name, folder):
#         getreply = s.get(url)
#         if os.path.exists(os.path.join("static", folder, name)):
#             return
#         with open(os.path.join("static", folder, name), 'wb') as f:
#             f.write(getreply.content)
#
#     s = requests.Session()
#     with ThreadPoolExecutor(max_workers=6) as executor:
#         for idx, post in enumerate(posts):
#             text = str(post["id"])
#             post_id = db.session.query(func.max(Post.id)).scalar()
#             post_id = 0 if post_id is None else post_id + 1
#
#             executor.submit(download, url=post["file_url"], s=s,
#                             name=str(post_id) + "." + post["file_ext"],
#                             folder="orig")
#             executor.submit(download, url=post["preview_file_url"], s=s,
#                             name=str(post_id) + ".jpg", folder="thumb")
#
#             new_post_obj = Post(id=post_id, file=str(post_id) + "." + post["file_ext"], text=text)
#             db.session.add(new_post_obj)
#             db.session.commit()
#
#     return redirect("../", code=302)


# @app.route("/api/post", methods=['GET'])
# def listing():
#     if request.args.get("id") is not None:
#         post = Post.query.filter_by(id=request.args.get("id")).first()
#         if post is None:
#             abort(404)
#         return json.dumps({'id': post.id,'text': post.text, 'file': post.file})
#
#     page_number = 1 if request.args.get("page") is None else int(request.args.get("page"))
#     page_limit = 20 if request.args.get("limit") is None else int(request.args.get("limit"))
#
#     posts_list = Post.query.order_by(Post.id.desc()).paginate(page_number, per_page=page_limit)
#     posts_list = [{"id": post.id, "file": post.file, "text": post.text} for post in posts_list.items]
#
#     return json.dumps({'posts': posts_list,
#                        'page': page_number,
#                        'limit': page_limit},
#                       indent=4)


@app.route("/api/post", methods=['POST'])
def new_post():

    posted_json = request.json
    if posted_json is None:
            abort(400)



    new_post_obj = Post( json=request.json)
    db.session.add(new_post_obj)
    db.session.commit()

    return json.dumps({'id': new_post_obj.id}, indent=4)




# @app.route("/api/post", methods=['DELETE'])
# def delete_post():
#     posted_json = request.json
#     if posted_json is None:
#         posted_json = {'id': request.args.get("id")}
#         if posted_json['id'] is None:
#             abort(400)
#
#     post = db.session.query(Post).get(posted_json['id'])
#     # post = Post.query.filter_by(id=id).first()
#     if post is None:
#         abort(404)
#
#     os.remove(os.path.join("static", "orig", post.file))
#     db.session.delete(post)
#     db.session.commit()
#     return json.dumps({'status': 'ok'}, indent=4)


# class PostObject(SQLAlchemyObjectType):
#     class Meta:
#         model = Post
#         interfaces = (relay.Node,)
#
#
# class Query(graphene.ObjectType):
#     node = relay.Node.Field()
#     all_posts = SQLAlchemyConnectionField(PostObject.connection)
#     # def resolve_search(self, info, **args):
#     #     q = args.get("q")  # Search query
#     #
#     #     # Get queries
#     #     posts_query = Post.get_query(info)
#     #     author_query = Author.get_query(info)
#     #
#     #     # Query Books
#     #     posts = posts_query.filter((Post.title.contains(q)) |
#     #                                   (Post.Author.any(
#     #                                   Author.name.contains(q)))).all()
#     #
#     #     # Query Authors
#     #     authors = author_query.filter(User.name.contains(q)).all()
#     #
#     #     return authors + posts  # Combine lists
#
#
# # Mutation Objects Schema
# class CreatePost(graphene.Mutation):
#     class Arguments:
#         id = graphene.Int(required=False)
#         file = graphene.String(required=True)
#         text = graphene.String(required=True)
#
#     post = graphene.Field(lambda: PostObject)
#
#     def mutate(self, info, text, file):
#         post = Post(text=text, file=file)
#         db.session.add(post)
#         db.session.commit()
#         return CreatePost(post=post)
#
#
# # Mutation Objects Schema
# class ModifyPost(graphene.Mutation):
#     class Arguments:
#         id = graphene.Int(required=True)
#         file = graphene.String(required=False)
#         text = graphene.String(required=True)
#
#     post = graphene.Field(lambda: PostObject)
#
#     def mutate(self, info, id, file, text):
#         post = db.session.query(Post).get(id)
#         if post is None:
#             abort(404)
#         post.text = text
#         post.file = file  # download if url
#
#         db.session.commit()
#         return CreatePost(post=post)
#
#
# #class UploadFile(graphene.ClientIDMutation):
# #    class Input:
# #        pass
# #        # nothing needed for uploading file
# #
# #    # your return fields
# #    success = graphene.String()
# #
# #    @classmethod
# #    def mutate_and_get_payload(cls, root, info, **input):
# #        # When using it in Django, context will be the request
# #        files = info.context.FILES
# #        # Or, if used in Flask, context will be the flask global request«
# #        # files = request.files
# #        # do something with files
# #        return UploadFile(success=True)
#
#
# class Mutation(graphene.ObjectType):
#     save_post = CreatePost.Field()
#     mod_post = ModifyPost.Field()
#
#
# # noinspection PyTypeChecker
# schema = graphene.Schema(query=Query, mutation=Mutation, types=[PostObject])
#
# app.add_url_rule('/graphql', view_func=GraphQLView.as_view(
#     'graphql',
#     schema=schema, graphiql=True
# ))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=PORT)
