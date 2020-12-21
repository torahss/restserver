from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

import pandas as pd

def svmRun(inputdata) :
    data = pd.read_csv('/var/www/restserver/quickstart/train.csv', header=0, index_col=0, squeeze=True)
    dataset = pd.DataFrame(data)
    t_data = pd.read_csv('/root/Downloads/test.csv', header=0, index_col=0, squeeze=True)
    t_data = pd.DataFrame(t_data)
    tr_y = dataset.iloc[:,4]
    tr_data = dataset.iloc[:, [0, 1, 2, 3]]

    test_y = t_data.iloc[:,4]
    t_data = t_data.iloc[:, [0, 1, 2, 3]]


    svm = SVC(kernel='rbf',C=1.0, random_state=1, gamma=0.1)
    svm.fit(tr_data,tr_y)
    #print(inputdata[0][1])
    y_pre_test = svm.predict(t_data)

    t_data.iloc[1:2,0] = inputdata[0][0]
    t_data.iloc[1:2, 1] = inputdata[0][1]
    t_data.iloc[1:2, 2] = inputdata[0][2]
    t_data.iloc[1:2, 3] = inputdata[0][3]
    y_pred = svm.predict(t_data.iloc[1:2, ])

    if y_pred[0] == 'Good' :
        result = 0
    elif y_pred[0] == 'Normal' :
        result = 1
    elif y_pred[0] == 'Bad':
        result = 2
    elif y_pred[0] == 'Worst':
        result =3

    print("Accuracy : %.2f" % accuracy_score(test_y, y_pre_test))

    return result
