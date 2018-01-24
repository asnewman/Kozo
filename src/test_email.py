import smtplib
server = smtplib.SMTP('smtp.gmail.com', 587)

#Next, log in to the server
server.login("ashznewman", "aGH5/V2U")

#Send the mail
msg = "
Hello!" # The /n separates the message from the headers
server.sendmail("ashznewman@gmail.com", "ashznewman@gmail.com", msg)
