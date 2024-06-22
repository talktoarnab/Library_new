from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

db = SQLAlchemy()

class Author(db.Model):
    AuthorID = db.Column(db.Integer, primary_key=True)
    FirstName = db.Column(db.String(50), nullable=False)
    LastName = db.Column(db.String(50), nullable=False)
    Bio = db.Column(db.Text)

class Publisher(db.Model):
    __tablename__ = "Publisher"
    PublisherID = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(100), nullable=False)
    Address = db.Column(db.String(255))
    Phone = db.Column(db.String(15))
    Email = db.Column(db.String(100))
class Book(db.Model):
    BookID = db.Column(db.Integer, primary_key=True)
    Title = db.Column(db.String(50), nullable=False)
    ISBN = db.Column(db.String(100), nullable=False)
    Year = db.Column(db.String(50), nullable=False)
    Genre = db.Column(db.String(100), nullable=False)
    AuthorID = db.Column(db.Integer, ForeignKey("author.AuthorID"))
    PublisherID = db.Column(db.Integer, ForeignKey("Publisher.PublisherID"))
    author = relationship("Author")
    publisher = relationship("Publisher")

class BookCopy(db.Model):
    __tablename__ = "BookCopy"
    CopyID = db.Column(db.Integer, primary_key=True)
    BookID = db.Column(db.Integer, db.ForeignKey('book.BookID'))
    ShelfLocation = db.Column(db.String(50))
    Status = db.Column(db.Enum('Available', 'Loaned', 'Reserved', 'Maintenance'), default='Available')
    book = relationship("Book")

class Loan(db.Model):
    __tablename__ = "Loan"
    LoanID = db.Column(db.Integer, primary_key=True)
    CopyID = db.Column(db.Integer, db.ForeignKey('BookCopy.CopyID'))
    MemberID = db.Column(db.Integer, db.ForeignKey('Member.MemberID'))
    LoanDate = db.Column(db.Date, nullable=False)
    DueDate = db.Column(db.Date, nullable=False)
    ReturnDate = db.Column(db.Date)
    StaffID = db.Column(db.Integer, db.ForeignKey('staff.StaffID'))
    bookCopy = relationship("BookCopy")
    member = relationship("Member")

class Member(db.Model):
    __tablename__ = "Member"
    MemberID = db.Column(db.Integer, primary_key=True)
    FirstName = db.Column(db.String(50), nullable=False)
    LastName = db.Column(db.String(50), nullable=False)
    Address = db.Column(db.String(255))
    Phone = db.Column(db.String(15))
    Email = db.Column(db.String(100))
    MembershipDate = db.Column(db.Date, nullable=False)
    MembershipType = db.Column(db.Enum('Regular', 'Premium'), default='Regular')