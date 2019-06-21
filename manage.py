# -*- coding: UTF-8 -*-
import os
from app.__init__ import create_app,db,socketio
from app.models import User,Role,Permission
from flask_script import Manager,Shell
from flask_migrate import Migrate , MigrateCommand

app =create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate =Migrate(app,db)

def make_shell_context():
    return dict(app=app,db=db,User=User,Role=Role,Permission=Permission)

manager.add_command("shell",Shell(make_context=make_shell_context))
manager.add_command('db',MigrateCommand)

if __name__=='__main__':
    #socketio.run(app)
    socketio.run(app,debug=True,host='0.0.0.0',port=5000)
    #manager.run()

