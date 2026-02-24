#endpoint of a signup
from flask import *
import pymysql
import pymysql.cursors
from flask_cors import CORS
import os # it allows python code to talk/communicte with the operating system
#create flask app
app = Flask(__name__)
CORS(app)#allows request from external origins
#configure our upload folder
app.config['UPLOAD_FOLDER'] = 'static/images'
@app.route('/api/signup',methods=['POST'])
def signup():
    #extract values posted by the user request
    username= request.form['username']
    email= request.form['email']
    password= request.form['password']
    phone= request.form['phone']
    #connection Database
    connection = pymysql.connect(host='localhost',user='root',password='',database='dailyyogurts_swala')
    #create a cursor to initialize the connection
    cursor= connection.cursor()
    #write sql query
    sql='INSERT INTO users(username,email,password,phone)values(%s,%s,%s,%s)'
    #prepare data to replace the place holders
    data=(username,email,password,phone)
    #execute the data and the sql using the cursor
    cursor.execute(sql,data)
    #commit/save chages to the database
    connection.commit()
    return jsonify({'success':'thank you for joining'})
    # add products

    # Define the Add Product Route/Endpoint
@app.route('/api/add_product', methods=['POST'])
def add_product():
        # Extract POST Data
        product_name = request.form['product_name']
        product_description = request.form['product_description']
        product_cost = request.form['product_cost']
        # Extract image data
        photo = request.files['product_photo']
        # Get the image file name
        filename = photo.filename
        # Specify computer path where the image will be saved (in static Folder)
        photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        # Save your image to that path specified above
        photo.save(photo_path)

        # Connect to DB
        connection = pymysql.connect(host='localhost', user='root',
                                        password='',database='dailyyogurts_swala')
        # Create a cursor, initialize connection 
        cursor = connection.cursor()
        # Do Insert SQL, include placeholders 
        sql = 'INSERT INTO product_details (product_name, product_description, product_cost, product_photo) VALUES (%s, %s, %s, %s)'
        # Prepare data to replace placeholders 
        data = (product_name, product_description, product_cost,  filename)
        # using cursor execute sql, providing values in place of placeholders
        cursor.execute(sql, data)

        # Commit the changes to the database
        connection.commit()
        # Return success message in Dictionary Format
        return jsonify({"success": "Product details added successfully"})

# get products
# Define the Get Product Details Route/Endpoint
@app.route('/api/get_product_details', methods=['GET'])
def get_product_details():

    # Connect to the database with DictCursor for direct dictionary results
    connection = pymysql.connect(host='localhost', user='root',
                                        password='',database='dailyyogurts_swala')

    # Create a cursor object and fetch all products details from the products_details table
    # pymysql.cursors.DictCursor helps return a Dictionary Format.
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    # DO SELECT SQL.
    sql = 'SELECT * FROM product_details'

    # Use cursor to execute SQL
    cursor.execute(sql)

    # Fetch/Get all records into a Dictionary Format
    product_details = cursor.fetchall()


    # Return the products details directly as a dictionay - JSON
    return jsonify(product_details)

    #sign in route
@app.route('/api/signin')    
def signin():
    #extract post data
    username=request.form['username']
    password=request.form['password']

    #connect to database
    connection = pymysql.connect(host='localhost',user='root',password='',database='dailyyogurts_swala')

    #connect to cursor
    cursor=connection.cursor(pymysql.cursors.DictCursor)

    #sql query
    sql='select * from users where username=%s and password=%s'
    data=(username,password)

    #execute cursor
    cursor.execute(sql,data)
    #check if there were rows found
    count = cursor.rowcount
    if count ==0:
         return jsonify({'message':'log in failed'})
    else:
         #if the cursor has returned a valid user or atleast a row
         user=cursor.fetchone()
         return jsonify({'message':'login successful','user':user})
    #mpesa payments
# Mpesa Payment Route 
import requests
import datetime
import base64
from requests.auth import HTTPBasicAuth

@app.route('/api/mpesa_payment', methods=['POST'])
def mpesa_payment():
    if request.method == 'POST':
        # Extract POST Values sent
        amount = request.form['amount']
        phone = request.form['phone']

        # Provide consumer_key and consumer_secret provided by safaricom
        consumer_key = "GTWADFxIpUfDoNikNGqq1C3023evM6UH"
        consumer_secret = "amFbAoUByPV2rM5A"

        # Authenticate Yourself using above credentials to Safaricom Services, and Bearer Token this is used by safaricom for security identification purposes - Your are given Access
        api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"  # AUTH URL
        # Provide your consumer_key and consumer_secret 
        response = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))
        # Get response as Dictionary
        data = response.json()
        # Retrieve the Provide Token
        # Token allows you to proceed with the transaction
        access_token = "Bearer" + ' ' + data['access_token']

        #  GETTING THE PASSWORD
        timestamp = datetime.datetime.today().strftime('%Y%m%d%H%M%S')  # Current Time
        passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'  # Passkey(Safaricom Provided)
        business_short_code = "174379"  # Test Paybile (Safaricom Provided)
        # Combine above 3 Strings to get data variable
        data = business_short_code + passkey + timestamp
        # Encode to Base64
        encoded = base64.b64encode(data.encode())
        password = encoded.decode()

        # BODY OR PAYLOAD
        payload = {
            "BusinessShortCode": "174379",
            "Password":password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": "1",  # use 1 when testing
            "PartyA": phone,  # change to your number
            "PartyB": "174379",
            "PhoneNumber": phone,
            "CallBackURL": "https://coding.co.ke/api/confirm.php",
            "AccountReference": "SokoGarden Online",
            "TransactionDesc": "Payments for Products"
        }

        # POPULAING THE HTTP HEADER, PROVIDE THE TOKEN ISSUED EARLIER
        headers = {
            "Authorization": access_token,
            "Content-Type": "application/json"
        }

        # Specify STK Push  Trigger URL
        url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"  
        # Create a POST Request to above url, providing headers, payload 
        # Below triggers an STK Push to the phone number indicated in the payload and the amount.
        response = requests.post(url, json=payload, headers=headers)
        print(response.text) # 
        # Give a Response
        return jsonify({"message": "An MPESA Prompt has been sent to Your Phone, Please Check & Complete Payment"})
if __name__ == '__main__':
    app.run(debug=True)