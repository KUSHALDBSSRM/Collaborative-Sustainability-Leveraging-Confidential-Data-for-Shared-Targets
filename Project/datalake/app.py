from pymongo import MongoClient
from flask import Flask,render_template,request
import mysql.connector
import hashlib
import redis


app=Flask(__name__)

#redis connection
r=redis.Redis(host='127.0.0.1',port=6379)

#mongodb connection
cluster ="mongodb://localhost:27017"
client=MongoClient(cluster)
db=client["datalake"]

#mysql connection
conn = mysql.connector.connect(
    host='localhost',
    port=3306,
    user='root',
    password='aritra1234',
    database='datalake'
)
cursor = conn.cursor()

@app.route("/",methods=['GET','POST'])
def rt():
    return render_template('index.html')

@app.route("/dashboard",methods=['POST'])
def dash():
    d=request.form
    id=d['id']
    pas=d['password']
    hashpas=hashlib.md5(pas.encode()).hexdigest()
    k=str(r.get(id))
    k=k[2:len(k)-1]
    if k==hashpas:
        query = "SELECT companyid FROM COMPANY"
        cursor.execute(query)
        rows = cursor.fetchall()
        companies=[]
        for i in rows:
            companies.append(str(i)[2:len(i)-4])
        query = "SELECT * FROM projects WHERE companyid='"+id+"'"
        cursor.execute(query)
        rows = cursor.fetchall()
        d=[]
        for i in rows:
            k=[i[0],i[3],i[2],i[1]]
            d.append(k)
        return render_template("dashboard.html",data=d)
    else:
        return render_template("index2.html",data='incorrect username or password')

@app.route("/employee",methods=['POST'])
def emp():
    pid=str(request.get_data())
    pid=pid[2:len(pid)-1]
    docs=db.employees.find({"projectid":pid})
    d=[]
    for i in docs:
        d.append([i['name'],i['dept'],i['projectid'],i['desig'],i['experience']])   
    k=[pid,d]             
    return render_template("employee.html",data=k)

@app.route("/collaborate",methods=['POST'])
def collab():
    res=request.json
    pid=res['pid']
    cid=res['cid']
    cid=cid[0:len(cid)-1]
    query = f"select companyid, companyname from company where companyid <> '{cid}'"
    print(query)
    cursor.execute(query)
    rows = cursor.fetchall()
    companies=[]
    for i in rows:
        print(i)
        j=i[1]+"(ID: "+ i[0] +")"
        companies.append(j)
        p=[pid,companies]
    return render_template("collaborate.html",data=p)

@app.route("/confirm",methods=['POST'])
def confirm():
    res=request.form
    collabid=res['collabid'].split(" ")[1]
    collabid=collabid[0:len(collabid)-1]
    origid=res['origid']
    origid=origid[0:len(origid)-1]
    projid=res['projid']
    query=f"INSERT INTO collab VALUES('{projid}','{origid}','{collabid}')"
    print(query)
    try:
        cursor.execute(query)
    except:
        query = "SELECT * FROM projects WHERE companyid='"+origid+"'"
        cursor.execute(query)
        rows = cursor.fetchall()
        d=[]
        for i in rows:
            k=[i[0],i[3],i[2],i[1],'This company is already in collaboration']
            d.append(k)
        return render_template("dashboard2.html",data=d)
    conn.commit()
    query = "SELECT * FROM projects WHERE companyid='"+origid+"'"
    cursor.execute(query)
    rows = cursor.fetchall()
    d=[]
    for i in rows:
        k=[i[0],i[3],i[2],i[1],'Company added in collaboration']
        d.append(k)
    return render_template("dashboard2.html",data=d)


@app.route("/fetchcollab",methods=['POST'])
def collabcomp():
    k=request.json
    company=k['comp']
    company=company[0:len(company)-1]
    query1 = "SELECT P.projectname,P.projectdesc,Co.projectid,Co.ownercompanyid,C.companyname,Co.collabcompanyid "
    query2 = "FROM collab AS Co, projects AS P, company AS C "
    query3 = f"WHERE Co.projectid=P.projectid AND Co.ownercompanyid=C.companyid AND Co.collabcompanyid='{company}'"
    query=query1+query2+query3
    cursor.execute(query)
    rows = cursor.fetchall()
    collab=[]
    if str(rows)=="[]":
        collab=[]
    else:
        for i in rows:
            p=[i[2],i[3],i[4],i[0],i[1]]
            collab.append(p)
    return render_template("listofcollab.html",data=collab)

@app.route("/collabemployeelist",methods=['POST'])
def colllist():
    pid=request.json['pid']
    docs=db.employees.find({"projectid":pid})
    d=[]
    for i in docs:
        d.append([i['name'],i['dept'],i['projectid'],i['desig'],i['experience'],i['companyid']])   
    k=[pid,d]
    return render_template("collabemployeelist.html",data=k)

@app.route("/addcollabemployee",methods=['POST'])
def addcollemp():
    d=request.json
    pid=d['pid']
    cid=d['cid']
    k=[cid,pid]
    return render_template("form.html",data=k)

@app.route("/addemp",methods=['POST'])
def addemp():
    d=request.form
    name=d['name']
    dept=d['dept']
    companyid=d['cid']
    companyid=companyid[0:len(companyid)-1]
    projectid=d['pid']
    designation=d['desig']
    experience=str(d['exp'])+" months"
    mydict = { "name":name, "dept": dept,"companyid":companyid,"projectid":projectid,"desig":designation,"experience":experience }
    x = db.employees.insert_one(mydict)
    print(x)
    query = "SELECT * FROM projects WHERE companyid='"+companyid+"'"
    cursor.execute(query)
    rows = cursor.fetchall()
    d=[]
    for i in rows:
        k=[i[0],i[3],i[2],i[1],'Employee successfully added']
        d.append(k)
    return render_template("dashboard2.html",data=d)

@app.route("/addempl",methods=['POST'])
def addempl():
    d=request.json
    pid=d['pid']
    cid=d['cid']
    k=[cid,pid]
    return render_template("form2.html",data=k)

@app.route("/addemployee",methods=['POST'])
def addemployee():
    d=request.form
    print(d)
    name=d['name']
    dept=d['dept']
    companyid=d['cid']
    companyid=companyid[0:len(companyid)-1]
    projectid=d['pid']
    designation=d['desig']
    experience=str(d['exp'])+" months"
    mydict = { "name":name, "dept": dept,"companyid":companyid,"projectid":projectid,"desig":designation,"experience":experience }
    x = db.employees.insert_one(mydict)
    print(x)
    query = "SELECT * FROM projects WHERE companyid='"+companyid+"'"
    cursor.execute(query)
    rows = cursor.fetchall()
    d=[]
    for i in rows:
        k=[i[0],i[3],i[2],i[1],'Employee successfully added']
        d.append(k)
    return render_template("dashboard2.html",data=d)



@app.route("/projform",methods=['POST'])
def projform():
    cid=request.json['cid']
    cid=cid[0:len(cid)-1]
    query=f"select projectid from projects WHERE companyid='{cid}'"
    cursor.execute(query)
    rows = cursor.fetchall()
    projids=[]
    for i in rows:
        projids.append(i[0])
    projid=projids[len(projids)-1]
    temp=projid[0:4]
    projid=projid[len(projid)-3:]
    for i in projid:
        if(i!=0):
            num=int(i)
    num=list(str(num+1))
    while len(num)<3:
        num=['0']+num
    for i in num:
        temp=temp+i
    id=temp
    d=[cid,id]
    return render_template("form3.html",data=d)

@app.route("/addproject",methods=['POST'])
def addproj():
    d=request.form
    pid=d['pid']    
    cid=d['cid']
    pname=d['pname']
    desc=d['desc']
    dur=d['dur']
    query=f"INSERT INTO projects (projectid, companyid, projectname, projectdesc, duration) VALUES ('{pid}','{cid}','{pname}','{desc}',{dur})"
    cursor.execute(query)
    conn.commit()
    query = "SELECT * FROM projects WHERE companyid='"+cid+"'"
    cursor.execute(query)
    rows = cursor.fetchall()
    d=[]
    for i in rows:
        k=[i[0],i[3],i[2],i[1],'Project successfully added']
        d.append(k)
    return render_template("dashboard2.html",data=d)

@app.route("/home",methods=['POST'])
def home():
    cid=request.form['cid']
    if cid[(len(cid)-1)]==" ":
        cid=cid[0:len(cid)-1]
    query = "SELECT * FROM projects WHERE companyid='"+cid+"'"
    print(query)
    cursor.execute(query)
    rows = cursor.fetchall()
    d=[]
    for i in rows:
        k=[i[0],i[3],i[2],i[1]]
        d.append(k)
    return render_template("dashboard.html",data=d)

@app.route("/logout",methods=['POST'])
def logout():
    return render_template("index.html")
app.run()                  