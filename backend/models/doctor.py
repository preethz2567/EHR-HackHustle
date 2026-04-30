class Doctor:
    def __init__(self, id, name, email, specialization):
        self.id = id
        self.name = name
        self.email = email
        self.specialization = specialization

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'email': self.email, 'specialization': self.specialization}

    @classmethod
    def from_dict(cls, data):
        return cls(data.get('id'), data.get('name'), data.get('email'), data.get('specialization'))
