class Collect(object):
    def __init__(self):
        self._objects = []

    @property
    def objects(self):
        return self._objects

    def append_object(self, obj):
        return self._objects.append(obj)

    def sort_objects(self):
        return sorted(self._objects, key=lambda x: x.fit, reverse=True)

    def size_of_col(self):
        return len(self._objects)