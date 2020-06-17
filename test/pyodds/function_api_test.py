import pytest
import numpy as np
import time

from pyodds.utils.utilities import output_performance,insert_demo_data,connect_server,query_data
from pyodds.utils.importAlgorithm import algorithm_selection

# @pytest.fixture(scope='module')
def test_static_api():
    host = '127.0.0.1'
    user = 'user'
    password = '0906'
    algorithm = ['iforest','ocsvm','lof','robustcovariance','cblof','knn','hbos','sod','pca','dagmm','autoencoder','lstm_ad','lstm_ed','staticautoencoder']
    rng = np.random.RandomState(42)
    np.random.seed(42)
    conn,cursor=connect_server(host, user, password)
    ground_truth_whole = insert_demo_data(conn, cursor, 'db', 't', ground_truth_flag=True)
    data, ground_truth = query_data(conn, cursor, 'db', 't',time_serie_name='ts', ground_truth=ground_truth_whole,start_time='2019-07-20 00:00:00',end_time='2019-08-20 00:00:00',time_serie=False, ground_truth_flag=True)

    for alg in algorithm:
        clf = algorithm_selection(alg, random_state=rng, contamination=0.1)
        print('Start processing:')
        start_time = time.clock()
        clf.fit(data)
        prediction_result = clf.predict(data)
        outlierness = clf.decision_function(data)
        output_performance(alg, ground_truth, prediction_result, time.clock() - start_time, outlierness)
    data, ground_truth = query_data(conn, cursor, 'db', 't',time_serie_name='ts', ground_truth=ground_truth_whole,start_time=None,end_time=None,time_serie=False, ground_truth_flag=True)
    data, ground_truth = query_data(conn, cursor, 'db', 't',time_serie_name='ts', ground_truth=ground_truth_whole,start_time=None,end_time=None,time_serie=False, ground_truth_flag=False)

    conn.close()

def test_timestamp_api():
    host = '127.0.0.1'
    user = 'user'
    password = '0906'
    algorithm = ['luminol']
    rng = np.random.RandomState(42)
    np.random.seed(42)
    conn,cursor=connect_server(host, user, password)
    ground_truth_whole = insert_demo_data(conn, cursor, 'db', 't', ground_truth_flag=True)
    data, ground_truth = query_data(conn, cursor, 'db', 't',time_serie_name='ts', ground_truth=ground_truth_whole,start_time='2019-07-20 00:00:00',end_time='2019-08-20 00:00:00',time_serie=True, ground_truth_flag=True)
    for alg in algorithm:
        clf = algorithm_selection(alg, random_state=rng, contamination=0.1)
        print('Start processing:')
        start_time = time.clock()
        clf.fit(data)
        prediction_result = clf.predict(data)
        outlierness = clf.decision_function(data)
        output_performance(alg, ground_truth, prediction_result, time.clock() - start_time, outlierness)
    conn.close()


if __name__ == "__main__":
    test_static_api()
    test_timestamp_api()
    print("Everything passed")
