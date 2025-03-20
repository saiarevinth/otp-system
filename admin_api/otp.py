import pywhatkit as kit


def sender_otp(phone_number, otp):
    kit.sendwhatmsg_instantly(phone_number, otp)


