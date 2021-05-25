import numpy as np
import cv2


def gstreamer_pipeline(
        capture_width=1280,
        capture_height=720,
        display_width=1280,
        display_height=720,
        framerate=30,
        flip_method=0,
):
    return (
            "nvarguscamerasrc ! "
            "video/x-raw(memory:NVMM), "
            "width=(int)%d, height=(int)%d, "
            "format=(string)NV12, framerate=(fraction)%d/1 ! "
            "nvvidconv flip-method=%d ! "
            "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
            "videoconvert ! "
            "video/x-raw, format=(string)BGR ! appsink max-buffers=1 drop=true"
            % (
                capture_width,
                capture_height,
                framerate,
                flip_method,
                display_width,
                display_height,
            )
    )


def process(frame, rect_number):
    rect_size = 100
    h_sensivity = 20
    s_h = 255
    v_h = 255
    s_l = 50
    v_l = 50
    width, height, channels = frame.shape
    # choose points by rect_number
    if rect_number == 1:
        start_point = (int(height / 6 - rect_size / 2), int(width / 6 - rect_size / 2))
        end_point = (int(height / 6 + rect_size / 2), int(width / 6 + rect_size / 2))
    if rect_number == 2:
        start_point = (int(height / 2 - rect_size / 2), int(width / 2 - rect_size / 2))
        end_point = (int(height / 2 + rect_size / 2), int(width / 2 + rect_size / 2))
    if rect_number == 3:
        start_point = (int(height / 6 * 5 - rect_size / 2), int(width / 6 * 5 - rect_size / 2))
        end_point = (int(height / 6 * 5 + rect_size / 2), int(width / 6 * 5 + rect_size / 2))
    color = (255, 0, 222)
    thickness = 2
    rect = cv2.rectangle(frame, start_point, end_point, color, thickness)

    # hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # mask_frame = hsv_frame[start_point[1]:end_point[1] + 1, start_point[0]:end_point[0] + 1]

    list_of_masks = [
        (np.array([0 + h_sensivity, s_h, v_h]), np.array([0 - h_sensivity, s_l, v_l]), "red"),
        (np.array([20 + h_sensivity, s_h, v_h]), np.array([20 - h_sensivity, s_l, v_l]), "orange"),
        (np.array([30 + h_sensivity, s_h, v_h]), np.array([30 - h_sensivity, s_l, v_l]), "yellow"),
        (np.array([60 + h_sensivity, s_h, v_h]), np.array([60 - h_sensivity, s_l, v_l]), "green"),
        (np.array([90 + h_sensivity, s_h, v_h]), np.array([90 - h_sensivity, s_l, v_l]), "cyan"),
        (np.array([120 + h_sensivity, s_h, v_h]), np.array([120 - h_sensivity, s_l, v_l]), "blue"),
        (np.array([155 + h_sensivity, s_h, v_h]), np.array([155 - h_sensivity, s_l, v_l]), "purple")
    ]

    global_rate = 0.0
    # green_upper = np.array([30 + h_sensivity, s_h, v_h])
    # green_lower = np.array([30 - h_sensivity, s_l, v_l])
    # mask_green = cv2.inRange(mask_frame, green_lower, green_upper)
    # global_rate = np.count_nonzero(mask_green) / (rect_size * rect_size)

    inside_text = 'not rainbow color'
    # if global_rate > 0.9:
    #     inside_text = 'purple'

    for borders in list_of_masks:
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask_frame = hsv_frame[start_point[1]:end_point[1] + 1, start_point[0]:end_point[0] + 1]
        mask = cv2.inRange(mask_frame, borders[1], borders[0])
        rate = np.count_nonzero(mask) / (rect_size * rect_size)
        # print(borders[2] + " rate = " + str(rate))
        if rate > 0.9:
            print(borders)
            inside_text = borders[2]
            global_rate = rate

    org = (end_point[0] - 100, end_point[1] + 20)
    font = cv2.FONT_HERSHEY_SIMPLEX
    fontScale = 0.7
    text = cv2.putText(rect, inside_text, org, font, fontScale, color, thickness, cv2.LINE_AA)
    av_hue = np.average(mask_frame[:, :, 0])
    av_sat = np.average(mask_frame[:, :, 1])
    av_val = np.average(mask_frame[:, :, 2])
    average = [int(av_hue), int(av_sat), int(av_val)]

    text = cv2.putText(rect, str(average) + " " + str(global_rate) + " chosen rectangle #" + str(rect_number), (10, 50), font, fontScale, color, thickness,
                       cv2.LINE_AA)
    frame = text
    return frame


print('Press 1..3 to choose rectangle')
print('Press 4 to Quit the Application\n')

# Open Default Camera
rect_number = 1
cap = cv2.VideoCapture(0)  # gstreamer_pipeline(flip_method=4), cv2.CAP_GSTREAMER)

while (cap.isOpened()):
    # Take each Frame
    ret, frame = cap.read()

    # Flip Video vertically (180 Degrees)
    frame = cv2.flip(frame, 180)

    invert = process(frame, rect_number)

    # Show video
    cv2.imshow('Cam', frame)

    # Exit if "4" is pressed
    k = cv2.waitKey(1) & 0xFF
    if k == 52:  # ord 4
        # Quit
        print('Good Bye!')
        break
    if k == 51:
        rect_number = 3
    if k == 50:
        rect_number = 2
    if k == 49:
        rect_number = 1

# Release the Cap and Video
cap.release()
cv2.destroyAllWindows()
