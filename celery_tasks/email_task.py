import os
from email.message import EmailMessage
from dotenv import load_dotenv
load_dotenv('.env')
import smtplib
email_sender = 'bookservice.law@gmail.com'
email_password = os.getenv('MAIL_PASSWORD')
from celery import shared_task
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import schedule
import datetime

@shared_task(bind=True,autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 5},
             name='send_email:send_emaila')
def send_emaila(self, subject=str, recipient=str, message=str):
    subj = subject
    body = message

    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = recipient
    em['Subject'] = subj
    em.set_content(body)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(email_sender, email_password)
    server.sendmail(email_sender, recipient, em.as_string())
    server.quit()
    return 'Email has been sent'

def send_emailb(buku:dict, subject=str, recipient=str, mulai=datetime.date, selesai=datetime.date):
    em = MIMEMultipart()
    # em = EmailMessage()
    em['From'] = email_sender
    em['To'] = recipient
    em['Subject'] = subject
    html = get_html(buku, mulai, selesai)
    em.attach(MIMEText(html, 'html'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(email_sender, email_password)
    server.sendmail(email_sender, recipient, em.as_string())
    server.quit()
    return 'Email has been sent'

def send_email_start(buku:dict, subject=str, recipient=str, mulai=datetime.date, selesai=datetime.date):
    em = MIMEMultipart()
    # em = EmailMessage()
    em['From'] = email_sender
    em['To'] = recipient
    em['Subject'] = subject
    html = get_html(buku, mulai, selesai)
    em.attach(MIMEText(html, 'html'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(email_sender, email_password)
    server.sendmail(email_sender, recipient, em.as_string())
    server.quit()
    return 'Email has been sent'

@shared_task(bind=True,autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 5},
             name='send_email:reminder_schedule')
def reminder_schedule(self, buku:dict, mulai=str, selesai=str, recipient=str):
    mulai = datetime.datetime.strptime(mulai, '%Y-%m-%d').date()
    selesai = datetime.datetime.strptime(selesai, '%Y-%m-%d').date()
    
    send_email_start(buku, 'Reading Reminder!', recipient, mulai, selesai)
    schedule.every().day.do(lambda: send_emailb(buku, 'Reading Reminder!', recipient, mulai, selesai))
    while selesai > datetime.date.today():
        schedule.run_pending()
    # email terakhir
    return 'All emails has been sent'

def get_html_start(buku, mulai, selesai):
    sisawaktu =  selesai - mulai
    html = """

    <!DOCTYPE HTML PUBLIC "-//W3C//DTD XHTML 1.0 Transitional //EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">
  <head>
      <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <meta name="x-apple-disable-message-reformatting">
      <meta http-equiv="X-UA-Compatible" content="IE=edge">
      <title></title>
      
      <style type="text/css">
        @media only screen and (min-width: 620px) {
          .u-row {
            width: 600px !important;
          }
          .u-row .u-col {
            vertical-align: top;
          }
          
          .u-row .u-col-50 {
            width: 300px !important;
          }
          
          .u-row .u-col-100 {
            width: 600px !important;
          }
          
        }
        
        @media (max-width: 620px) {
          .u-row-container {
            max-width: 100% !important;
            padding-left: 0px !important;
            padding-right: 0px !important;
          }
          .u-row .u-col {
            min-width: 320px !important;
            max-width: 100% !important;
            display: block !important;
          }
          .u-row {
            width: 100% !important;
          }
          .u-col {
            width: 100% !important;
          }
          .u-col > div {
            margin: 0 auto;
          }
        }
        body {
          margin: 0;
          padding: 0;
          font-family:'Poppins', sans-serif;
          background-color: black;
        }
        
        table,
        tr,
        td {
          vertical-align: top;
          border-collapse: collapse;
        }
        
        p {
          margin: 0;
        }
        
        .ie-container table,
        .mso-container table {
          table-layout: fixed;
        }
        
        * {
          line-height: inherit;
        }
        
        a[x-apple-data-detectors='true'] {
          color: inherit !important;
          text-decoration: none !important;
        }
        
        table, td { color: #000000; } #u_body a { color: #0000ee; text-decoration: underline; } @media (max-width: 480px) { #u_content_heading_2 .v-container-padding-padding { padding: 40px 10px 0px !important; } #u_content_heading_2 .v-font-size { font-size: 28px !important; } #u_content_heading_3 .v-container-padding-padding { padding: 40px 10px 0px !important; } #u_content_heading_3 .v-font-size { font-size: 22px !important; } #u_content_text_2 .v-container-padding-padding { padding: 5px 10px 10px !important; } #u_content_button_2 .v-size-width { width: 65% !important; } #u_content_text_1 .v-container-padding-padding { padding: 10px 10px 40px !important; } #u_content_heading_6 .v-text-align { text-align: center !important; } #u_content_button_4 .v-container-padding-padding { padding: 10px 10px 40px !important; } #u_content_button_4 .v-size-width { width: 65% !important; } #u_content_button_4 .v-text-align { text-align: center !important; } #u_content_heading_7 .v-text-align { text-align: center !important; } #u_content_button_5 .v-container-padding-padding { padding: 10px 10px 40px !important; } #u_content_button_5 .v-size-width { width: 65% !important; } #u_content_button_5 .v-text-align { text-align: center !important; } #u_content_heading_4 .v-text-align { text-align: center !important; } #u_content_button_3 .v-container-padding-padding { padding: 10px 10px 40px !important; } #u_content_button_3 .v-size-width { width: 65% !important; } #u_content_button_3 .v-text-align { text-align: center !important; } #u_content_heading_5 .v-container-padding-padding { padding: 40px 10px 10px !important; } #u_content_heading_5 .v-font-size { font-size: 20px !important; } #u_content_button_1 .v-container-padding-padding { padding: 10px 10px 40px !important; } #u_content_button_1 .v-size-width { width: 65% !important; } #u_content_heading_8 .v-container-padding-padding { padding: 40px 10px 20px !important; } #u_content_text_6 .v-container-padding-padding { padding: 10px 10px 40px !important; } #u_content_text_5 .v-container-padding-padding { padding: 10px 10px 40px !important; } #u_content_heading_13 .v-container-padding-padding { padding: 40px 10px 0px !important; } #u_content_heading_13 .v-font-size { font-size: 24px !important; } #u_content_text_4 .v-container-padding-padding { padding: 5px 10px 10px !important; } #u_content_button_6 .v-container-padding-padding { padding: 10px 10px 40px !important; } #u_content_button_6 .v-size-width { width: 65% !important; } #u_content_social_2 .v-container-padding-padding { padding: 40px 10px 10px !important; } #u_content_text_deprecated_2 .v-container-padding-padding { padding: 10px 10px 20px !important; } #u_content_image_8 .v-container-padding-padding { padding: 20px 10px 40px !important; } }
        </style>
  
  
  
  <link href="https://fonts.googleapis.com/css?family=Raleway:400,700&display=swap" rel="stylesheet" type="text/css"><link href="https://fonts.googleapis.com/css?family=Playfair+Display:400,700&display=swap" rel="stylesheet" type="text/css">
  
</head>

<body class="clean-body u_body" style="margin: 0;padding: 0;-webkit-text-size-adjust: 100%;background-color: #000000;color: #000000">
  
    
      <table id="u_body" style="border-collapse: collapse;table-layout: fixed;border-spacing: 0;mso-table-lspace: 0pt;mso-table-rspace: 0pt;vertical-align: top;min-width: 320px;Margin: 0 auto;background-color: #000000;width:100%" cellpadding="0" cellspacing="0">
        <tbody>
          <tr style="vertical-align: top">
            <td style="word-break: break-word;border-collapse: collapse !important;vertical-align: top">
                
                
                <div class="u-row-container" style="padding: 0px;background-color: transparent">
                  <div class="u-row" style="Margin: 0 auto;min-width: 320px;max-width: 600px;overflow-wrap: break-word;word-wrap: break-word;word-break: break-word;background-color: transparent;">
                    <div style="border-collapse: collapse;display: table;width: 100%;height: 100%;background-color: transparent;">
                      
                        
                        
                          <div class="u-col u-col-100" style="max-width: 320px;min-width: 600px;display: table-cell;vertical-align: top;">
                            <div style="background-color: #f9e5df;height: 100%;width: 100% !important;">
                              <div style="box-sizing: border-box; height: 100%; padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;">
                                
                                <table id="u_content_heading_2" style="font-family:'Raleway',sans-serif;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
                                  <tbody>
                                    <tr>
                                      <td class="v-container-padding-padding" style="overflow-wrap:break-word;word-break:break-word;padding:60px 10px 0px;font-family:'Raleway',sans-serif;" align="left">
                                        
                                        <h1 class="v-text-align v-font-size" style="margin: 0px; color: #000000; line-height: 120%; text-align: center; word-wrap: break-word; font-family: 'Playfair Display',serif; font-size: 35px; "><strong>LibLAW</strong><br /></h1>
                                        <br>
                                        <h2 style="margin: 0px; color: #000000; line-height: 120%; text-align: center; word-wrap: break-word; font-family: 'Playfair Display',serif; "><strong>Reading Target</strong></h2>
                                        
                                        
                                      </td>
                                    </tr>
                                  </tbody>
                                </table>
                                
                                <table style="font-family:'Raleway',sans-serif;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
                                  <tbody>
                                    <tr>
                                      <td class="v-container-padding-padding" style="overflow-wrap:break-word;word-break:break-word;padding:30px 10px 0px;font-family:'Raleway',sans-serif;" align="left">
                                        
                                      </td>
                                    </tr>
                                  </tbody>
                                </table>
                                
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                      
                      
                      
                      <div class="u-row-container" style="padding: 0px;background-color: transparent">
                        <div class="u-row" style="Margin: 0 auto;min-width: 320px;max-width: 600px;overflow-wrap: break-word;word-wrap: break-word;word-break: break-word;background-color: transparent;">
                          <div style="border-collapse: collapse;display: table;width: 100%;height: 100%;background-color: transparent;">
                            
                              
                        
                                <div class="u-col u-col-100" style="max-width: 320px;min-width: 600px;display: table-cell;vertical-align: top;">
                                  <div style="height: 100%;width: 100% !important;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;">
                                    <div style="box-sizing: border-box; height: 100%; padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;">
                                      
                                      <table id="u_content_button_2" style="font-family:'Raleway',sans-serif;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
                                        <tbody>
                                          <tr>
                                            <td class="v-container-padding-padding" style="overflow-wrap:break-word;word-break:break-word;padding:10px;font-family:'Raleway',sans-serif;" align="left">
                                            </td>
                                          </tr>
                                        </tbody>
                                      </table>
                                      
                                      </div>
                                    </div>
                                  </div>
                                </div>
                              </div>
                            </div>
                            
                            
                            
                            <div class="u-row-container" style="padding: 0px;background-color: transparent">
                              <div class="u-row" style="Margin: 0 auto;min-width: 320px;max-width: 600px;overflow-wrap: break-word;word-wrap: break-word;word-break: break-word;background-color: transparent;">
                                <div style="border-collapse: collapse;display: table;width: 100%;height: 100%;background-color: transparent;">
                                  
                                    
                              
                                      <div class="u-col u-col-100" style="max-width: 320px;min-width: 600px;display: table-cell;vertical-align: top;">
                                        <div style="height: 100%;width: 100% !important;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;">
                                          <div style="box-sizing: border-box; height: 100%; padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;">
                                            
                                            </div>
                                          </div>
                                        </div>
                                      </div>
                                    </div>
                                  </div>
                                  
                                  
                                  
                                  <div class="u-row-container" style="padding: 0px;background-color: transparent">
                                    <div class="u-row" style="Margin: 0 auto;min-width: 320px;max-width: 600px;overflow-wrap: break-word;word-wrap: break-word;word-break: break-word;background-color: transparent;">
                                        <div style="border-collapse: collapse;display: table;width: 100%;height: 100%;background-color: transparent;">
                                            <div class="u-col u-col-50" style="max-width: 320px;min-width: 300px;display: table-cell;vertical-align: top;">
                                                <div style="height: 100%;width: 100% !important;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;">      
                                                    <table style="font-family:'Raleway',sans-serif;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
                                                    <tbody>
                                                        <tr>
                                                        <td class="v-container-padding-padding" style="overflow-wrap:break-word;word-break:break-word;padding:5px;font-family:'Raleway',sans-serif;" align="left">
                                                            
                                                            <table width="100%" cellpadding="0" cellspacing="0" border="0">
                                                            <tr>
                                                                <td class="v-text-align" style="padding-right: 0px;padding-left: 0px;" align="center">
                                                                <!-- INI BAGIAN BUKU -->
                                                                <img align="center" border="0" src=" """+ buku['image_url_m']+""" " alt="image" title="image" style="outline: none;text-decoration: none;-ms-interpolation-mode: bicubic;clear: both;display: inline-block !important;border: none;height: auto;float: none;width: 100%;max-width: 290px;" width="290"/>
                                                                
                                                                </td>
                                                            </tr>
                                                            </table>
                                                            
                                                        </td>
                                                        </tr>
                                                    </tbody>
                                                    </table>
                                                    
                                                    <table id="u_content_heading_6" style="font-family:'Raleway',sans-serif;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
                                                    <tbody>
                                                        <tr>
                                                        <td class="v-container-padding-padding" style="overflow-wrap:break-word;word-break:break-word;padding:10px;font-family:'Raleway',sans-serif;" align="left">
                                                            
                                                            <h2 class="v-text-align v-font-size" style="margin: 0px; line-height: 140%; text-align: center; word-wrap: break-word; font-size: 18px; color: white;">"""+ buku['author'] +"""</h2>
                                                            <h1 style="margin: 0px; line-height: 140%; text-align: center; word-wrap: break-word; color: white;">"""+ buku['title']+"""</h1>
                                                            <br>
                                                            <h2 class="v-text-align v-font-size" style="margin: 0px; line-height: 140%; text-align: center; word-wrap: break-word; font-size: 18px; color: white;">Mulai Membaca:""" + str(mulai)+ """</h2>
                                                            <h2 class="v-text-align v-font-size" style="margin: 0px; line-height: 140%; text-align: center; word-wrap: break-word; font-size: 18px; color: white;">Target Selesai:""" + str(selesai) + """</h2>
                                                            <h2 class="v-text-align v-font-size" style="margin: 0px; line-height: 140%; text-align: center; word-wrap: break-word; font-size: 18px; color: white;">Sisa Waktu: """ + str(sisawaktu.days) + """ Hari</h2>
                                                        </td>
                                                        </tr>
                                                    </tbody>
                                                    </table>
                                                    
                                                    <table id="u_content_button_4" style="font-family:'Raleway',sans-serif;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
                                                    <tbody>
                                                        <tr>
                                                        <td class="v-container-padding-padding" style="overflow-wrap:break-word;word-break:break-word;padding:10px;font-family:'Raleway',sans-serif;" align="left">
                                                        
                                                            <div class="v-text-align" align="center">
                                                                <a href=" " target="_blank" class="v-button v-size-width v-font-size" style="box-sizing: border-box;display: inline-block;font-family:'Raleway',sans-serif;text-decoration: none;-webkit-text-size-adjust: none;text-align: center;color: #FFFFFF; background-color:blue; border-radius: 4px;-webkit-border-radius: 4px; -moz-border-radius: 4px; width:60%; max-width:100%; overflow-wrap: break-word; word-break: break-word; word-wrap:break-word; mso-border-alt: none;font-size: 14px;">
                                                                <span style="display:block;padding:10px 20px;line-height:120%;"><span style="line-height: 16.8px;color:white;">Open LibLAW website</span></span>
                                                                </a>
                                                            </div>
                                                            
                                                            </td>
                                                        </tr>
                                                        </tbody>
                                                    </table>
                                                    </div>
                                                </div>
                                                </div>
                                                <hr style="border-top: 1px solid white">
                                            </div>
                                        </div>                                                      
                                  </td>
                                </tr>
                              </tbody>
                            </table>
                          </body>
                                                        
                      </html>

   """
    
    return html

def get_html(buku, mulai, selesai):
    sisawaktu =  selesai - mulai
    html = """

    <!DOCTYPE HTML PUBLIC "-//W3C//DTD XHTML 1.0 Transitional //EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">
  <head>
      <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <meta name="x-apple-disable-message-reformatting">
      <meta http-equiv="X-UA-Compatible" content="IE=edge">
      <title></title>
      
      <style type="text/css">
        @media only screen and (min-width: 620px) {
          .u-row {
            width: 600px !important;
          }
          .u-row .u-col {
            vertical-align: top;
          }
          
          .u-row .u-col-50 {
            width: 300px !important;
          }
          
          .u-row .u-col-100 {
            width: 600px !important;
          }
          
        }
        
        @media (max-width: 620px) {
          .u-row-container {
            max-width: 100% !important;
            padding-left: 0px !important;
            padding-right: 0px !important;
          }
          .u-row .u-col {
            min-width: 320px !important;
            max-width: 100% !important;
            display: block !important;
          }
          .u-row {
            width: 100% !important;
          }
          .u-col {
            width: 100% !important;
          }
          .u-col > div {
            margin: 0 auto;
          }
        }
        body {
          margin: 0;
          padding: 0;
          font-family:'Poppins', sans-serif;
          background-color: black;
        }
        
        table,
        tr,
        td {
          vertical-align: top;
          border-collapse: collapse;
        }
        
        p {
          margin: 0;
        }
        
        .ie-container table,
        .mso-container table {
          table-layout: fixed;
        }
        
        * {
          line-height: inherit;
        }
        
        a[x-apple-data-detectors='true'] {
          color: inherit !important;
          text-decoration: none !important;
        }
        
        table, td { color: #000000; } #u_body a { color: #0000ee; text-decoration: underline; } @media (max-width: 480px) { #u_content_heading_2 .v-container-padding-padding { padding: 40px 10px 0px !important; } #u_content_heading_2 .v-font-size { font-size: 28px !important; } #u_content_heading_3 .v-container-padding-padding { padding: 40px 10px 0px !important; } #u_content_heading_3 .v-font-size { font-size: 22px !important; } #u_content_text_2 .v-container-padding-padding { padding: 5px 10px 10px !important; } #u_content_button_2 .v-size-width { width: 65% !important; } #u_content_text_1 .v-container-padding-padding { padding: 10px 10px 40px !important; } #u_content_heading_6 .v-text-align { text-align: center !important; } #u_content_button_4 .v-container-padding-padding { padding: 10px 10px 40px !important; } #u_content_button_4 .v-size-width { width: 65% !important; } #u_content_button_4 .v-text-align { text-align: center !important; } #u_content_heading_7 .v-text-align { text-align: center !important; } #u_content_button_5 .v-container-padding-padding { padding: 10px 10px 40px !important; } #u_content_button_5 .v-size-width { width: 65% !important; } #u_content_button_5 .v-text-align { text-align: center !important; } #u_content_heading_4 .v-text-align { text-align: center !important; } #u_content_button_3 .v-container-padding-padding { padding: 10px 10px 40px !important; } #u_content_button_3 .v-size-width { width: 65% !important; } #u_content_button_3 .v-text-align { text-align: center !important; } #u_content_heading_5 .v-container-padding-padding { padding: 40px 10px 10px !important; } #u_content_heading_5 .v-font-size { font-size: 20px !important; } #u_content_button_1 .v-container-padding-padding { padding: 10px 10px 40px !important; } #u_content_button_1 .v-size-width { width: 65% !important; } #u_content_heading_8 .v-container-padding-padding { padding: 40px 10px 20px !important; } #u_content_text_6 .v-container-padding-padding { padding: 10px 10px 40px !important; } #u_content_text_5 .v-container-padding-padding { padding: 10px 10px 40px !important; } #u_content_heading_13 .v-container-padding-padding { padding: 40px 10px 0px !important; } #u_content_heading_13 .v-font-size { font-size: 24px !important; } #u_content_text_4 .v-container-padding-padding { padding: 5px 10px 10px !important; } #u_content_button_6 .v-container-padding-padding { padding: 10px 10px 40px !important; } #u_content_button_6 .v-size-width { width: 65% !important; } #u_content_social_2 .v-container-padding-padding { padding: 40px 10px 10px !important; } #u_content_text_deprecated_2 .v-container-padding-padding { padding: 10px 10px 20px !important; } #u_content_image_8 .v-container-padding-padding { padding: 20px 10px 40px !important; } }
        </style>
  
  
  
  <link href="https://fonts.googleapis.com/css?family=Raleway:400,700&display=swap" rel="stylesheet" type="text/css"><link href="https://fonts.googleapis.com/css?family=Playfair+Display:400,700&display=swap" rel="stylesheet" type="text/css">
  
</head>

<body class="clean-body u_body" style="margin: 0;padding: 0;-webkit-text-size-adjust: 100%;background-color: #000000;color: #000000">
  
    
      <table id="u_body" style="border-collapse: collapse;table-layout: fixed;border-spacing: 0;mso-table-lspace: 0pt;mso-table-rspace: 0pt;vertical-align: top;min-width: 320px;Margin: 0 auto;background-color: #000000;width:100%" cellpadding="0" cellspacing="0">
        <tbody>
          <tr style="vertical-align: top">
            <td style="word-break: break-word;border-collapse: collapse !important;vertical-align: top">
                
                
                <div class="u-row-container" style="padding: 0px;background-color: transparent">
                  <div class="u-row" style="Margin: 0 auto;min-width: 320px;max-width: 600px;overflow-wrap: break-word;word-wrap: break-word;word-break: break-word;background-color: transparent;">
                    <div style="border-collapse: collapse;display: table;width: 100%;height: 100%;background-color: transparent;">
                      
                        
                        
                          <div class="u-col u-col-100" style="max-width: 320px;min-width: 600px;display: table-cell;vertical-align: top;">
                            <div style="background-color: #f9e5df;height: 100%;width: 100% !important;">
                              <div style="box-sizing: border-box; height: 100%; padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;">
                                
                                <table id="u_content_heading_2" style="font-family:'Raleway',sans-serif;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
                                  <tbody>
                                    <tr>
                                      <td class="v-container-padding-padding" style="overflow-wrap:break-word;word-break:break-word;padding:60px 10px 0px;font-family:'Raleway',sans-serif;" align="left">
                                        
                                        <h1 class="v-text-align v-font-size" style="margin: 0px; color: #000000; line-height: 120%; text-align: center; word-wrap: break-word; font-family: 'Playfair Display',serif; font-size: 35px; "><strong>LibLAW</strong><br /></h1>
                                        <br>
                                        <h2 style="margin: 0px; color: #000000; line-height: 120%; text-align: center; word-wrap: break-word; font-family: 'Playfair Display',serif; "><strong>This is your reading reminder!</strong></h2>
                                        
                                        
                                      </td>
                                    </tr>
                                  </tbody>
                                </table>
                                
                                <table style="font-family:'Raleway',sans-serif;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
                                  <tbody>
                                    <tr>
                                      <td class="v-container-padding-padding" style="overflow-wrap:break-word;word-break:break-word;padding:30px 10px 0px;font-family:'Raleway',sans-serif;" align="left">
                                        
                                      </td>
                                    </tr>
                                  </tbody>
                                </table>
                                
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                      
                      
                      
                      <div class="u-row-container" style="padding: 0px;background-color: transparent">
                        <div class="u-row" style="Margin: 0 auto;min-width: 320px;max-width: 600px;overflow-wrap: break-word;word-wrap: break-word;word-break: break-word;background-color: transparent;">
                          <div style="border-collapse: collapse;display: table;width: 100%;height: 100%;background-color: transparent;">
                            
                              
                        
                                <div class="u-col u-col-100" style="max-width: 320px;min-width: 600px;display: table-cell;vertical-align: top;">
                                  <div style="height: 100%;width: 100% !important;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;">
                                    <div style="box-sizing: border-box; height: 100%; padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;">
                                      
                                      <table id="u_content_button_2" style="font-family:'Raleway',sans-serif;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
                                        <tbody>
                                          <tr>
                                            <td class="v-container-padding-padding" style="overflow-wrap:break-word;word-break:break-word;padding:10px;font-family:'Raleway',sans-serif;" align="left">
                                            </td>
                                          </tr>
                                        </tbody>
                                      </table>
                                      
                                      </div>
                                    </div>
                                  </div>
                                </div>
                              </div>
                            </div>
                            
                            
                            
                            <div class="u-row-container" style="padding: 0px;background-color: transparent">
                              <div class="u-row" style="Margin: 0 auto;min-width: 320px;max-width: 600px;overflow-wrap: break-word;word-wrap: break-word;word-break: break-word;background-color: transparent;">
                                <div style="border-collapse: collapse;display: table;width: 100%;height: 100%;background-color: transparent;">
                                  
                                    
                              
                                      <div class="u-col u-col-100" style="max-width: 320px;min-width: 600px;display: table-cell;vertical-align: top;">
                                        <div style="height: 100%;width: 100% !important;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;">
                                          <div style="box-sizing: border-box; height: 100%; padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;">
                                            
                                            </div>
                                          </div>
                                        </div>
                                      </div>
                                    </div>
                                  </div>
                                  
                                  
                                  
                                  <div class="u-row-container" style="padding: 0px;background-color: transparent">
                                    <div class="u-row" style="Margin: 0 auto;min-width: 320px;max-width: 600px;overflow-wrap: break-word;word-wrap: break-word;word-break: break-word;background-color: transparent;">
                                        <div style="border-collapse: collapse;display: table;width: 100%;height: 100%;background-color: transparent;">
                                            <div class="u-col u-col-50" style="max-width: 320px;min-width: 300px;display: table-cell;vertical-align: top;">
                                                <div style="height: 100%;width: 100% !important;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;">      
                                                    <table style="font-family:'Raleway',sans-serif;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
                                                    <tbody>
                                                        <tr>
                                                        <td class="v-container-padding-padding" style="overflow-wrap:break-word;word-break:break-word;padding:5px;font-family:'Raleway',sans-serif;" align="left">
                                                            
                                                            <table width="100%" cellpadding="0" cellspacing="0" border="0">
                                                            <tr>
                                                                <td class="v-text-align" style="padding-right: 0px;padding-left: 0px;" align="center">
                                                                <!-- INI BAGIAN BUKU -->
                                                                <img align="center" border="0" src=" """+ buku['image_url_m']+""" " alt="image" title="image" style="outline: none;text-decoration: none;-ms-interpolation-mode: bicubic;clear: both;display: inline-block !important;border: none;height: auto;float: none;width: 100%;max-width: 290px;" width="290"/>
                                                                
                                                                </td>
                                                            </tr>
                                                            </table>
                                                            
                                                        </td>
                                                        </tr>
                                                    </tbody>
                                                    </table>
                                                    
                                                    <table id="u_content_heading_6" style="font-family:'Raleway',sans-serif;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
                                                    <tbody>
                                                        <tr>
                                                        <td class="v-container-padding-padding" style="overflow-wrap:break-word;word-break:break-word;padding:10px;font-family:'Raleway',sans-serif;" align="left">
                                                            
                                                            <h2 class="v-text-align v-font-size" style="margin: 0px; line-height: 140%; text-align: center; word-wrap: break-word; font-size: 18px; color: white;">"""+ buku['author'] +"""</h2>
                                                            <h1 style="margin: 0px; line-height: 140%; text-align: center; word-wrap: break-word; color: white;">"""+ buku['title']+"""</h1>
                                                            <br>
                                                            <h2 class="v-text-align v-font-size" style="margin: 0px; line-height: 140%; text-align: center; word-wrap: break-word; font-size: 18px; color: white;">Mulai Membaca:""" + str(mulai)+ """</h2>
                                                            <h2 class="v-text-align v-font-size" style="margin: 0px; line-height: 140%; text-align: center; word-wrap: break-word; font-size: 18px; color: white;">Target Selesai:""" + str(selesai) + """</h2>
                                                            <h2 class="v-text-align v-font-size" style="margin: 0px; line-height: 140%; text-align: center; word-wrap: break-word; font-size: 18px; color: white;">Sisa Waktu: """ + str(sisawaktu.days) + """ Hari</h2>
                                                        </td>
                                                        </tr>
                                                    </tbody>
                                                    </table>
                                                    
                                                    <table id="u_content_button_4" style="font-family:'Raleway',sans-serif;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
                                                    <tbody>
                                                        <tr>
                                                        <td class="v-container-padding-padding" style="overflow-wrap:break-word;word-break:break-word;padding:10px;font-family:'Raleway',sans-serif;" align="left">
                                                        
                                                            <div class="v-text-align" align="center">
                                                                <a href=" " target="_blank" class="v-button v-size-width v-font-size" style="box-sizing: border-box;display: inline-block;font-family:'Raleway',sans-serif;text-decoration: none;-webkit-text-size-adjust: none;text-align: center;color: #FFFFFF; background-color:blue; border-radius: 4px;-webkit-border-radius: 4px; -moz-border-radius: 4px; width:60%; max-width:100%; overflow-wrap: break-word; word-break: break-word; word-wrap:break-word; mso-border-alt: none;font-size: 14px;">
                                                                <span style="display:block;padding:10px 20px;line-height:120%;"><span style="line-height: 16.8px;color:white;">Open LibLAW website</span></span>
                                                                </a>
                                                            </div>
                                                            
                                                            </td>
                                                        </tr>
                                                        </tbody>
                                                    </table>
                                                    </div>
                                                </div>
                                                </div>
                                                <hr style="border-top: 1px solid white">
                                            </div>
                                        </div>                                                      
                                  </td>
                                </tr>
                              </tbody>
                            </table>
                          </body>
                                                        
                      </html>

   """
    
    return html
