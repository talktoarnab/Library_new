
from flask import Flask, render_template, request, redirect, url_for

from config import Config
from models import db, Author, Book, Publisher, BookCopy, Loan, Member
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/authors')
def authors():
    authors = Author.query.all()
    return render_template('authors.html', authors=authors)


@app.route('/books', methods=['GET', 'POST'])
def books():
    if request.method == 'POST':
        search_query = request.form['search_query']
        search_genre = request.form['search_genre']
        search_author = request.form['search_author']
        print('Hi' + search_query, 'hello' + search_genre)
        if search_query:
            books = db.session.query(Book, Author, Publisher).join(Author).join(Publisher).filter(Book.Title.like(f"%{search_query}%")).all()
        if search_genre:
            books = db.session.query(Book, Author, Publisher).join(Author).join(Publisher).filter(Book.Genre.like(f"%{search_genre}%")).all()
        if search_author:
            books = db.session.query(Book, Author, Publisher).join(Author).join(Publisher).filter(Author.FirstName.like(f"%{search_author}%") | Author.LastName.like(f"%{search_author}%")).all()
        if search_query == '' and search_genre == '' and search_author == '':
            books = db.session.query(Book, Author, Publisher).join(Author).join(Publisher).all()
    else:
        books = db.session.query(Book, Author, Publisher).join(Author).join(Publisher).all()
    publisher = db.session.query(Publisher).all()
    author = db.session.query(Author).all()
    return render_template('books.html', book=books, pub=publisher, auth=author)


@app.route('/newbook', methods=['GET', 'POST'])
def newbook():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        publisher = request.form['publisher']
        isbn = request.form['isbn']
        year = request.form['year']
        genre = request.form['genre']
        if title and isbn:
            book = Book(Title=title, AuthorID=author, PublisherID=publisher, ISBN=isbn, Year=year, Genre=genre)
            db.session.add(book)
            db.session.commit()
        books = db.session.query(Book, Author, Publisher).join(Author).join(Publisher).all()
        publisher = db.session.query(Publisher).all()
        author = db.session.query(Author).all()
    return render_template('books.html', book=books, pub=publisher, auth=author)


@app.route('/bookCopies')
def bookCopies():
    if request.method == 'GET':
        search_query = request.args.get('title')
        if search_query:
            copy = db.session.query(Book, BookCopy, Loan, Member).outerjoin(BookCopy, Book.BookID == BookCopy.BookID)\
                .outerjoin(Loan, BookCopy.CopyID == Loan.CopyID)\
                .outerjoin(Member, Loan.MemberID == Member.MemberID)\
                .filter(Book.Title.like(f"{search_query}")).all()
        print(copy)
    return render_template('bookCopies.html', title=copy)


@app.route('/newCopy', methods=['GET', 'POST'])
def newcopy():
    if request.method == 'POST':
        title = request.form['title']
        status = request.form['status']
        shelf = request.form['shelf']

        if shelf:
            copy = BookCopy(BookID=title, Status=status, ShelfLocation=shelf)
            db.session.add(copy)
            db.session.commit()
        copy = db.session.query(Book, BookCopy, Loan, Member).join(BookCopy, Book.BookID == BookCopy.BookID) \
            .outerjoin(Loan, BookCopy.CopyID == Loan.CopyID) \
            .outerjoin(Member, Loan.MemberID == Member.MemberID) \
            .filter(Book.BookID.like(f"{title}")).all()
        return render_template('bookCopies.html', title=copy)


if __name__ == '__main__':
    app.run(debug=True)