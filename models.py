from app import db
from sqlalchemy.dialects.postgresql import JSON


class Barcode(db.Model):
    __tablename__ = 'barcode'

    id = db.Column(db.String(200), primary_key=True)
    date_created = db.Column(db.DateTime(timezone=True), server_default=db.func.current_timestamp())
    production_line = db.Column(db.String(200), nullable=False)

    def __init__(self, id, production_line):
        self.id = id
        self.production_line = production_line

    def to_dict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

    def __repr__(self):
        return '<Barcode %r' % self.id
