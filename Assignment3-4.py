import numpy as np
import cv2 as cv

# The given video and calibration data
input_file = 'C:/Users/pyeonmu/Desktop/Pyeon-directors-vlog/data/chessboard.mp4'
K = np.array([[958.94884136, 0, 572.25745102],
              [0, 958.51653746, 901.36955821],
              [0, 0, 1]])
dist_coeff = np.array([0.02098796, 0.00614936, -0.0009255, 0.00326809, -0.09228366])
board_pattern = (10, 7)
board_cellsize = 0.025
board_criteria = cv.CALIB_CB_ADAPTIVE_THRESH + cv.CALIB_CB_NORMALIZE_IMAGE + cv.CALIB_CB_FAST_CHECK

# Open a video
video = cv.VideoCapture(input_file)
assert video.isOpened(), 'Cannot read the given input, ' + input_file

# Prepare a 3D box for simple AR
box_lower = board_cellsize * np.array([[7, 1,  -1], [4, 1,  -1], [4, 2,  -1], [5, 2,  -1], [5, 6,  -1], [6, 6,  -1], [7, 5,  -1], [7, 4,  -1], [6, 5,  -1], [6, 2,  -1], [7, 2,  -1], [7, 1,  -1]])
box_upper = board_cellsize * np.array([[7, 1, -3], [4, 1, -3], [4, 2, -3], [5, 2, -3], [5, 6, -3], [6, 6, -3], [7, 5, -3], [7, 4, -3], [6, 5, -3], [6, 2, -3], [7, 2, -3], [7, 1, -3]])

# Prepare 3D points on a chessboard
obj_points = board_cellsize * np.array([[c, r, 0] for r in range(board_pattern[1]) for c in range(board_pattern[0])])

# Run pose estimation
while True:
    # Read an image from the video
    valid, img = video.read()
    if not valid:
        break

    # Estimate the camera pose
    complete, img_points = cv.findChessboardCorners(img, board_pattern, board_criteria)
    if complete:
        ret, rvec, tvec = cv.solvePnP(obj_points, img_points, K, dist_coeff)

        # Draw the box on the image
        line_lower, _ = cv.projectPoints(box_lower, rvec, tvec, K, dist_coeff)
        line_upper, _ = cv.projectPoints(box_upper, rvec, tvec, K, dist_coeff)
        cv.polylines(img, [np.int32(line_lower)], True, (255, 0, 255), 2) # Draw the magenta box
        cv.polylines(img, [np.int32(line_upper)], True, (255, 255, 0), 2) # Draw the aqua box
        for b, t in zip(line_lower, line_upper):
            cv.line(img, np.int32(b.flatten()), np.int32(t.flatten()), (0, 255, 0), 2)

        # Print the camera position
        R, _ = cv.Rodrigues(rvec) # Alternative) scipy.spatial.transform.Rotation
        p = (-R.T @ tvec).flatten()
        info = f'XYZ: [{p[0]:.3f} {p[1]:.3f} {p[2]:.3f}]'
        cv.putText(img, info, (10, 25), cv.FONT_HERSHEY_DUPLEX, 0.6, (0, 255, 0))

    # Show the image and process the key event
    cv.imshow('Pose Estimation (Chessboard)', img)
    key = cv.waitKey(10)
    if key == ord(' '):
        key = cv.waitKey()
    if key == 27: # ESC
        break

video.release()
cv.destroyAllWindows()