import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage


def send_email(to, subject, message, message_type='text'):

    from_email = 'fomin_from_mordovia@mail.ru'

    msg = MIMEMultipart()

    msg['From'] = from_email
    msg['To'] = to
    msg['Subject'] = subject

    if message_type == 'text':
        msg.attach(MIMEText(message))
    elif message_type == 'html':
        msg.attach(MIMEText(message, 'html'))


    smtp_server = 'smtp.mail.ru'
    smtp_port = 587
    smtp_username = 'fomin_from_mordovia@mail.ru'
    smtp_password = 'SECRET'
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.ehlo()
    server.starttls()
    server.login(smtp_username, smtp_password)
    server.sendmail(from_email, to, msg.as_string())
    server.quit()


to_email = 'heartmarshall@yandex.ru'
subject = 'ComNet HW'
message = 'Test of email sender'
message_type = 'text' # или html 

send_email(to_email, subject, message, message_type)
