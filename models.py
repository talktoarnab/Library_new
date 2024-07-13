from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

db = SQLAlchemy()

class Author(db.Model):
    __tablename__ = "author"
    AuthorID = db.Column(db.Integer, primary_key=True)
    FirstName = db.Column(db.String(50), nullable=False)
    LastName = db.Column(db.String(50), nullable=False)
    Bio = db.Column(db.Text)

class Publisher(db.Model):
    __tablename__ = "publisher"
    PublisherID = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(100), nullable=False)
    Address = db.Column(db.String(255))
    Phone = db.Column(db.String(15))
    Email = db.Column(db.String(100))
class Book(db.Model):
    __tablename__ = "book"
    BookID = db.Column(db.Integer, primary_key=True)
    Title = db.Column(db.String(50), nullable=False)
    ISBN = db.Column(db.String(100), nullable=False)
    Year = db.Column(db.String(50), nullable=False)
    Genre = db.Column(db.String(100), nullable=False)
    AuthorID = db.Column(db.Integer, ForeignKey("author.AuthorID"))
    PublisherID = db.Column(db.Integer, ForeignKey("publisher.PublisherID"))
    author = relationship("Author")
    publisher = relationship("Publisher")

class BookCopy(db.Model):
    __tablename__ = "bookcopy"
    CopyID = db.Column(db.Integer, primary_key=True)
    BookID = db.Column(db.Integer, db.ForeignKey('book.BookID'))
    ShelfLocation = db.Column(db.String(50))
    Status = db.Column(db.Enum('Available', 'Loaned', 'Reserved', 'Maintenance'), default='Available')
    book = relationship("Book")

class Loan(db.Model):
    __tablename__ = "loan"
    LoanID = db.Column(db.Integer, primary_key=True)
    CopyID = db.Column(db.Integer, db.ForeignKey('bookcopy.CopyID'))
    MemberID = db.Column(db.Integer, db.ForeignKey('member.MemberID'))
    LoanDate = db.Column(db.Date, nullable=False)
    DueDate = db.Column(db.Date, nullable=False)
    StaffID = db.Column(db.Integer, db.ForeignKey('staff.StaffID'))
    bookCopy = relationship("BookCopy")
    member = relationship("Member")
    staff = relationship("Staff")

class Member(db.Model):
    __tablename__ = "member"
    MemberID = db.Column(db.Integer, primary_key=True)
    FirstName = db.Column(db.String(50), nullable=False)
    LastName = db.Column(db.String(50), nullable=False)
    Address = db.Column(db.String(255))
    Phone = db.Column(db.String(15))
    Email = db.Column(db.String(100))
    MembershipDate = db.Column(db.Date, nullable=False)
    MembershipType = db.Column(db.Enum('Regular', 'Premium'), default='Regular')


class Staff(db.Model):
    __tablename__ = 'staff'
    StaffID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    FirstName = db.Column(db.String(50), nullable=False)
    LastName = db.Column(db.String(50), nullable=False)
    Email = db.Column(db.String(100), unique=True, nullable=False)
    Position = db.Column(db.String(50), nullable=False)
    HireDate = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    Phone = db.Column(db.String(15))


class ReturnedLoan(db.Model):
    __tablename__ = "returnedloan"
    ReturnedLoanID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    LoanID = db.Column(db.Integer)
    CopyID = db.Column(db.Integer, db.ForeignKey('bookcopy.CopyID'))
    MemberID = db.Column(db.Integer, db.ForeignKey('member.MemberID'))
    LoanDate = db.Column(db.Date, nullable=False)
    DueDate = db.Column(db.Date, nullable=False)
    ReturnDate = db.Column(db.Date, nullable=False)
    StaffID = db.Column(db.Integer, db.ForeignKey('staff.StaffID'))
    bookCopy = relationship("BookCopy")
    member = relationship("Member")
    staff = relationship("Staff")

