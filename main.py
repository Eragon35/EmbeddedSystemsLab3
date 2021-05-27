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
    h_sensitivity = 20
    high = 255
    low = 50
    width, height, channels = frame.shape
    # Choose rectangle's points by rect_number
    if rect_number == 1:
        start_point = (int(height / 6 - rect_size / 2), int(width / 6 - rect_size / 2))
        end_point = (int(height / 6 + rect_size / 2), int(width / 6 + rect_size / 2))
    elif rect_number == 2:
        start_point = (int(height / 2 - rect_size / 2), int(width / 2 - rect_size / 2))
        end_point = (int(height / 2 + rect_size / 2), int(width / 2 + rect_size / 2))
    else:
        start_point = (int(height / 6 * 5 - rect_size / 2), int(width / 6 * 5 - rect_size / 2))
        end_point = (int(height / 6 * 5 + rect_size / 2), int(width / 6 * 5 + rect_size / 2))

    # Drawing rect
    color = (150, 150, 150)
    thickness = 2
    rect = cv2.rectangle(frame, start_point, end_point, color, thickness)

    # Initializing array of colors' borders
    list_of_masks = [
        (np.array([175 + h_sensitivity, high, high]), np.array([175 - h_sensitivity, low, low]), "red"),
        (np.array([20 + h_sensitivity, high, high]), np.array([20 - h_sensitivity, low, low]), "orange"),
        (np.array([30 + h_sensitivity, high, high]), np.array([30 - h_sensitivity, low, low]), "yellow"),
        (np.array([90 + h_sensitivity, high, high]), np.array([90 - h_sensitivity, low, low]), "cyan"),
        (np.array([60 + h_sensitivity, high, high]), np.array([60 - h_sensitivity, low, low]), "green"),
        (np.array([120 + h_sensitivity, high, high]), np.array([120 - h_sensitivity, low, low]), "blue"),
        (np.array([155 + h_sensitivity, high, high]), np.array([155 - h_sensitivity, low, low]), "violet")
    ]
    global_rate = 0.0
    inside_text = 'not rainbow color'

    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask_frame = hsv_frame[start_point[1]:end_point[1] + 1, start_point[0]:end_point[0] + 1]

    # Finding the most similar color
    for borders in list_of_masks:
        mask = cv2.inRange(mask_frame, borders[1], borders[0])
        rate = np.count_nonzero(mask) / (rect_size * rect_size)
        if rate > 0.9:
            inside_text = borders[2]
            global_rate = rate

    # Tune & draw text
    org = (end_point[0] - 100, end_point[1] + 20)
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.7
    cv2.putText(rect, inside_text, org, font, font_scale, color, thickness, cv2.LINE_AA)
    av_hue = np.average(mask_frame[:, :, 0])
    av_sat = np.average(mask_frame[:, :, 1])
    av_val = np.average(mask_frame[:, :, 2])
    cv2.putText(rect, str([int(av_hue), int(av_sat), int(av_val)]) + " " + str(global_rate) + " chosen rectangle #" +
                str(rect_number), (10, 50), font, font_scale, color, thickness, cv2.LINE_AA)
    return frame


print('Press 1..3 to choose rectangle')
print('Press 4 to Quit the Application\n')

# Open Default Camera
rectangle_number = 1
cap = cv2.VideoCapture(0)  # gstreamer_pipeline(flip_method=4), cv2.CAP_GSTREAMER)

while cap.isOpened():
    # Take each Frame
    ret, frame_for_render = cap.read()

    # Flip Video vertically (180 Degrees)
    frame_for_render = cv2.flip(frame_for_render, 180)

    # do all magic here
    process(frame_for_render, rectangle_number)

    # Show video
    cv2.imshow('Cam', frame_for_render)

    # Exit if "4" is pressed
    k = cv2.waitKey(1) & 0xFF
    if k == 52:  # ord 4
        # Quit
        print('Good Bye!')
        break
    # Choosing number of rectangle
    elif k == 51:
        rectangle_number = 3
    elif k == 50:
        rectangle_number = 2
    elif k == 49:
        rectangle_number = 1

# Release the Cap and Video
cap.release()
cv2.destroyAllWindows()
