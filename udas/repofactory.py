# repofactory.py
# Created by abdularis on 10/11/17


from udas.dbrepository import *


class RepositoryFactory:

    def study_repo(self):
        pass

    def class_repo(self):
        pass

    def student_repo(self):
        pass

    def token_repo(self):
        pass

    def admin_repo(self):
        pass

    def annc_repo(self):
        pass


class DbRepoFactory(RepositoryFactory):

    def __init__(self):
        self._admin_repo = DbAdminRepo()
        self._token_repo = DbTokenRepo()
        self._class_repo = DbClassRepo()
        self._student_repo = DbStudentRepo()
        self._annc_repo = DbAnnouncementRepo()
        self._study_repo = DbStudyRepo()

    def admin_repo(self):
        return self._admin_repo

    def token_repo(self):
        return self._token_repo

    def class_repo(self):
        return self._class_repo

    def student_repo(self):
        return self._student_repo

    def annc_repo(self):
        return self._annc_repo

    def study_repo(self):
        return self._study_repo


rf = DbRepoFactory()


__all__ = ('RepositoryFactory', 'rf')
