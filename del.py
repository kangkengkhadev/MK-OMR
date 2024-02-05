import pickle
pickle_name = 'exam1'
position_path = './pickle/'
try:
    with open(position_path+pickle_name, 'rb') as f:
        posList = pickle.load(f)
        posList = posList[:-1]
        with open(position_path+pickle_name, 'wb') as f:
            pickle.dump(posList, f)
except:
    posList = []

