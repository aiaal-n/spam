
import random



me = 'neustroev.aiaal@gmail.com' # change to your email
p_reader = open('password.txt', 'rb') # edit for your password
cipher = p_reader.read().decode("utf-8")
recipients = ['naumov.radik@gmail.com'] # enter recipients here


# def spamEveryMinute():
#     while (True):
#         fp = open('message.txt', 'rb')
#         #multipart class is for multiple recipients
#         msg = MIMEText(fp.read(), 'plain', 'utf-8')
#         fp.close()

#         thread_number = random.randint(0, 10000)
#         msg['Subject'] = Header('Minutely Spam Report (randomizer: ' + str(thread_number) + ')', 'utf-8')
#         msg['From'] = me
#         msg['To'] = ', '.join(recipients)

#         s = smtplib.SMTP(host='smtp.gmail.com', port=587)
#         s.ehlo()
#         s.starttls()
#         s.ehlo()
#         s.login(me, cipher)
#         s.sendmail(me, recipients, msg.as_string())

#         print ("Email sent to: " + ', '.join(recipients))
#         s.quit()
#         try:
#             time.sleep(5) # change rate of fire here
#         except KeyboardInterrupt:
#             print('Спаммер остановлен')
#             break;



# spamEveryMinute()
