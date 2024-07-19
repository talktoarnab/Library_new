from datetime import date, timedelta

import flask
from flask import Flask, render_template, request, redirect, url_for, jsonify
from sqlalchemy import text

from config import Config
from models import db, Author, Book, Publisher, BookCopy, Loan, Member, ReturnedLoan

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
    page = request.args.get('page', 1, type=int)
    per_page = 14
    if request.method == 'POST':
        search_query = request.form['search_query']
        search_genre = request.form['search_genre']
        search_author = request.form['search_author']
        print('Hi' + search_query, 'hello' + search_genre)
        if search_query:
            books = db.session.query(Book, Author, Publisher).join(Author).join(Publisher).filter(Book.Title.like(f"%{search_query}%")).order_by(Book.Title)
        if search_genre:
            books = db.session.query(Book, Author, Publisher).join(Author).join(Publisher).filter(Book.Genre.like(f"%{search_genre}%")).order_by(Book.Title)
        if search_author:
            books = db.session.query(Book, Author, Publisher).join(Author).join(Publisher).filter(Author.FirstName.like(f"%{search_author}%") | Author.LastName.like(f"%{search_author}%")).order_by(Book.Title)
        if search_query == '' and search_genre == '' and search_author == '':
            books = db.session.query(Book, Author, Publisher).join(Author).join(Publisher).order_by(Book.Title)
    else:
        books = db.session.query(Book, Author, Publisher).join(Author).join(Publisher).order_by(Book.Title)
    paginatedbook = books.paginate(page=page, per_page=per_page, error_out=False)
    next_url = url_for('books', page=paginatedbook.next_num) if paginatedbook.has_next else None
    prev_url = url_for('books', page=paginatedbook.prev_num) if paginatedbook.has_prev else None
    publisher = db.session.query(Publisher).all()
    author = db.session.query(Author).all()
    return render_template('books.html', book=paginatedbook.items, pub=publisher, auth=author,next_url=next_url, prev_url=prev_url)


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
                .filter(Book.BookID == search_query).all()
            print(copy)
            count = db.session.query(Book, BookCopy).outerjoin(BookCopy, Book.BookID == BookCopy.BookID)\
                .filter(Book.BookID == search_query, BookCopy.Status.like(f"Available")).all()
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
            if ret == 'yes' or ret == 'yesmember':
                result = db.session.execute(text('insert into Returnedloan(LoanID,CopyID,MemberID,StaffID,LoanDate,DueDate) select * from Loan where CopyID = :cid'), {'cid': copy})
                result = db.session.execute(text('delete from Loan where CopyID = :cid'), {'cid': copy})
                result = db.session.execute(text("update bookcopy set Status='Available' where CopyID = :cid"),
                                            {'cid': copy})
                db.session.commit()
        copytitle = db.session.query(Book, BookCopy, Loan, Member).join(BookCopy, Book.BookID == BookCopy.BookID) \
            .outerjoin(Loan, BookCopy.CopyID == Loan.CopyID) \
            .outerjoin(Member, Loan.MemberID == Member.MemberID) \
            .filter(Book.BookID.like(f"{title}")).all()
        count = db.session.query(Book, BookCopy).outerjoin(BookCopy, Book.BookID == BookCopy.BookID) \
            .filter(Book.BookID.like(f"{title}"), BookCopy.Status.like(f"Available")).all()
        count = len(count)
        if ret == 'yes' or ret == 'no':
            return render_template('bookCopies.html', title=copytitle, c=count)
        elif ret == 'yesmember':
            copy = db.session.query(Member, Loan, BookCopy, Book).outerjoin(Loan, Member.MemberID == Loan.MemberID) \
                .outerjoin(BookCopy, Loan.CopyID == BookCopy.CopyID) \
                .outerjoin(Book, BookCopy.BookID == Book.BookID) \
                .filter(Member.MemberID == member).all()
            count = db.session.query(Member, ReturnedLoan, BookCopy, Book)\
                .join(ReturnedLoan, Member.MemberID == ReturnedLoan.MemberID)\
                .join(BookCopy, ReturnedLoan.CopyID == BookCopy.CopyID) \
                .join(Book, BookCopy.BookID == Book.BookID) \
                .filter(Member.MemberID == member).all()
            return render_template('memberloan.html', title=copy, c=count)


@app.route('/members', methods=['GET', 'POST'])
def members():
    page = request.args.get('page', 1, type=int)
    per_page = 12
    if request.method == 'POST':
        search_name = request.form['search_name']
        search_email = request.form['search_mail']
        search_phone = request.form['search_phone']
        if search_name:
            members = db.session.query(Member).filter(Member.FirstName.like(f"%{search_name}%") | Member.LastName.like(f"%{search_name}%")).order_by(Member.FirstName)
        if search_email:
            members = db.session.query(Member).filter(Member.Email.like(f"%{search_email}%")).order_by(Member.FirstName)
        if search_phone:
            members = db.session.query(Member).filter(Member.Phone.like(f"%{search_phone}%")).order_by(Member.FirstName)
        if search_name == '' and search_email == '' and search_phone == '':
            members = db.session.query(Member).order_by(Member.FirstName)
    else:
        members = db.session.query(Member).order_by(Member.FirstName)
    paginatedmembers = members.paginate(page=page, per_page=per_page, error_out=False)
    next_url = url_for('members', page=paginatedmembers.next_num) if paginatedmembers.has_next else None
    prev_url = url_for('members', page=paginatedmembers.prev_num) if paginatedmembers.has_prev else None
    return render_template('members.html', member=paginatedmembers.items,next_url=next_url,
                           prev_url=prev_url)


@app.route('/memberloan')
def memberloan():
    if request.method == 'GET':
        search_query = request.args.get('member')
        if search_query:
            copy = db.session.query(Member, Loan, BookCopy, Book).outerjoin(Loan, Member.MemberID == Loan.MemberID)\
                .outerjoin(BookCopy, Loan.CopyID == BookCopy.CopyID)\
                .outerjoin(Book, BookCopy.BookID == Book.BookID)\
                .filter(Member.MemberID == search_query).all()
            count = db.session.query(Member, ReturnedLoan, BookCopy, Book).join(ReturnedLoan, Member.MemberID == ReturnedLoan.MemberID)\
                .join(BookCopy, ReturnedLoan.CopyID == BookCopy.CopyID)\
                .join(Book, BookCopy.BookID == Book.BookID)\
                .filter(Member.MemberID == search_query).all()
    return render_template('memberloan.html', title=copy, c=count)


@app.route('/newmember', methods=['GET', 'POST'])
def newmember():
    if request.method == 'POST':
        first = request.form['first']
        second = request.form['second']
        add = request.form['add']
        phone = request.form['phone']
        email = request.form['email']
        memdate = request.form['memdate']
        type = request.form['type']
        if first and second and memdate and type:
            member = Member(FirstName=first, LastName=second, Address=add, Phone=phone, Email=email, MembershipDate=memdate, MembershipType=type)
            db.session.add(member)
            db.session.commit()
        members = Member.query.order_by(Member.FirstName).all()
    return render_template('members.html', member=members)


@app.route('/newpublisher', methods=['GET', 'POST'])
def newpublisher():
    if request.method == 'POST':
        pub = request.form['publisher']
        ph = request.form['phone']
        email = request.form['email']
        add = request.form['add']
        if pub:
            newpublisher = Publisher(Name=pub, Address=add, Phone=ph, Email=email)
            db.session.add(newpublisher)
            db.session.commit()
        publisher = Publisher.query.order_by(Publisher.Name).all()
    return render_template('publisher.html', publisher=publisher)

@app.route('/publisher')
def publisher():
    publisher = Publisher.query.order_by(Publisher.Name).all()
    return render_template('publisher.html', publisher=publisher)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
