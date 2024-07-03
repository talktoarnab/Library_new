from datetime import date, timedelta

from flask import Flask, render_template, request, redirect, url_for, jsonify
from sqlalchemy import text

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
    authors = Author.query.order_by(Author.FirstName).all()
    return render_template('authors.html', authors=authors)


@app.route('/newauthor', methods=['GET', 'POST'])
def newauthor():
    if request.method == 'POST':
        fname = request.form['first']
        sname = request.form['second']
        bio = request.form['bio']
        auth = Author(FirstName=fname, LastName=sname, Bio=bio)
        db.session.add(auth)
        db.session.commit()
    authors = Author.query.order_by(Author.FirstName).all()
    return render_template('authors.html', authors=authors)


@app.route('/books', methods=['GET', 'POST'])
def books():
    if request.method == 'POST':
        search_query = request.form['search_query']
        search_genre = request.form['search_genre']
        search_author = request.form['search_author']
        print('Hi' + search_query, 'hello' + search_genre)
        if search_query:
            books = db.session.query(Book, Author, Publisher).join(Author).join(Publisher).order_by(Book.Title).filter(Book.Title.like(f"%{search_query}%")).all()
        if search_genre:
            books = db.session.query(Book, Author, Publisher).join(Author).join(Publisher).order_by(Book.Title).filter(Book.Genre.like(f"%{search_genre}%")).all()
        if search_author:
            books = db.session.query(Book, Author, Publisher).join(Author).join(Publisher).order_by(Book.Title).filter(Author.FirstName.like(f"%{search_author}%") | Author.LastName.like(f"%{search_author}%")).all()
        if search_query == '' and search_genre == '' and search_author == '':
            books = db.session.query(Book, Author, Publisher).join(Author).join(Publisher).order_by(Book.Title).all()
    else:
        books = db.session.query(Book, Author, Publisher).join(Author).join(Publisher).order_by(Book.Title).all()
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
        books = db.session.query(Book, Author, Publisher).join(Author).join(Publisher).order_by(Book.Title).all()
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
            count = db.session.query(Book, BookCopy).outerjoin(BookCopy, Book.BookID == BookCopy.BookID)\
                .filter(Book.Title.like(f"{search_query}"), BookCopy.Status.like(f"Available")).all()
            count = len(count)
    return render_template('bookCopies.html', title=copy, c=count)


@app.route('/newcopy', methods=['GET', 'POST'])
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
        count = db.session.query(Book, BookCopy).outerjoin(BookCopy, Book.BookID == BookCopy.BookID) \
            .filter(Book.BookID.like(f"{title}"), BookCopy.Status.like(f"Available")).all()
        count = len(count)
        return render_template('bookCopies.html', title=copy,c=count)


@app.route('/search_member')
def search_member():
    query = request.args.get('query', '')
    members = Member.query.filter(
        (Member.FirstName.like(f"%{query}%")) |
        (Member.LastName.like(f"%{query}%")) |
        (Member.Email.like(f"%{query}%"))
    ).all()

    member_list = [
        {"MemberID": member.MemberID, "FirstName": member.FirstName, "LastName": member.LastName, "Email": member.Email}
        for member in members]
    return jsonify(members=member_list)


@app.route('/newloan', methods=['GET', 'POST'])
def newloan():
    if request.method == 'POST':
        copy = request.form['copyID']
        member = request.form['memberId']
        title = request.form['title']
        ret = request.form['return']
        print("titile" + title)
        if copy and member:
            if ret == 'no':
                loan = Loan(CopyID=copy, MemberID=member, StaffID=5, LoanDate=date.today(),
                            DueDate=date.today() + timedelta(days=15))
                db.session.add(loan)
                copyrow = BookCopy.query.filter_by(CopyID=copy).first()
                copyrow.Status = 'Loaned'
                db.session.commit()
            if ret == 'yes':
                result = db.session.execute(text('insert into Returnedloan(LoanID,CopyID,MemberID,StaffID,LoanDate,DueDate) select * from Loan where CopyID = :cid'), {'cid': copy})
                result = db.session.execute(text('delete from Loan where CopyID = :cid'), {'cid': copy})
                result = db.session.execute(text("update bookcopy set Status='Available' where CopyID = :cid"),
                                            {'cid': copy})
                db.session.commit()
        copytitle = db.session.query(Book, BookCopy, Loan, Member).join(BookCopy, Book.BookID == BookCopy.BookID) \
            .outerjoin(Loan, BookCopy.CopyID == Loan.CopyID) \
            .outerjoin(Member, Loan.MemberID == Member.MemberID) \
            .filter(Book.BookID.like(f"{title}")).all()
        print(copytitle)
        count = db.session.query(Book, BookCopy).outerjoin(BookCopy, Book.BookID == BookCopy.BookID) \
            .filter(Book.BookID.like(f"{title}"), BookCopy.Status.like(f"Available")).all()
        count = len(count)
        return render_template('bookCopies.html', title=copytitle, c=count)


@app.route('/authors')
def authors():
    authors = Author.query.order_by(Author.FirstName).all()
    return render_template('authors.html', authors=authors)


if __name__ == '__main__':
    app.run(debug=True)

