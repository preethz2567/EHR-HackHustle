class Patient:
    def __init__(self, id, name, email):
        self.id = id
        self.name = name
        self.email = email

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'email': self.email}

    @classmethod
    def from_dict(cls, data):
        return cls(data.get('id'), data.get('name'), data.get('email'))
