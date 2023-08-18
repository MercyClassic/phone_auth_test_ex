from rest_framework import exceptions


class NotAuthenticated(exceptions.NotAuthenticated):
    pass


class AlreadyInvited(exceptions.PermissionDenied):
    default_detail = 'You have been already invited'


class CantInviteItSelf(exceptions.PermissionDenied):
    default_detail = "You can't invite yourself"


class CantBeInvitedByYoursInvitedUser(exceptions.PermissionDenied):
    default_detail = "You can't be invited by user who was invited by you"


class CodeNotFound(exceptions.NotFound):
    default_detail = 'Code not found'
