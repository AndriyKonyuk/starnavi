from __future__ import absolute_import, unicode_literals
import json
import os
import lorem
import requests
from datetime import datetime
from random import randint
from celery import shared_task
from api.models import User


@shared_task
def run_bot():
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    with open(os.path.join(__location__, 'config.json')) as conf:
        data = json.loads(conf.read())
        user_numbers = data["number_of_users"]
        max_post = data["max_posts_per_user"]
        max_likes = data["max_likes_per_user"]

        for i in range(1, user_numbers + 1):
            try:
                user = User.objects.get(pk=i)
            except User.DoesNotExist:
                print("Not enough users")
                break

            token = user._generate_jwt_token()
            s = requests.Session()
            s.headers.update({'token': 'Token ' + token})
            s.headers.update({'Content-Type': 'application/json'})

            post_per_user = randint(1, max_post)
            for _ in range(post_per_user):
                payload = {
                    "title": lorem.sentence(),
                    "content": lorem.text(),
                    "like": 0,
                    "created_date": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                    "user": user.id
                }

                response = s.post("http://localhost:8000/api/post/1/", json=payload)
                print(response)

            likes_per_user = randint(1, max_likes)
            all_posts = s.get("http://localhost:8000/api/post/1/").content
            all_posts = json.loads(all_posts)
            for _ in range(likes_per_user):
                index = randint(0, len(all_posts) -1)
                print(index)
                post = all_posts[index]
                post["like"] += 1
                s.put(f"http://localhost:8000/api/post/{post['id']}/", json=post)
