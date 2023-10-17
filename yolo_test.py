from ultralytics import YOLO
import cv2 as cv

# model = YOLO('blue.yaml')


# Load a model
# model = YOLO('yolov5n.pt')  # build a new model from YAML
model = YOLO('yolov8n.pt')  # load a pretrained model (recommended for training)
# model = YOLO('yolov8n.yaml').load('yolov8n.pt')  # build from YAML and transfer weights

# Train the model
model.train(data='target_object.yaml', epochs=200, imgsz=640, device=0, workers=0)

# model = YOLO('runs/detect/train8/weights/best.pt')
# model.export(format='engine', device=0)

# model.train(resume=True)

# def set_camera_properties(capture):
#     capture.set(cv.CAP_PROP_FRAME_WIDTH, 960)
#     capture.set(cv.CAP_PROP_FRAME_HEIGHT, 540)
#     capture.set(cv.CAP_PROP_FPS, 30)
    # capture.set(cv.CAP_PROP_BRIGHTNESS, 1)
    # capture.set(cv.CAP_PROP_CONTRAST,40)
    # capture.set(cv.CAP_PROP_SATURATION, 50)


# capture.set(cv.CAP_PROP_HUE, 50)
# capture.set(cv.CAP_PROP_EXPOSURE, 50)

# cap = cv.VideoCapture(0)
# set_camera_properties(cap)
#

# def get_center(coordinate):
#     return [int((coordinate[0] + coordinate[2]) / 2), int((coordinate[1] + coordinate[3]) / 2)]

#
# while True:
#     ret, frame = cap.read()
#
#     result = model.predict(frame, show=False)
#
#     name_dict = result[0].names
#     classes = result[0].boxes.cls.cpu().numpy()
#     coordinates = result[0].boxes.xyxy.cpu().numpy()
#     for i in range(len(classes)):
#         object_coordinate = coordinates[i]
#         center = get_center(object_coordinate)
#         text = 'x ' + str(center[0]) + '\ny ' + str(center[1])
#         if classes[i] > 2:
#             cv.putText(frame, text, [center[0] + 2, center[1] - 2], cv.FONT_HERSHEY_PLAIN, 0.75, (255, 255, 255), 2)
#         if classes[i] == 3:
#             cv.circle(frame, center, 2, (0, 255, 0), -1)
#         elif classes[i] == 4:
#             cv.circle(frame, center, 2, (0, 0, 255), -1)
#         elif classes[i] == 5:
#             cv.circle(frame, center, 2, (255, 0, 0), -1)
#
#     print("name dict: ", name_dict)
#     print("classes: ", classes)
#     print("coordinates: ", coordinates)
#
#     cv.imshow('camera', frame)
#     # cv.imshow('contour', frame_contour)
#     if cv.waitKey(1) == 27:
#         cv.destroyAllWindows()
#         break
