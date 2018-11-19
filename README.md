Starnavi test
===================

To run celery task please run thi commands in terminal:
    celery -A starnavi beat
    celery -A starnavi worker -B -l info --concurrency=1
