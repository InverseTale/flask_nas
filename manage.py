from flask_script import Manager
from flask_migrate import MigrateCommand
from app import create_app

if __name__ == '__main__':
    app = create_app()
    manager = Manager(app)
    manager.add_command('db', MigrateCommand)
    manager.run()
