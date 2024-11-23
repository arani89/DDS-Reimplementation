import os

video_name = 'MVI_40991' #don't add extension
min_conf = '0.1'
max_conf = '0.25'
print(video_name)

def generate_first_pass_video():
  print(video_name)
  os.system('ffmpeg -y -i input/' + video_name +'.mp4 -pix_fmt yuv420p media/raw_files/' + video_name +'.y4m')

#change qp to 36 and resolution to 0.6
  os.system('ffmpeg -y -i media/raw_files/' + video_name +'.y4m -c:v libx264 -qp 36 -r 30 -vf scale=iw*0.6:ih*0.6 media/first_pass_input/' + video_name + '.mp4')
  os.system('python3 yolov5/detect.py --weights yolov5s.pt --conf ' + min_conf + '--source media/first_pass_input/' + video_name + '.mp4 --save-txt --save-conf --project results --name ' + video_name +'_first')

generate_first_pass_video()


# # DDS Second Pass

# Find objects with confidence values between `min_conf` and `max_conf` from the results produced in first pass and store them in `results/{video_name}_first}/required_objects.txt`.

# In[7]:

def find_relevant_objects_second_pass():
  labels_path = 'results/'+video_name+'_first4/labels'
  files = os.listdir(labels_path)
  print(files)
  # print('Number of labels in the video: ',len(files))

  start = len(video_name)+1
  print(start)

def get_numeric_part(filename):
  #extract the numeric part from the filename, format is '{video_name}_num.txt'
  #num represents frame number
  return int(filename[start:-4])

#sort to process frames faster in next steps
def process_frames():
  files.sort(key=get_numeric_part)

  #path to store required_objects.txt
  req_obj_path = 'results/'+video_name+'_first4/required_objects.txt'
  # print(req_obj_path)

  with open(req_obj_path, 'w') as req_obj_file:
    for label_name in files:
      # print(label_name)
      # print(labels_path)
      input_file_path = labels_path+'/'+label_name
      with open(input_file_path, 'r') as input_file:
        for line in input_file:
          entry = line.split()
          if float(entry[-1])>=float(min_conf) and float(entry[-1])<=float(max_conf):
            req_obj_file.write(label_name[start:-4]+' '+line)




  os.system('mkdir -p media/raw_frames/{video_name}')
  os.system('mkdir -p media/frame_crops/{video_name}')
  os.system('mkdir -p media/processed_frames/{video_name}')
  os.system('mkdir -p media/final_path/{video_name}')

  os.system('ffmpeg -i media/raw_files/{video_name}.y4m -r 30 media/raw_frames/{video_name}/%d.png')



  from PIL import Image
  import subprocess

  def normalized_to_absolute(x, y, w, h, img_width, img_height):
    #returns coordinates to crop the object
    left = int(x * img_width)
    top = int(y * img_height)
    right = int((x + w) * img_width)
    bottom = int((y + h) * img_height)
    return (left, top, right, bottom)

  def create_black_background(width, height, save_path):
    #creates a black background to paste the crops of objects (if any)
    subprocess.run([
      'ffmpeg', '-f', 'lavfi', f'-i', f'color=c=black:s={width}x{height}', '-frames:v', '1', save_path
    ])

  def crop_image(image_path, coordinates, cropped_image_path):
    #open the original image
    image = Image.open(image_path)
    img_width, img_height = image.size
    #convert normalized coordinates to absolute pixel coordinates
    abs_coords = normalized_to_absolute(*coordinates, img_width, img_height)
    #crop the image
    cropped_image = image.crop(abs_coords)
    print("-------------------------------")
    print(cropped_image)
    #save the cropped image
    cropped_image.save(cropped_image_path)
    #return the top-left coordinates of the cropped image
    return (abs_coords[0], abs_coords[1])

  def overlay_cropped_on_black(original_image_path, cropped_image_path, output_image_path, coordinates):
    #crop the image and get the top-left coordinates of the cropped area
    top_left = crop_image(original_image_path, coordinates, cropped_image_path)
    #overlay the cropped portion
    subprocess.run([
        'ffmpeg', '-y', output_image_path, '-i', cropped_image_path, '-filter_complex', f'overlay={top_left[0]}:{top_left[1]}', 'temp.png'
    ])
    subprocess.run(['mv', 'temp.png', output_image_path])


  req_obj_path = 'results/'+video_name+'_first4/required_objects.txt'
  print("--------")
  print(req_obj_path)
  raw_frames_path = f'media/raw_frames/{video_name}'
  frame_crops_path = f'media/frame_crops/{video_name}'
  processed_frames_path = f'media/processed_frames/{video_name}'
  final_path = f'media/final_frames/{video_name}'

  with Image.open('media/raw_frames'+f'/{video_name}/1.png') as img:
    frame_width, frame_height = img.size
  # print(width, height)

  frame_num, crop_cnt = 1, 1
  with open(req_obj_path, 'r') as req_obj_file:
    for line in req_obj_file:
      temp_entry = line.split()
      entry = [float(x) for x in temp_entry]

      # adding black frames for frames which don't have any required object
      while(int(entry[0])>=frame_num):
        create_black_background(frame_width, frame_height, f'{processed_frames_path}/{frame_num}.png')
        frame_num += 1

      #processing required frame now
      #frame_num -= 1
      coordinates = entry[2:-1]
      coordinates[0] -= coordinates[2]/2
      coordinates[1] -= coordinates[3]/2
      overlay_cropped_on_black(f'{raw_frames_path}/{frame_num}.png',
        f'{frame_crops_path}/{crop_cnt}.png', f'{final_path}/{frame_num}.png', coordinates)
      crop_cnt += 1
      frame_num += 1



  os.system('ffmpeg -framerate 30 -i media/processed_frames/{video_name}/%d.png -c:v libx264 -qp 30 -vf "scale=iw*0.8:ih*0.8" -pix_fmt yuv420p media/second_pass_input/{video_name}.mp4')
  os.system('python3 yolov5/detect.py --weights yolov5s.pt --conf {min_conf} --source media/second_pass_input/{video_name}.mp4 --save-txt --save-conf --project results --name {video_name}_second')


  #clear all videos and images generated to produce results
  os.system('rm -rf media/raw_files/{video_name}.y4m')
  os.system('rm -rf media/first_pass_input/{video_name}.mp4')
  os.system('rm -rf media/raw_frames/{video_name}')
  os.system('rm -rf media/frame_crops/{video_name}')
  os.system('rm -rf media/processed_frames/{video_name}')
  os.system('rm -rf media/second_pass_input/{video_name}.mp4')

