from enum import Enum


class AppStatus(Enum):
    SUCCESS = "SUCCESS", 200, "Success."
    REGISTER_USER_SUCCESS = 'REGISTER_USER_SUCCESS', 200, "Register user successful."
    SEND_MAIL_SUCCESS = 'SEND_MAIL_SUCCESS', 200, "Email sent successfully, please check your email."

    ID_INVALID = 'ID_INVALID', 400, "ID model invalid."
    GENRE_INVALID = "GENRE_INVALID", 400, "Genre invalid."
    AUTHENTICATION_FAILED = 'AUTHENTICATION_FAILED', 400, "Authentication failed."

    NAME_MANGA_INVALID = "NAME_MANGA_INVALID", 400, "Name manga invalid."
    REGISTER_USER_FAIL = "REGISTER_USER_FAIL", 400, "Register user failed."
    EMAIL_ALREADY_EXIST = "EMAIL_ALREADY_EXIST", 400, "Email already exist."
    EXPIRED_VERIFY_CODE = 'EXPIRED_VERIFY_CODE', 400, 'Your code is expired.'
    INVALID_VERIFY_CODE = "INVALID_VERIFY_CODE", 400, "Your code is invalid."
    COMIC_ALREADY_EXIST = "COMIC_ALREADY_EXIST", 400, "Comic already exist hihihi."
    USERNAME_ALREADY_EXIST = "USERNAME_ALREADY_EXIST", 400, "Username already exist."
    USER_NOT_HAVE_ENOUGH_PERMISSION = "USER_NOT_HAVE_ENOUGH_PERMISSION", 400, "User does not have enough permission."

    EMAIL_NOT_EXIST = "EMAIL_NOT_EXIST", 404, "Email does not exist."


    @property
    def message(self):
        return {
            'message': str(self.value[2]),
            'code': str(self.value[1]),
            'data': 'success' if self.value[1] in [200, 201] else 'failed'
        }
