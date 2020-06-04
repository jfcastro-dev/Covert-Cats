from sklearn import tree
import pandas as pd
import sys
import unittest
import csv
from sklearn.model_selection import train_test_split
import pydotplus
from IPython.display import Image
'''
For more advanced models, lookup hitter ID
and their respective tendencies
and location.
'''

try:
    f=open(sys.argv[1])
    reader = csv.DictReader(f,delimiter=',')
    team=input("Name the Pitcher's Team Acronym (NYM,ATL,etc)")
except:
    print("File Not Existent")
    sys.exit(1)

try:
    writecsv=open("output.csv",'w')
    writecsv.write("Count,Ahead,Close,AfterFifth,Righty,Pitch\n")
   
   '''
    Format Data for Actual Predictions
    '''
    for i in reader:
        if(team==i['home_team']):
            home=True
        elif(team==i['away_team']):
            home=False
        else:
            print("Incorrect Team Acronym.")
            f.close()
            writecsv.close()
            sys.exit(1)
        count=str(i['balls'])+"-"+str(i['strikes'])
        x=int(i['home_score'])
        y=int(i['away_score'])
        if(home):
            ahead=x-y>0
        else:
            ahead=x-y<0
        close=abs(x-y)<3
        AfterFifth=int(i['inning'])>5
        Righty='R'==i['stand']
        pitchtype=i['pitch_name']
        heat= ((pitchtype=='4-Seam Fastball') or (pitchtype=='Sinker') or (pitchtype=='2-Seam Fastball'))
        if(pitchtype!='Intentional Ball'):
            writecsv.write(count+","+str(ahead)+","+ str(close)+","+str(AfterFifth)+","+str(Righty)+","+str(heat)+"\n")
    writecsv.close()
    #CSV Written Out for Debugging
   
    df=pd.read_csv("output.csv")
    data=pd.get_dummies(df[['Count','Ahead','Close','AfterFifth','Righty']])

    print(data)
    x_train, x_test, y_train, y_test = train_test_split(data, df['Pitch'],test_size=0.2)
    classifier=tree.DecisionTreeClassifier()
    classtrain=classifier.fit(x_train,y_train)
    y_pred = classtrain.predict(x_test)

    df2=pd.DataFrame({'Actual':y_test, 'Predicted':y_pred})
    print(df2)
    df2.to_csv(r'df2.csv',index=None,header=True) 
    g=open('df2.csv')
    r = csv.DictReader(g,delimiter=',')
    correct=0
    total=0
    for row in r:
        if row['Actual']==row['Predicted']:
            correct+=1
        total+=1
    g.close()
    print("Correct: " + str(correct) + " Total: " + str(total) +" Num: " +str(float(correct/total*100.0)) + "%")

except:
    print("Incorrect File Format")
    f.close()
    sys.exit(1)
