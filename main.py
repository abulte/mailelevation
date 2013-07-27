#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
# Copyright 2013 Alexandre Bulté <alexandre[at]bulte[dot]net>
# 
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
from flask import Flask, request, make_response
from utils import make_profile
from flask_mail import Mail, Message

app = Flask(__name__)
mail = Mail(app)

app.debug = True

app.config.update(
    MAIL_SERVER = 'smtp.mandrillapp.com',
    MAIL_PORT = 465,
    MAIL_USE_SSL = True,
    MAIL_USERNAME = os.getenv('MANDRILL_USERNAME'),
    MAIL_PASSWORD = os.getenv('MANDRILL_APIKEY'),
    MAIL_DEBUG = True
)

print app.config.get('MAIL_SERVER')
print app.config.get('MAIL_PORT')
print app.config.get('MAIL_USERNAME')
print app.config.get('MAIL_PASSWORD')

@app.route('/incoming/email', methods=['POST'])
def mail_receive():
    app.logger.info('-- Received incoming email --')
    app.logger.info(request.form)
    app.logger.info(request.files)
    
    mfrom = request.form.get('envelope[from]', False)
    afile = request.files.get('attachments[0]', False)
    if afile and mfrom:
        resp, status = make_profile(afile)
        if status == 'KO':
            return make_response('Something bad happened : %s' % resp, 500)
        elif status == 'OK':
            msg = Message("Elevation profile", sender='alexandre@bulte.net', 
                recipients=[mfrom], bcc='alexandre@bulte.net')
            msg.body = resp
            mail.send(msg)
    else:
        return make_response('Missing sender or attached file', 400)

    return 'OK'

@app.route('/')
def index():
    return """
<h1>Convert a GPX to an ASCII elevation profile</h1>

<p>Send an email with a GPX attached (max 100ko) to 
<a href="mailto:b29d062265b9b6b211c0@cloudmailin.net">b29d062265b9b6b211c0@cloudmailin.net</a>, 
and you'll receive the elevation profile in reply.</p>

<p>Currently, only tracks (not routes) are processed from GPX file.</p>

<pre>
# Copyright 2013 Alexandre Bulté &lt;alexandre[at]bulte[dot]net&gt;
# 
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
</pre>

<pre>
MIN : 785.56
MAX : 2107.73
TOTAL : 1322.17
POSITIF CUM. : 10853.11
NEGATIF CUM. : -124272.85

One * is 42.1546 meters.

2065                                 **                                                                
2023                                ***                                                                
1981                               ******                                                              
1939                               *******                                                             
1896                              *********                                                            
1854                             ***********                                                           
1812                             ***********                                                           
1770                            *************                                                          
1728                            **************                                                         
1686                           ****************                                                        
1644 **                       ******************                                                       
1601 ****                    ***********************                                                   
1559 *****                  *************************                                                  
1517 *******                **************************                                                 
1475 ********              ****************************                                                
1433 **********          *******************************                                               
1391 ***********        ********************************                                               
1348 ************    ***********************************                                               
1306 ****************************************************                                              
1264 *****************************************************                                             
1222 *****************************************************                                             
1180 ******************************************************                                            
1138 ******************************************************                                            
1096 *******************************************************                                           
1053 ********************************************************                                          
1011 *********************************************************                                       * 
969  **********************************************************                                     ** 
927  ***********************************************************          * **                     *** 
885  *************************************************************    ************                **** 
843  *******************************************************************************              **** 
800  *********************************************************************************   *****  ****** 
758  ************************************************************************************************* 
716  ************************************************************************************************* 
674  ************************************************************************************************* 
632  **************************************************************************************************
590  **************************************************************************************************
548  **************************************************************************************************
505  **************************************************************************************************
463  **************************************************************************************************
421  **************************************************************************************************
379  **************************************************************************************************
337  **************************************************************************************************
295  **************************************************************************************************
252  **************************************************************************************************
210  **************************************************************************************************
168  **************************************************************************************************
126  **************************************************************************************************
84   **************************************************************************************************
42   **************************************************************************************************
0    **************************************************************************************************
</pre>
"""

if __name__ == '__main__':
    app.run()