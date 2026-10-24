from app.safety import check_pair, find_conflicts, haversine_m

def test_haversine_same_point_is_zero():
    assert haversine_m(11.0, 76.0, 11.0, 76.0) == 0

def test_close_same_altitude_conflict():
    a = {"id":"A","lat":11.0,"lon":76.0,"altitude_m":100,"status":"enroute"}
    b = {"id":"B","lat":11.0001,"lon":76.0001,"altitude_m":110,"status":"enroute"}
    assert check_pair(a,b)["conflict"] is True
    assert len(find_conflicts([a,b])) == 1

def test_vertical_separation_suppresses_demo_alert():
    a = {"id":"A","lat":11.0,"lon":76.0,"altitude_m":100,"status":"enroute"}
    b = {"id":"B","lat":11.0001,"lon":76.0001,"altitude_m":200,"status":"enroute"}
    assert check_pair(a,b)["conflict"] is False
