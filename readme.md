# Visitor Analytics Using Azure Face API

Limited vesrion for Azure face API is available for Free [here](https://azure.microsoft.com/en-in/services/cognitive-services/face/) and can be used for testing the scripts like this or building your own solutions by forking and modifying the script.

# Sample
Sample input video and outputs are included in this repository.
[![Sample Input](http://img.youtube.com/vi/nX_inqaAzOI/0.jpg)](https://www.youtube.com/watch?v=nX_inqaAzOI&feature=youtu.be&hd=1 "RMI Fibonacci Java")

Here are all the unique persons that are recognized in the video.
|<img src="https://raw.githubusercontent.com/mayank1513/visitor-analytics-with-azure-face/master/visitor_images/visitor1.jpg">|<img src="https://raw.githubusercontent.com/mayank1513/visitor-analytics-with-azure-face/master/visitor_images/visitor2.jpg"|
## How to use
1. Clone git repo or download and extract zip 
2. open in VS code or any other python sde and edit subscription key and endpoint on line 16 and 19 respectively.
3. type 
    python retail_genome.py -v sample.mp4

- if you don't pass any argument it will start default webcam

4. Other arguments (optional)
- n -> detect only every nth frame (int) [default 1]
- nskip -> skip first nskip frames if we know there are no detactable people in them (int) [default 0]
- o -> output filename (str) [default inputfilename_speed.avi] only avi output supported
- s -> output speed (defaut is 1x, you can put any float value 1.5 to make 1.5x or 0.8 for 0.8x) (float)
- example  
    python retail_genome.py -v Retail_genome.mp4 -n 2 -nskip 160 -o my -s 0.8

5. press 'q' to terminate
6. At the end all detcted faces are enlarged analyzed and grouped to find unique persons. The results are stored in 'visitor_images' folder

# API used
- Azure face API
- Azure has enough free quota - costing can be optimized by running detaction for say every 5th frame

# How to contribute
Fork into your own repository by clicking on a fork button on top right.

