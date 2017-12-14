# wtformutil.py
# Created by abdularis on 11/11/17

from wtforms.validators import InputRequired, ValidationError

from unma.database import db_session


class UniqueValue(object):

    def __init__(self, model_t, model_id_t, edit_mode=False, last_value='', message="This field must be unique"):
        self.message = message
        self.model_t = model_t
        self.model_id_t = model_id_t
        self.edit_mode = edit_mode
        self.last_value = last_value

    def __call__(self, form, field):
        result = db_session.query(self.model_t).filter(self.model_id_t == field.data).first()
        if result:
            if not self.edit_mode or field.data != self.last_value:
                raise ValidationError(self.message)

    @staticmethod
    def set_edit_mode_on_field(field, edit_mode, last_value):
        for validator in field.validators:
            if isinstance(validator, UniqueValue):
                validator.edit_mode = edit_mode
                validator.last_value = last_value


class SwitchableRequired(InputRequired):

    def __init__(self, enable=True, message=None):
        super().__init__(message)
        self.enable = enable

    def __call__(self, form, field):
        if self.enable:
            super().__call__(form, field)
