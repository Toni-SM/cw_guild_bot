import json
import html
import pydoc
import sqlalchemy
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

import settings

__all__=["User", "subscribe", "unsubscribe", "users", "user_by_id"]

# sqlalchemy engine
_engine=sqlalchemy.create_engine(settings.SQL_URL, echo=False)

# sqlalchemy session
session_factory=sessionmaker(bind=_engine)
Session=scoped_session(session_factory)

# model
Base=declarative_base()

class User(Base):
    """
    Telegram user model
    """
    __tablename__="user"
    
    id=sqlalchemy.Column(sqlalchemy.String, primary_key=True, unique=True)
    username=sqlalchemy.Column(sqlalchemy.String, unique=False, default="")
    full_name=sqlalchemy.Column(sqlalchemy.String, unique=False, default="")
    link=sqlalchemy.Column(sqlalchemy.String, unique=False, default="")
    is_bot=sqlalchemy.Column(sqlalchemy.Boolean, unique=False, default=False)
    
    cw_name=sqlalchemy.Column(sqlalchemy.String, unique=False, default="")
    cw_level=sqlalchemy.Column(sqlalchemy.Integer, unique=False, default=0)
    updated=sqlalchemy.Column(sqlalchemy.String, unique=False, default="")
    crafting=sqlalchemy.Column(sqlalchemy.String, unique=False, default="{}")
    
    def __repr__(self):
        return '<User {0}: {1} ({2})>'.format(self.id, self.username, self.full_name)
        
class Data(Base):
    """
    Data model
    """
    __tablename__="data"
    key=sqlalchemy.Column(sqlalchemy.String, primary_key=True, unique=True)
    value=sqlalchemy.Column(sqlalchemy.String, unique=False, default="")
    type_of=sqlalchemy.Column(sqlalchemy.String, unique=False, default="str")
    
    def __repr__(self):
        return '<Data>'
    
Base.metadata.create_all(_engine)

# functions
def subscribe(user):
    """
    Subscribe/add an user to the database
    """
    _session=Session(expire_on_commit=False)
    if not _session.query(User).get(user.id):
        _session.add(user)
        _session.commit()
        _session.expunge_all()
        Session.remove()
        return True
    Session.remove()
    return False

def unsubscribe(user):
    """
    Unsubscribe/remove an user from the database
    """
    _session=Session(expire_on_commit=False)
    _user=_session.query(User).get(user.id)
    if _user:
        _session.delete(_user)
        _session.commit()
        Session.remove()
        return True
    Session.remove()
    return False
    
def users():
    """
    List all subscribed users
    """
    _session=Session(expire_on_commit=False)
    response=_session.query(User).order_by(User.cw_level).all()
    Session.remove()
    return response

def user_by_id(id):
    """
    Get an User instance by its id
    """
    _session=Session(expire_on_commit=False)
    _user=_session.query(User).get(id)
    if _user:
        Session.remove()
        return _user
    Session.remove()
    return None
    
def filtered_users(user, delta_upper, delta_lower):
    """
    List of filtered users according to their level
    """
    _session=Session(expire_on_commit=False)
    simple_users=[]
    strong_users=[]
    _user=_session.query(User).get(user.id)
    if _user:
        simple_users=_session.query(User).filter(User.cw_level<=_user.cw_level+delta_upper).filter(User.cw_level>=_user.cw_level-delta_lower).order_by(User.cw_level).all()
        strong_users=_session.query(User).filter(User.cw_level>_user.cw_level+delta_upper).order_by(User.cw_level).all()
    else:
        simple_users=_session.query(User).order_by(User.cw_level).all()
    Session.remove()
    return (simple_users, strong_users)
    
def update_user(user):
    """
    Update user
    """
    _session=Session(expire_on_commit=False)
    _user=_session.query(User).get(user.id)
    if _user:
        try:
            if user.username!=None:
                _user.username=user.username
            if user.full_name!=None:
                _user.full_name=user.full_name
            if user.link!=None:
                _user.link=user.link
            if user.cw_name!=None:
                _user.cw_name=user.cw_name
            if user.cw_level!=None:
                _user.cw_level=user.cw_level
            if user.crafting!=None:
                _user.crafting=user.crafting
            _user.updated=str(datetime.utcnow())
            _session.add(_user)
            _session.commit()
        except Exception as e:
            print("Exception model.update_user", e)
            Session.remove()
            return False
        Session.remove()
        return True
    Session.remove()
    return False
    
def get_data(key, default=None):
    """
    Get data from database
    Returns the default value if key does not exists
    """
    _session=Session(expire_on_commit=False)
    _data=_session.query(Data).get(key.upper())
    if _data:
        Session.remove()
        f=pydoc.locate(_data.type_of)
        return f(_data.value)
    Session.remove()
    return default
    
def set_data(key, value):
    """
    Set data on database
    """
    _session=Session(expire_on_commit=False)
    _data=_session.query(Data).get(key.upper())
    if _data:
        try:
            _data.value=str(value)
            _data.type_of=type(value).__name__
            _session.add(_data)
            _session.commit()
        except Exception as e:
            print("Exception model.update_data", e)
            Session.remove()
            return False
        Session.remove()
        return True
    else:
        try:
            _data=Data(key=key.upper(),
                       value=str(value),
                       type_of=type(value).__name__)
            _session.add(_data)
            _session.commit()
            _session.expunge_all()
            Session.remove()
            return True
        except Exception as e:
            print("Exception model.new_data", e)
            Session.remove()
            return False
    Session.remove()
    return False

def del_data(key):
    """
    Remove data from database
    """
    _session=Session(expire_on_commit=False)
    _data=_session.query(Data).get(key)
    if _data:
        _session.delete(_data)
        _session.commit()
        Session.remove()
        return True
    Session.remove()
    return False
    

if __name__=="__main__":
    print(statistics(show=True, export=True))
    