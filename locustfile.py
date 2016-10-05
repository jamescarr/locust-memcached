from locust import TaskSet, task
from memcached import MemcachedLocust

class UserBehavior(TaskSet):
    @task
    def set(self):
        self.client.random_set()


class WebsiteUser(MemcachedLocust):
    task_set = UserBehavior
    min_wait = 1000
    max_wait = 1000
    max_set_size = 9000
    number_of_keys = 10
