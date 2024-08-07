# simple flask app
from flask import Flask, render_template, request, url_for,redirect,session,jsonify,send_file
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from datetime import datetime
import pandas as pd
import Query
from io import BytesIO
import xlsxwriter
import os
from dotenv import load_dotenv
from itsdangerous import URLSafeSerializer, SignatureExpired
from flask_mail import Mail, Message
import threading


app = Flask(__name__)
load_dotenv()

app.secret_key = os.getenv('SECRET_KEY')

app.config['MYSQL_HOST']=os.getenv('SQL_HOST')
app.config['MYSQL_USER']=os.getenv('SQL_USER')
app.config['MYSQL_PASSWORD']=os.getenv('SQL_PASSWORD')
app.config['MYSQL_DB']=os.getenv('DATABASE')
app.config['SECURITY_PASSWORD_SALT']=os.getenv('SECURITY_PASSWORD_SALT')
app.config['MAIL_SERVER']=os.getenv('MAILSERVER')
app.config['MAIL_PORT']=587
app.config['MAIL_USERNAME']=os.getenv('EMAIL')
app.config['MAIL_PASSWORD']=os.getenv('EMAIL_PASSWORD')
app.config['MAIL_USE_TLS']=True
app.config['MAIL_USE_SSL']=False

SQl_back=MySQL(app)
sendMail=Mail(app)

encryption=URLSafeSerializer(app.secret_key)


@app.route('/',methods=['GET','POST'])
def index():

    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = SQl_back.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE username = % s AND password = % s', (username, password, ))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['ID']
            session['username'] = account['username']
            return redirect('/home')
        
    return render_template('index.html')

# add more routes

@app.route('/signup', methods=['GET','POST'])
def signup():
    msg=''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form.get('username')
        password = request.form.get('password')
        email= request.form.get('email')

        if username!='' and password!='' and email!='':
            print(username)
            print(password)
            print(email)

            cursor = SQl_back.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM user WHERE username = %s',(username,))
            ActExist=cursor.fetchone()

            if ActExist:
                msg='Account already exists'
            elif not re.match(r'[A-Za-z0-9]+',username):
                msg='Username should contain only numbers and letters'
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                msg = 'Invalid email address !'
            else:
                cursor.execute('INSERT INTO user VALUES (NULL,%s,%s,%s)',(username,password,email,))
                SQl_back.connection.commit()
                return redirect('/')
    
        msg='Please fill out form'
    return render_template('signup.html',msg=msg)



@app.route('/signout')
def signout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    session.pop('password',None)
    return redirect('/')

@app.route('/home',methods=['GET','POST'])
def home():
    if 'loggedin' in session:
        cursor = SQl_back.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT EQUIPID, GROSS, NET, TARE, DATES, TIMES FROM weighout ORDER BY id DESC')
        data=cursor.fetchone()
        cursor.execute('SELECT scale_conn FROM scale_conn ORDER BY id DESC')
        Con=cursor.fetchone()
        Connection=bool(Con['scale_conn'])
        #print(data)
        #print(type(data))
        #print(data['EQUIPID'])
        return render_template('home.html',data=data,Connection=Connection)
    else:
        return redirect('/')

@app.route('/update')
def update():
    cursor = SQl_back.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT EQUIPID, GROSS, NET, TARE, DATES, TIMES FROM weighout ORDER BY id DESC')
    data=cursor.fetchone()
    cursor.execute('SELECT scale_conn FROM scale_conn ORDER BY id DESC')
    Con=cursor.fetchone()
    Connection=bool(Con['scale_conn'])
    print(data)
    print(Connection)

    if data:
        data['DATES']=str(data['DATES'])
        data['TIMES']=str(data['TIMES'])
    
    updates={'SQLD':data,'ConnD':Connection}

    return jsonify(updates)


#add route for audit.html in templates
@app.route('/audit',methods=['GET','POST'])
def audit():
    if 'loggedin' in session:
        data=''
        truckId=''
        startDate=''
        endDate=''
        Material=''

        page=request.args.get('page',1,type=int)
        limit=4
        offset=(page-1)*limit
        searchType='weighout'
        
            #Conditional for if it catches a post method
        if request.method=='POST' or request.method=='GET':

            if request.method=='POST' and'truckId' in request.form and 'startDate' in request.form and 'endDate' in request.form:
                truckId=request.form.get('truckId')
                startDate=request.form.get('startDate')
                endDate=request.form.get('endDate')
                Material=request.form.get('material')
                print(Material)
            else:
                truckId=request.args.get('truckid','')
                startDate=request.args.get('startDate','')
                endDate=request.args.get('endDate','')
                Material=request.form.get('material','')
        
            cursor = SQl_back.connection.cursor(MySQLdb.cursors.DictCursor)
            #When no data has been entered by user
            if not truckId and not startDate and not endDate:
                query=f'SELECT * FROM {searchType} LIMIT %s OFFSET %s'
                cursor.execute(query, (limit,offset,))
                data=cursor.fetchall()
                print(data)
            
            else:
                sql_result,parameters=Query.search_sql(searchType,truckId,startDate,endDate,Material)
                
                if len(parameters)==1:
                    cursor.execute(sql_result,(parameters[0],limit,offset,))
                    data=cursor.fetchall()

                elif len(parameters)==2:
                    cursor.execute(sql_result,(parameters[0],parameters[1],limit,offset,))
                    data=cursor.fetchall()

                elif len(parameters)==3:
                    cursor.execute(sql_result,(parameters[0],parameters[1],parameters[2],limit,offset,))
                    data=cursor.fetchall()
                
                elif len(parameters)==4:
                    cursor.execute(sql_result,( parameters[0],parameters[1],parameters[2],parameters[3],limit,offset,))
                    data=cursor.fetchall()
                
            
            count=len(data)
            print(count)
            total_pages = (count+limit)//limit
            if total_pages>=2:
                total_pages+=1
            print(total_pages)
            
        return render_template('audit.html',data=data,page=page,rowPage=limit,total_pages=total_pages,searchType=searchType)
    else:
        return redirect('/')

#add route for audit.html in templates
@app.route('/audit/weighin',methods=['GET','POST'])
def audit_weighin():
    if 'loggedin' in session:
        data=''
        truckId=''
        startDate=''
        endDate=''

        page=request.args.get('page',1,type=int)
        limit=4
        offset=(page-1)*limit
        searchType="weighin"
        
            #Conditional for if it catches a post method
        if request.method=='POST' or request.method=='GET':

            if request.method=='POST' and'truckId' in request.form and 'startDate' in request.form and 'endDate' in request.form:
                truckId=request.form.get('truckId')
                startDate=request.form.get('startDate')
                endDate=request.form.get('endDate')
                Material=request.form.get('material')
            else:
                truckId=request.args.get('truckid','')
                startDate=request.args.get('startDate','')
                endDate=request.args.get('endDate','')
                Material=request.args.get('material','')
        
            cursor = SQl_back.connection.cursor(MySQLdb.cursors.DictCursor)
            #When no data has been entered by user
            if not truckId and not startDate and not endDate and not Material:
                query=f'SELECT * FROM {searchType} LIMIT %s OFFSET %s'
                cursor.execute(query, (limit,offset,))
                data=cursor.fetchall()
                print(data)
            
            else:
                sql_result,parameters=Query.search_sql(searchType,truckId,startDate,endDate,Material)
                
                if len(parameters)==1:
                    cursor.execute(sql_result,(parameters[0],limit,offset,))
                    data=cursor.fetchall()

                elif len(parameters)==2:
                    cursor.execute(sql_result,(parameters[0],parameters[1],limit,offset,))
                    data=cursor.fetchall()

                elif len(parameters)==3:
                    cursor.execute(sql_result,( parameters[0],parameters[1],parameters[2],limit,offset,))
                    data=cursor.fetchall()
                
                elif len(parameters)==4:
                    cursor.execute(sql_result,( parameters[0],parameters[1],parameters[2],parameters[3],limit,offset,))
                    data=cursor.fetchall()
                
            
            count=len(data)
            print(count)
            total_pages = (count+limit)//limit
            if total_pages>=2:
                total_pages+=1
            print(total_pages)
            
        return render_template('audit_weighin.html',data=data,page=page,rowPage=limit,total_pages=total_pages,searchType=searchType)
    else:
        return redirect('/')

@app.route('/audit/trend', methods=['GET','POST'])
def trends():
    if 'loggedin' in session:
        material=''
        truckId=''
        startDate=''
        endDate=''
        if request.method=='POST':
            truckId=request.form.get('truckId')
            startDate=request.form.get('startDate')
            endDate=request.form.get('endDate')
            material=request.form.get('material')

            print(truckId)
            print(startDate)
            print(endDate)
            print(material)
            
            if truckId=='' and material==None and endDate=='' and startDate=='':
                return render_template('Trends.html',Gmode=0)
            else:
                tripCount=[]
                matSum=[]
                cursor = SQl_back.connection.cursor(MySQLdb.cursors.DictCursor)

                mode,query,params,setDate= Query.graph_sql(truckId,material,startDate,endDate)

                match mode:
                    case 1:
                        tripQ=query[0]
                        matQ=query[1]
                        xAxis=setDate.tolist()
                        for date in setDate:
                            cursor.execute(tripQ,(params[0],params[1],date,))
                            tripData=cursor.fetchone()
                            tripCount.append(tripData['COUNT(EQUIPID)'])
                            print(tripCount)
                            cursor.execute(matQ,(params[0],params[1],date,))
                            matData=cursor.fetchone()

                            if matData['SUM(NET)']==None:
                                matData=0
                                matSum.append(matData)
                                print(matSum)
                            else:
                                matSum.append(matData['SUM(NET)'])
                                print(matSum)
                        
                        #Graph parameters
                        Labels=[' TripsCompleted per Dates','Material Used per Dates'] # Graph label

                        Data={
                            'xAxis':xAxis,
                            'label1':Labels[0],
                            'label2':Labels[1],
                            'trip':tripCount,
                            'mat':matSum
                        }
                        
                        

                        return render_template('Trends.html',Gmode=mode,gData=Data)
                    
                    case 2:
                        tripQ=query[0]
                        xAxis=setDate.tolist()
                        print(xAxis)

                        for date in setDate:
                            cursor.execute(tripQ,(params[0],date,))
                            tripData=cursor.fetchone()
                            tripCount.append(tripData['COUNT(EQUIPID)'])
                        
                        

                        Labels='Trips Completed per Dates'

                        Data={
                            'xAxis':xAxis,
                            'label1':Labels,
                            'trip':tripCount,
                        }

                        

                        return render_template('Trends.html',Gmode=mode,gData=Data)
                    
                    case 3:
                        matQ=query[0]
                        xAxis=setDate.tolist()

                        for date in setDate:
                            cursor.execute(matQ,(params[0],date,))
                            matData=cursor.fetchone()
                            if matData['SUM(NET)']==None:
                                matData=0
                                matSum.append(matData)
                                print(matSum)
                            else:
                                matSum.append(matData['SUM(NET)'])
                                print(matSum)
                            

                        Labels='Material used per Dates'

                        Data={
                            'xAxis':xAxis,
                            'label1':Labels,
                            'mat':matSum,
                        }
        

                        return render_template('Trends.html',Gmode=mode,gData=Data)
                    
                    case 4:
                        print('Working')
                        tripQ=query[0]
                        xAxis=[setDate]
                        cursor.execute(tripQ,(params[0],setDate,))
                        tripData=cursor.fetchone()
                        print(tripData)
                        tripCount.append(tripData['COUNT(EQUIPID)'])

                        Labels='Trips Completed per Date'

                        Data={
                            'xAxis':xAxis,
                            'label1':Labels,
                            'trip':tripCount,
                        }

                        return render_template('Trends.html',Gmode=mode,gData=Data)
                    

                    case 5:
                        print('Mode 5 WORKING')
                        matQ=query[0]
                        xAxis=[setDate]
                        cursor.execute(matQ,(params[0],setDate,))
                        matData=cursor.fetchone()
                        matSum.append(matData['SUM(NET)'])
                        print(matSum)
                        Labels='Material sent per Date'

                        Data={
                            'xAxis':xAxis,
                            'label1':Labels,
                            'mat':matSum,
                        }

                        return render_template('Trends.html',Gmode=mode,gData=Data)

        return render_template('Trends.html',Gmode=0)
    else:
        return redirect('/')

@app.route('/print_excel',methods=['GET','POST'])
def print_excel():

    if request.method=='GET':
        truckId=request.args.get('truckid','')
        startDate=request.args.get('startDate','')
        endDate=request.args.get('endDate','')
        searchType=request.args.get('type','')
        Material=request.args.get('material','')
        
        cursor = SQl_back.connection.cursor(MySQLdb.cursors.DictCursor)
        #When no data has been entered by user
        if not truckId and not startDate and not endDate:
            query=f'SELECT * FROM {searchType}'
            cursor.execute(query)
            data=cursor.fetchall()
            print(data)
        
        else:
            sql_result,parameters=Query.search_sql(searchType,truckId,startDate,endDate,Material)
            
            if len(parameters)==1:
                cursor.execute(sql_result,(parameters[0],))
                data=cursor.fetchall()

            elif len(parameters)==2:
                cursor.execute(sql_result,(parameters[0],parameters[1],))
                data=cursor.fetchall()

            elif len(parameters)==3:
                cursor.execute(sql_result,(parameters[0],parameters[1],parameters[2],))
                data=cursor.fetchall()

            elif len(parameters)==4:
                cursor.execute(sql_result,( parameters[0],parameters[1],parameters[2],parameters[3],))
                data=cursor.fetchall()
        
        df=pd.DataFrame(data)
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Audit.xlsx')
            writer.close()
        output.seek(0)
    
    return send_file(output, as_attachment=True,download_name='Audit.xlsx',mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    

@app.route('/log',methods=['GET','POST'])
def log():
    if 'loggedin' in session:
        return render_template('log.html')
    else:
        return redirect('/')


@app.route('/reset',methods=['GET','POST'])
def reset():

    def sendEmail(DB_email):
            if DB_email==email:
                print('successful')
                token=encryption.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])
                resetLink=url_for('passwordChange',token=token, _external=True)
                msg=Message('Request for Password Change', sender=os.getenv('EMAIL'),recipients=[email])
                msg.body=f'Use this link to reset your password {resetLink}'
                sendMail.send(msg)

            
    text=''
    if request.method=='POST' and 'email' in request.form and 'username' in request.form:
        email=request.form.get('email')
        name= request.form.get('username')

        if name!='' and email!='':
            cursor = SQl_back.connection.cursor(MySQLdb.cursors.DictCursor)
            DB_email=''
            cursor.execute('SELECT email FROM  user WHERE username=%s',(name,))
            data=cursor.fetchone()
            print(data)
            if data==None:
                text='Invalid username and email, try creating an account or speak to the administrator'
            
            else:
                DB_email=data.get('email')
                thread=threading.thread(target=lambda: sendEmail(DB_email))
                thread.start()
                text='If succcesful please check your email for reset link. Contact administrator if neccessary'

            
        
    
    return render_template('reset.html',msg=text)

@app.route('/reset/<token>', methods=['GET', 'POST'])
def passwordChange(token):
    text=''
    try:
        sentEmail=encryption.loads(token,salt=app.config['SECURITY_PASSWORD_SALT'],max_age=3600)
    except SignatureExpired:
        text=' Time to reset password has elasped try again'
    
    if request.method=='POST':
        newPassword=request.form.get('New Password')
        cursor = SQl_back.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('UPDATE user SET password = %s WHERE email = %s', (newPassword, sentEmail))
        SQl_back.connection.commit()
        return redirect('/')

    
    return render_template('reset_token.html', token=token, msg=text)
    
# run the app

if __name__ == '__main__':
    app.run()