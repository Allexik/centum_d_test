release: python manage.py migrate && python manage.py create_superuser && python manage.py loaddata init_tests
web: gunicorn centum_d_test.wsgi --log-file -
