cd C:\CredSoft

# Delete all migration files from all apps
Remove-Item -Path MembersApp\migrations\0*.py -ErrorAction SilentlyContinue
Remove-Item -Path LoanApp\migrations\0*.py -ErrorAction SilentlyContinue
Remove-Item -Path RecPayApp\migrations\0*.py -ErrorAction SilentlyContinue
Remove-Item -Path UserAuth\migrations\0*.py -ErrorAction SilentlyContinue
Remove-Item -Path SysSetup\migrations\0*.py -ErrorAction SilentlyContinue
Remove-Item -Path coa\migrations\0*.py -ErrorAction SilentlyContinue
Remove-Item -Path FinanceApp\migrations\0*.py -ErrorAction SilentlyContinue
Remove-Item -Path InvestApp\migrations\0*.py -ErrorAction SilentlyContinue


# Delete pycache folders
Remove-Item -Path __pycache__ -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path MembersApp\__pycache__ -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path MembersApp\migrations\__pycache__ -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path LoanApp\__pycache__ -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path RecPayApp\__pycache__ -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path UserAuth\__pycache__ -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path SysSetup\__pycache__ -Recurse -Force -ErrorAction 
Remove-Item -Path InvestApp\__pycache__ -Recurse -Force -ErrorAction 

# Delete SQLite database
Remove-Item -Path db.sqlite3 -ErrorAction SilentlyContinue

python manage.py makemigrations SysSetup
python manage.py makemigrations UserAuth
python manage.py makemigrations MembersApp
python manage.py makemigrations coa
python manage.py makemigrations LoanApp
python manage.py makemigrations RecPayApp
python manage.py makemigrations FinanceApp
python manage.py makemigrations InvestApp

python manage.py migrate SysSetup
python manage.py migrate UserAuth
python manage.py migrate MembersApp
python manage.py migrate coa
python manage.py migrate LoanApp
python manage.py migrate RecPayApp
python manage.py migrate FinanceApp
python manage.py migrate InvestApp