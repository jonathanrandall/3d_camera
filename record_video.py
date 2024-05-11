import sys
import cv2
import numpy as np
import ArducamDepthCamera as ac
import os

import subprocess
import time

print(dir(ac))

def get_auto_index(dataset_dir='./video_out/', dataset_name_prefix = '', data_suffix = 'mp4'):
    max_idx = 1000
    if not os.path.isdir(dataset_dir):
        os.makedirs(dataset_dir)
    for i in range(max_idx+1):
        if not os.path.isfile(os.path.join(dataset_dir, f'{dataset_name_prefix}stereo_{i}.{data_suffix}')):
            return i
    raise Exception(f"Error getting auto index, or more than {max_idx} episodes")

MAX_DISTANCE = 4 #2
record_vid1 = False
record_vid = False
# fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
# vid_out = cv2.VideoWriter('./video_out/mot20-01-det.mp4', fourcc, 15, (640, 240))

webcam_name = "3D USB Camera"# (usb-0000:01:00.0-1.1):"
webcam_name2 = "3D USB Camera: 3D USB Camera (usb-0000:01:00.0-1.3.4):"

def process_frame(depth_buf: np.ndarray, amplitude_buf: np.ndarray) -> np.ndarray:
        
    depth_buf = np.nan_to_num(depth_buf)

    amplitude_buf[amplitude_buf<=7] = 0
    amplitude_buf[amplitude_buf>7] = 255

    depth_buf =(1 - (depth_buf/MAX_DISTANCE)) * 255
    depth_buf = np.clip(depth_buf, 0, 255)
    result_frame = depth_buf.astype(np.uint8)  & amplitude_buf.astype(np.uint8)
    return result_frame 

class UserRect():
    def __init__(self) -> None:
        self.start_x = 0
        self.start_y = 0
        self.end_x = 0
        self.end_y = 0

selectRect = UserRect()

followRect = UserRect()

def on_mouse(event, x, y, flags, param):
    global selectRect,followRect
    
    if event == cv2.EVENT_LBUTTONDOWN:
        pass

    elif event == cv2.EVENT_LBUTTONUP:
        selectRect.start_x = x - 4 if x - 4 > 0 else 0
        selectRect.start_y = y - 4 if y - 4 > 0 else 0
        selectRect.end_x = x + 4 if x + 4 < 240 else 240
        selectRect.end_y=  y + 4 if y + 4 < 180 else 180
    else:
        followRect.start_x = x - 4 if x - 4 > 0 else 0
        followRect.start_y = y - 4 if y - 4 > 0 else 0
        followRect.end_x = x + 4 if x + 4 < 240 else 240
        followRect.end_y = y + 4 if y + 4 < 180 else 180
        
def usage(argv0):
    print("Usage: python "+argv0+" [options]")
    print("Available options are:")
    print(" -d        Choose the video to use")

def find_webcam_index(device_name):
    command = "v4l2-ctl --list-devices"
    output = subprocess.check_output(command, shell=True, text=True)
    devices = output.split('\n\n')
    
    for device in devices:
        #print(device)
        if device_name in device:
            lines = device.split('\n')
            for line in lines:
                if "video" in line:
                    parts = line.split()
                    for part in parts:
                        if part.startswith('/dev/video'):
                            print(part)
                            return (part[10:])


if __name__ == "__main__":
    record_vid=False
    record_vid1 = False
    cam = ac.ArducamCamera()
    if cam.open(ac.TOFConnect.CSI,0) != 0 :
        print("initialization failed")
    if cam.start(ac.TOFOutput.DEPTH) != 0 :
        print("Failed to start camera")
    cam.setControl(ac.TOFControl.RANG,MAX_DISTANCE)
    cv2.namedWindow("preview", cv2.WINDOW_AUTOSIZE)
    #cv2.setMouseCallback("preview",on_mouse)
    i=18
    webcam_index = int(find_webcam_index(webcam_name))
    cap_stereo = cv2.VideoCapture(webcam_index)
    cap_stereo.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap_stereo.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
    start_time = time.time()
    while True:
        frame = cam.requestFrame(200)
        if not cap_stereo.isOpened():
            print("Error: cannot open")
            break
        ret, stereo_frame = cap_stereo.read()
        
        #print("frame shape: ", frame.shape)
        #print("stereoframe shape: ", stereo_frame.shape)
        
        if frame != None and ret:
            depth_buf = frame.getDepthData()
            amplitude_buf = frame.getAmplitudeData()
            cam.releaseFrame(frame)
            amplitude_buf*=(255/1024)
            amplitude_buf = np.clip(amplitude_buf, 0, 255)
            
            cv2.imshow("stereo image", stereo_frame[50:220,65:575,:])
            #print(stereo_frame.shape)

            cv2.imshow("preview_amplitude", amplitude_buf.astype(np.uint8))
            #preview_image = amplitude_buf.copy()
            #preview_image = preview_image.astype(np.uint8)
            #print("select Rect distance:",np.mean(depth_buf[selectRect.start_y:selectRect.end_y,selectRect.start_x:selectRect.end_x]))
                       
            result_image = process_frame(depth_buf,amplitude_buf)
            if record_vid1 and ((time.time()-2)> start_time):
                record_vid = True
                record_vid1 = False
            if record_vid:
                if ((time.time()-4)> start_time):
                    tof_vid_out.release()
                    st_vid_out.release()
                    record_vid=False
                else:
                    tof_vid_out.write(result_image)
                    st_vid_out.write(stereo_frame)
            #result_image = cv2.applyColorMap(result_image, cv2.COLORMAP_JET)
            # cv2.rectangle(result_image,(selectRect.start_x,selectRect.start_y),(selectRect.end_x,selectRect.end_y),(128,128,128), 1)
            # cv2.rectangle(result_image,(followRect.start_x,followRect.start_y),(followRect.end_x,followRect.end_y),(255,255,255), 1)
            result_image = result_image.astype(np.uint8)     
            cv2.imshow("preview",result_image)
            #print(type(result_image))

            key = cv2.waitKey(1)
            if key == ord("q"):
                exit_ = True
                cam.stop()
                cam.close()
                sys.exit(0)
            if key == ord("s"):
                i=i+1
                i = get_auto_index(dataset_dir='./image_out/',data_suffix='jpg')
                fname = './image_out/tof_'+str(i) + '.jpg'
                fname2 = './image_out/stereo_'+str(i) + '.jpg'
                cv2.imwrite(fname2, stereo_frame)
                cv2.imwrite(fname, result_image)
            if key == ord("r"):
                record_vid1=True
                # i=i+1
                i = get_auto_index()
                tof_vid = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
                tof_vid_out = cv2.VideoWriter('./video_out/tof_'+str(i) + '.mp4', tof_vid, 5, (240, 180),0)
                st_vid = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
                st_vid_out = cv2.VideoWriter('./video_out/stereo_'+str(i) + '.mp4', st_vid, 5, (640, 240))
                start_time = time.time()
                # fname = '/home/jonny/images/tof_'+str(i) + '.jpg'
                # fname2 = '/home/jonny/images/stereo_'+str(i) + '.jpg'
                # cv2.imwrite(fname2, stereo_frame)
                # cv2.imwrite(fname, result_image)
                