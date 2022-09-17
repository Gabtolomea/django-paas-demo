# from .models import *

# mycursor = mydb.cursor()
# def porter_in(request):
#     col = 0
#     for t in range(len(tablenames)):
#         mycursor.execute("SELECT count(*) FROM information_schema.columns WHERE TABLE_NAME = '"+tablenames[t]+"';")
#         for c in range(mycursor.fetchone()[0]):
#             mycursor.execute("SELECT " + columnnames[col] + " FROM "+tablenames[t]+";")
#             result=mycursor.fetchall()
#             for x in result:
#                 alltables[t][c].append(x[0])
#             col+=1
    
#     current_table = rearrange('systemuser')#change string parameter to desired table name reference in tablenames above
#     porter_out(current_table)
#     return render(request, "home.html")

# def rearrange(var):
#     arr = []
#     mycursor.execute("SELECT count(*) FROM information_schema.columns WHERE TABLE_NAME = '"+var+"';")
#     cols = mycursor.fetchone()[0]
#     mycursor.execute("SELECT count(*) FROM "+var+";")
#     rows = mycursor.fetchone()[0]
#     for r in range(rows):
#         inner = []
#         for c in range(cols):
#             inner.append(globals()[var][c][r])
#         arr.append(inner)

#     return arr

    
# def porter_out(table):
#     sys_user = SystemUsers()
#     for i in table:
#         sys_user.userid = i[0]
#         sys_user.password = i[1]
#         sys_user.su_firstname = i[2]
#         sys_user.su_middlename = i[3]
#         sys_user.su_mobilenumber = i[4]
#         sys_user.su_lastname = i[5]
#         sys_user.su_emailaddress = i[6]
#         sys_user.usertype = i[7]
#         sys_user.su_profilepic = i[8]
#         sys_user.approver_flag = i[9]
#         sys_user.save()


#-----------------------------------------------#


# mycursor = mydb.cursor()
# def porter_in(request):
#     col = 0
#     for t in range(len(tablenames)):
#         mycursor.execute("SELECT count(*) FROM information_schema.columns WHERE TABLE_NAME = '"+tablenames[t]+"';")
#         for c in range(mycursor.fetchone()[0]):
#             mycursor.execute("SELECT " + columnnames[col] + " FROM "+tablenames[t]+";")
#             result=mycursor.fetchall()
#             for x in result:
#                 alltables[t][c].append(x[0])
#             col+=1
    
#     current_table = rearrange('ratestable')#change string parameter to desired table name reference in tablenames above
#     porter_out(current_table)
#     return render(request, "home.html")

# def rearrange(var):
#     arr = []
#     mycursor.execute("SELECT count(*) FROM information_schema.columns WHERE TABLE_NAME = '"+var+"';")
#     cols = mycursor.fetchone()[0]
#     mycursor.execute("SELECT count(*) FROM "+var+";")
#     rows = mycursor.fetchone()[0]
#     for r in range(rows):
#         inner = []
#         for c in range(cols):
#             inner.append(globals()[var][c][r])
#         arr.append(inner)

#     return arr

    
# def porter_out(table):
#     rt = RatesTable()
#     for i in table:
#         rt.minReading = i[0]
#         rt.minReadingCharge = i[1]
#         rt.rateAfterMin = i[2]
#         rt.ratePenalty = i[3]
#         rt.ratePenaltyFreq = i[4]





