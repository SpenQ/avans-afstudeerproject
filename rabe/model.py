from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship


Base = declarative_base()

class Session(Base):
    __tablename__ = 'sessions'

    id = Column(Integer, primary_key=True)
    session = Column(String)
    users = relationship("User", back_populates="session")

    def __repr__(self):
        return "<Session(session='%s')>" % (
            self.session)

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    dn = Column(String)
    session_id = Column(Integer, ForeignKey('sessions.id'))
    session = relationship("Session", back_populates="users")

    def __repr__(self):
        return "<User(dn='%s',session_id='%s')>" % (
            self.dn,
            self.session_id)