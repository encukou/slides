class MyList(list):
    def __str__(self):
        return ', '.join(self)
