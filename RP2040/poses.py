# Static servo positions used by Will's state functions.
# Values are copied from the board-fixed Will version without tuning.

pose_calibrate = { # Each dictionary key = servo name, value = angle
    "YAW": 90,
    "ROL": 90,
    "PIT": 80,
    "MOU": 170,
    "LID": 110,
    "EYL": 90,
    "EYR": 90,
    "EAL": 90,
    "EAR": 90,
}
pose_sleep = { # Each dictionary key = servo name, value = angle
    "YAW": 88,
    "RWH": 89,
    "ROL": 90,
    "PIT": 80,
    "MOU": 170,
    "LID": 30,
    "EYL": 90,
    "EYR": 90,
    "EAL": 150,
    "EAR": 30,
}

pose_base = { # Each dictionary key = servo name, value = angle
    "YAW": 88,
    "RWH": 89,
    "ROL": 90,
    "PIT": 20,
    "MOU": 170,
    "LID": 130,
    "EYL": 90,
    "EYR": 90,
    "EAL": 130,
    "EAR": 70,
}

pose_speaking = { # Each dictionary key = servo name, value = angle
    "YAW": 88,
    "RWH": 89,
    "ROL": 90,
    "PIT": 20,
    "MOU": 10,
    "LID": 130,
    "EYL": 90,
    "EYR": 90,
    "EAL": 130,
    "EAR": 70,
}

pose_stop_speaking = { # Each dictionary key = servo name, value = angle
    "YAW": 88,
    "RWH": 89,
    "ROL": 90,
    "PIT": 20,
    "MOU": 150,
    "LID": 130,
    "EYL": 90,
    "EYR": 90,
    "EAL": 130,
    "EAR": 70,
}

pose_thinking_1 = { # Each dictionary key = servo name, value = angle
    "YAW": 90,
    "RWH": 90,
    "ROL": 130,
    "PIT": 50,
    "MOU": 150,
    "LID": 70,
    "EYL": 90,
    "EYR": 90,
    "EAL": 150,
    "EAR": 120,
}

pose_curious_2 = { # Each dictionary key = servo name, value = angle
    "YAW": 90,
    "RWH": 90,
    "ROL": 40,
    "PIT": 10,
    "MOU": 160,
    "LID": 130,
    "EYL": 90,
    "EYR": 90,
    "EAL": 60,
    "EAR": 60,
}

pose_map={
    "pose_calibrate": pose_calibrate,
    "pose_base": pose_base,
    "pose_thinking_1": pose_thinking_1,
    "pose_curious_2": pose_curious_2,
    "pose_sleep": pose_sleep,
    "pose_speaking": pose_speaking,
    "pose_stop_speaking": pose_stop_speaking,
}

#_________________#  #_________________#
